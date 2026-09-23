"""Root conftest: CLI options, driver lifecycle, parallel device mapping, failure diagnostics."""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path

import allure
import pytest
from selenium.common.exceptions import WebDriverException

from config.settings import Settings, get_settings
from core.driver_factory import create_driver

logger = logging.getLogger("framework")


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--platform", default="android", choices=["android", "ios"],
                     help="Target mobile platform")
    parser.addoption("--env", default="staging", choices=["staging", "prod"],
                     help="Target backend environment")


def pytest_configure(config: pytest.Config) -> None:
    """RERUNS env var sets the flaky-retry default; an explicit --reruns wins."""
    if getattr(config.option, "reruns", None) in (None, 0) and (reruns := os.getenv("RERUNS")):
        config.option.reruns = int(reruns)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Enforce platform markers: @android_only scenarios never run on iOS and vice versa."""
    platform = config.getoption("--platform")
    for item in items:
        for marker in ("android_only", "ios_only"):
            if marker in item.keywords and platform != marker.removesuffix("_only"):
                item.add_marker(pytest.mark.skip(
                    reason=f"{marker} scenario, current platform is {platform}"))


@pytest.fixture(scope="session")
def settings(request: pytest.FixtureRequest, worker_id: str) -> Settings:
    """Session settings; under xdist each worker can target its own device/server.

    Parallel run example (2 devices):
        DEVICE_NAME_GW0=emulator-5554 APPIUM_SERVER_URL_GW0=http://127.0.0.1:4723 \\
        DEVICE_NAME_GW1=emulator-5556 APPIUM_SERVER_URL_GW1=http://127.0.0.1:4725 \\
        uv run pytest -n 2
    """
    base = get_settings(
        platform=request.config.getoption("--platform"),
        env=request.config.getoption("--env"),
    )
    if worker_id == "master":  # not running under xdist
        return base

    suffix = worker_id.upper()
    caps = dict(base.capabilities)
    if device := os.getenv(f"DEVICE_NAME_{suffix}"):
        caps["appium:deviceName"] = device
    if udid := os.getenv(f"UDID_{suffix}"):
        caps["appium:udid"] = udid
    url = os.getenv(f"APPIUM_SERVER_URL_{suffix}", base.appium_server_url)
    if caps == base.capabilities and url == base.appium_server_url:
        raise pytest.UsageError(
            f"Running under xdist but no per-worker device configured for {worker_id!r}: "
            f"set DEVICE_NAME_{suffix} / APPIUM_SERVER_URL_{suffix} (two workers cannot "
            "share one device)"
        )
    return base.model_copy(update={"capabilities": caps, "appium_server_url": url})


@pytest.fixture(scope="session")
def driver(settings: Settings):
    """One driver session per worker (join1-style economics): session creation
    pays no reinstall (noReset), and each scenario sets its own app state via
    AppSession — reset_to_logged_out for signup-like suites, relaunch_to_root
    for logged-in suites. Trade-off: a dead session fails the remaining
    scenarios of the run; acceptable, rebuild is one rerun away."""
    driver = create_driver(settings)
    yield driver
    try:
        driver.quit()
    except WebDriverException:  # a dead session must not pollute the test result
        logger.warning("driver.quit() failed; session already gone", exc_info=True)


# ---- failure diagnostics -------------------------------------------------

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    driver = item.funcargs.get("driver")
    if driver is None:
        return
    try:
        png = driver.get_screenshot_as_png()
        allure.attach(png, name="failure_screenshot", attachment_type=allure.attachment_type.PNG)
        shots = Path("screenshots")
        shots.mkdir(exist_ok=True)
        # scenario names carry spaces/quotes/unicode — keep filenames filesystem-safe
        safe_name = re.sub(r"[^\w.-]+", "_", item.name)[:150]
        (shots / f"{safe_name}.png").write_bytes(png)
        allure.attach(driver.page_source, name="page_source",
                      attachment_type=allure.attachment_type.XML)
    except Exception:  # driver may already be dead; diagnostics must not mask the real failure
        logger.exception("Failed to capture failure diagnostics")


_CYAN   = "\033[96m"
_YELLOW = "\033[93m"
_GREEN  = "\033[92m"
_RED    = "\033[91m"
_WHITE  = "\033[37m"
_BOLD   = "\033[1m"
_RESET  = "\033[0m"

_KEYWORD_COLOR = {
    "Given": _CYAN,
    "When":  _YELLOW,
    "Then":  _GREEN,
    "And":   _WHITE,
    "But":   _WHITE,
}


def pytest_bdd_before_scenario(request, feature, scenario):
    print(f"\n{_BOLD}  Scenario: {scenario.name}{_RESET}", flush=True)


def pytest_bdd_before_step(request, feature, scenario, step, step_func):
    keyword = step.keyword.strip()
    color = _KEYWORD_COLOR.get(keyword, _WHITE)
    print(f"    {_BOLD}{color}{keyword}{_RESET} {step.name}", end="  ", flush=True)


def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args):
    print(f"{_GREEN}✓{_RESET}", flush=True)


def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    print(f"{_RED}✗{_RESET}", flush=True)
    logger.error("Step failed: [%s] %s %s -> %s",
                 scenario.name, step.keyword, step.name, exception)
