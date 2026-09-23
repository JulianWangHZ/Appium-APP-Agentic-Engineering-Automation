"""pytest plugin — generates a self-contained Markdown test report.

Registered automatically via conftest.py pytest_plugins.
Output: reports/<timestamp>-<platform>.md + reports/latest.md symlink.

Hooks used:
  pytest_bdd_before_scenario  — initialise step tracking per scenario
  pytest_bdd_before_step      — mark step as running
  pytest_bdd_after_step       — mark step passed + duration
  pytest_bdd_step_error       — mark step failed + message
  pytest_runtest_makereport   — capture screenshot on call-phase failure
  pytest_unconfigure          — flush report to disk
"""
from __future__ import annotations

import base64
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

# ── constants ────────────────────────────────────────────────────────────────
REPORTS_DIR = Path("reports")
ANSI = re.compile(r"\x1b\[[0-9;]*m")
PASS = "✓"
FAIL = "✗"
SKIP = "–"
RUNNING = "·"


# ── helpers ───────────────────────────────────────────────────────────────────
def _git(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *cmd], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"


def _opt(config: pytest.Config, name: str, default: str = "") -> str:
    try:
        v = config.getoption(name)
        return v if v is not None else default
    except (ValueError, AttributeError):
        return default


def _strip(s: str) -> str:
    return ANSI.sub("", s)


def _fmt_ms(ms: float) -> str:
    if ms < 1000:
        return f"{ms:.0f}ms"
    s = ms / 1000
    if s < 60:
        return f"{s:.1f}s"
    return f"{int(s // 60)}m{int(s % 60)}s"


# ── plugin class ──────────────────────────────────────────────────────────────
class _Report:
    def __init__(self) -> None:
        self._scenarios: list[dict[str, Any]] = []
        self._started_at = time.time()

    # ── BDD hooks ─────────────────────────────────────────────────────────────

    def pytest_bdd_before_scenario(
        self, request: pytest.FixtureRequest, feature: Any, scenario: Any
    ) -> None:
        steps = [
            {
                "keyword": getattr(step, "keyword", "") or "",
                "text": getattr(step, "name", "") or "",
                "status": "NOT_RUN",
                "duration_ms": 0.0,
                "error": None,
            }
            for step in (getattr(scenario, "steps", None) or [])
        ]
        entry: dict[str, Any] = {
            "nodeid": request.node.nodeid,
            "feature": getattr(feature, "name", ""),
            "scenario": getattr(scenario, "name", ""),
            "tags": [t.strip("@") for t in getattr(scenario, "tags", [])],
            "steps": steps,
            "status": "RUNNING",
            "duration_ms": 0.0,
            "started_at": time.time(),
            "screenshots": [],
        }
        request.config._report_scenarios[request.node.nodeid] = entry  # type: ignore[attr-defined]

    def _get_step(self, request: pytest.FixtureRequest, step: Any) -> dict[str, Any] | None:
        scenarios: dict = getattr(request.config, "_report_scenarios", {})
        entry = scenarios.get(request.node.nodeid)
        if not entry:
            return None
        step_name = getattr(step, "name", "")
        for s in entry["steps"]:
            if s["text"] == step_name and s["status"] in ("NOT_RUN", "RUNNING"):
                return s
        return None

    def pytest_bdd_before_step(
        self, request: pytest.FixtureRequest, feature: Any, scenario: Any, step: Any, step_func: Any
    ) -> None:
        s = self._get_step(request, step)
        if s:
            s["status"] = "RUNNING"
            s["_t"] = time.time()

    def pytest_bdd_after_step(
        self, request: pytest.FixtureRequest, feature: Any, scenario: Any, step: Any, step_func: Any
    ) -> None:
        s = self._get_step(request, step)
        if s:
            s["status"] = "PASS"
            s["duration_ms"] = (time.time() - s.pop("_t", time.time())) * 1000

    def pytest_bdd_step_error(
        self,
        request: pytest.FixtureRequest,
        feature: Any,
        scenario: Any,
        step: Any,
        step_func: Any,
        step_func_args: Any,
        exception: Exception,
    ) -> None:
        s = self._get_step(request, step)
        if s:
            s["status"] = "FAIL"
            s["duration_ms"] = (time.time() - s.pop("_t", time.time())) * 1000
            s["error"] = _strip(str(exception))[:400]

    # ── screenshot on failure ─────────────────────────────────────────────────

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_makereport(self, item: pytest.Item, call: pytest.CallInfo) -> Any:
        outcome = yield
        report = outcome.get_result()
        if call.when != "call" or not report.failed:
            return
        scenarios: dict = getattr(item.config, "_report_scenarios", {})
        entry = scenarios.get(item.nodeid)
        if not entry:
            return
        # Try to take an Appium screenshot via the driver fixture (if available).
        try:
            driver = item.funcargs.get("driver")
            if driver is not None:
                png = driver.get_screenshot_as_base64()
                REPORTS_DIR.mkdir(parents=True, exist_ok=True)
                safe_name = re.sub(r"[^\w]", "_", item.nodeid)[:80]
                ts = datetime.now().strftime("%H%M%S")
                shot_path = REPORTS_DIR / f"{ts}_{safe_name}.png"
                shot_path.write_bytes(base64.b64decode(png))
                entry["screenshots"].append(str(shot_path))
        except Exception:
            pass

    # ── finalise ──────────────────────────────────────────────────────────────

    def pytest_unconfigure(self, config: pytest.Config) -> None:
        if config.option.collectonly:
            return
        scenarios: dict = getattr(config, "_report_scenarios", {})
        if not scenarios:
            return
        # Resolve overall status for each scenario.
        for entry in scenarios.values():
            statuses = {s["status"] for s in entry["steps"]}
            if "FAIL" in statuses:
                entry["status"] = "FAIL"
            elif "RUNNING" in statuses or "NOT_RUN" in statuses:
                entry["status"] = "SKIP"
            else:
                entry["status"] = "PASS"
            entry["duration_ms"] = (time.time() - entry["started_at"]) * 1000

        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        platform = _opt(config, "--platform", "unknown")
        report_path = REPORTS_DIR / f"{ts}-{platform}.md"
        _write_md(report_path, list(scenarios.values()), config, platform)

        # latest.md symlink (Unix only)
        latest = REPORTS_DIR / "latest.md"
        try:
            latest.unlink(missing_ok=True)
            latest.symlink_to(report_path.name)
        except OSError:
            pass

        passed = sum(1 for e in scenarios.values() if e["status"] == "PASS")
        failed = sum(1 for e in scenarios.values() if e["status"] == "FAIL")
        skipped = sum(1 for e in scenarios.values() if e["status"] == "SKIP")
        print(f"\n  Report → {report_path}  ({passed}✓ {failed}✗ {skipped}–)\n")


# ── markdown writer ───────────────────────────────────────────────────────────

def _write_md(path: Path, scenarios: list[dict], config: pytest.Config, platform: str) -> None:
    lines: list[str] = []
    total = len(scenarios)
    passed = sum(1 for e in scenarios if e["status"] == "PASS")
    failed = sum(1 for e in scenarios if e["status"] == "FAIL")
    skipped = total - passed - failed
    duration = sum(e["duration_ms"] for e in scenarios)

    lines += [
        "# Test Report",
        "",
        "| | |",
        "|---|---|",
        f"| **Platform** | {platform} |",
        f"| **Branch** | {_git(['rev-parse', '--abbrev-ref', 'HEAD'])} |",
        f"| **Commit** | `{_git(['rev-parse', '--short', 'HEAD'])}` |",
        f"| **Suite** | {_opt(config, '-m', '—')} |",
        f"| **Started** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |",
        f"| **Duration** | {_fmt_ms(duration)} |",
        "",
        "## Summary",
        "",
        "| Passed | Failed | Skipped | Total |",
        "|---|---|---|---|",
        f"| {passed} | {failed} | {skipped} | {total} |",
        "",
        "## Results",
        "",
    ]

    for entry in scenarios:
        icon = {"PASS": PASS, "FAIL": FAIL}.get(entry["status"], SKIP)
        lines.append(f"### {icon} {entry['scenario']}")
        lines.append(f"*Feature: {entry['feature']}*")
        if entry["tags"]:
            lines.append("  ".join(f"`@{t}`" for t in entry["tags"]))
        lines.append("")
        lines.append("| Step | Status | Duration |")
        lines.append("|---|---|---|")
        for step in entry["steps"]:
            s_icon = {"PASS": PASS, "FAIL": FAIL, "SKIP": SKIP}.get(step["status"], RUNNING)
            kw = step["keyword"].strip()
            lines.append(f"| {kw} {step['text']} | {s_icon} | {_fmt_ms(step['duration_ms'])} |")
        # Failure error
        for step in entry["steps"]:
            if step["error"]:
                lines.append("")
                lines.append(f"> **Failure:** `{step['error']}`")
        # Screenshots
        for shot in entry["screenshots"]:
            lines.append("")
            lines.append(f"![screenshot]({shot})")
        lines.append("")
        lines.append("---")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


# ── registration ──────────────────────────────────────────────────────────────

def pytest_configure(config: pytest.Config) -> None:
    if not hasattr(config, "_report_scenarios"):
        config._report_scenarios = {}  # type: ignore[attr-defined]
    plugin = _Report()
    config.pluginmanager.register(plugin, "_custom_report")
