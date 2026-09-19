"""Central config loader.

Priority (high -> low): environment variables (.env) > capabilities yaml > environment yaml.
Selected at runtime via CLI: pytest --platform=android --env=staging
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel

CONFIG_DIR = Path(__file__).parent

load_dotenv()


class Settings(BaseModel):
    platform: Literal["android", "ios"]
    env: str  # "staging" | "prod"
    appium_server_url: str
    capabilities: dict
    app_id: str  # package name / bundle id — clearApp, terminate/activate need it
    api_base_url: str
    implicit_wait: int = 0  # keep 0; use explicit waits only
    explicit_wait: int = 15

    model_config = {"frozen": True}


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        available = sorted(p.stem for p in path.parent.glob("*.yaml"))
        raise FileNotFoundError(f"Config file not found: {path} (available: {available})")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@lru_cache
def get_settings(platform: str, env: str) -> Settings:
    env_conf = _load_yaml(CONFIG_DIR / "environments" / f"{env}.yaml")
    caps = _load_yaml(CONFIG_DIR / "capabilities" / f"{platform}.yaml")

    # app_id is framework config, not an Appium capability — pop before sending caps
    app_id = caps.pop("app_id", None)
    if not app_id:
        raise KeyError(f"'app_id' missing in capabilities/{platform}.yaml")

    # env-var overrides for machine/build-specific values;
    # platform-specific var (IOS_* / ANDROID_*) beats the generic one
    prefix = platform.upper()
    if app_id_env := os.getenv(f"{prefix}_APP_ID") or os.getenv("APP_ID"):
        app_id = app_id_env
    if device := os.getenv("DEVICE_NAME"):
        caps["appium:deviceName"] = device
    if udid := os.getenv("UDID"):
        caps["appium:udid"] = udid
    if app := os.getenv(f"{prefix}_APP_PATH") or os.getenv("APP_PATH"):
        caps["appium:app"] = app

    return Settings(
        platform=platform,
        env=env,
        appium_server_url=os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723"),
        capabilities=caps,
        app_id=app_id,
        api_base_url=env_conf["api_base_url"],
        explicit_wait=int(os.getenv("EXPLICIT_WAIT", env_conf.get("explicit_wait", 15))),
    )
