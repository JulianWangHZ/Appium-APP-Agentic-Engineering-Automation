"""App session lifecycle composites.

Absorbs reinstall/relaunch differences: the worker's first scenario calls
reset_to_logged_out for a clean logged-out state; subsequent scenarios call
relaunch_to_root (cold restart, login state preserved, navigation stack
reset) — an order of magnitude faster than reinstalling every scenario.
"""
from __future__ import annotations

import logging

from appium.webdriver.webdriver import WebDriver

from config.settings import Settings

logger = logging.getLogger("framework")


class AppSession:
    def __init__(self, driver: WebDriver, settings: Settings):
        self.driver = driver
        self.app_id = settings.app_id
        self.app_path = settings.capabilities.get("appium:app")

    def reset_to_logged_out(self) -> None:
        """Clearing data = logging out. Prefer clearApp (no reinstall — lighter,
        less churn); install only if missing; fall back to uninstall+install
        where clearApp is unsupported."""
        if not self.driver.is_app_installed(self.app_id):
            self.driver.install_app(self.app_path)
            self.driver.activate_app(self.app_id)
            return
        try:
            self.driver.execute_script("mobile: clearApp", {"appId": self.app_id})
        except Exception:
            logger.info("clearApp unsupported, falling back to reinstall")
            self.driver.remove_app(self.app_id)
            self.driver.install_app(self.app_path)
        self.driver.activate_app(self.app_id)

    def relaunch_to_root(self) -> None:
        """Cold restart back to the root screen (terminate → activate);
        login state persists."""
        self.driver.terminate_app(self.app_id)
        self.driver.activate_app(self.app_id)
