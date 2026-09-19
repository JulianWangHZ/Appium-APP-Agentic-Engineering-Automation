---
name: coding-standards
description: Coding conventions for all automation code in this repo (steps / screens / core / api / config)
globs: ["**/*.py"]
---

# Automation Code Conventions

Mechanical style is ruff's job (`uv run ruff check .`); this file covers what
ruff can't see. When in doubt, read the neighboring code — consistency beats
preference.

## Layering (hard red lines)

Dependencies point one way: **steps → screens → core**. Violations to reject
on sight:

- Steps contain **no selectors, no raw-driver calls, no business logic** beyond
  assertions — parse args → call a Screen/API method → assert.
- Screens never touch test infra (fixtures, pytest, config loading) and never
  call other screens' privates; **all Appium calls funnel through
  `core/base_screen.py`**.
- `core/` never imports from `screens/`, `tests/`, or `api/`.
- API clients stay thin (endpoint methods only); cross-endpoint flows go in
  `api/workflows.py`.

## Screens

- One class per screen, extending `BaseScreen`.
- `Locator` declarations grouped at the top of the class; methods below.
- Methods named by **business intent** (`create_playlist()`), never by widget
  mechanics (`tap_confirm_button()`).
- Several UI actions forming one business action → one composite method
  (this is what keeps feature files declarative).
- Platform divergence branches on `self.platform` **inside** the method; split
  into per-platform screen files only when entire screens differ.

## Locators

- Priority: accessibility id (`by_a11y_id`) > id > platform-native
  (predicate / uiautomator) > xpath (avoid).
- Dynamic locators = factory functions returning `Locator`, argument embedded
  in `name` for debuggability.
- No structural XPath chains, no absolute coordinates in locators
  (coordinate taps exist only as `BaseScreen` escape hatches).

## Waits & stability

- **No `time.sleep` in test/screen code, ever.** Wait on a business anchor:
  `wait_visible` / `wait_not_visible` / `wait_enabled`.
- `is_visible` is a branching probe; assertions use `wait_*` (they raise
  `TimeoutError` with the element name).
- Re-render flakiness → `tap_stable`; keyboard in the way → `hide_keyboard`;
  enabled=false-but-tappable controls → `tap_element_center`. Escalate in that
  order; coordinates are last resort.

## Fixtures & steps

- Screens are injected through the single `screens` catalog fixture
  (`screens/catalog.py`, lazy `cached_property` per screen). Adding a screen =
  one property in the catalog; steps use `screens.signup`, never construct
  screens inline and never add per-screen fixtures.
- Data flows between steps via `target_fixture`, never module globals.
- Shared Givens live in `tests/conftest.py`; feature-specific steps in their
  own `tests/steps/test_<feature>.py`.
- New Gherkin tags must be registered as markers in `pyproject.toml`
  (`--strict-markers` will fail otherwise).

## Config & secrets

- Machine-specific values (paths, devices, udid) come from env vars only —
  never hardcode into yaml or Python.
- Secrets from env (`.env` local, CI secrets); never in code, logs
  (`type(..., secret=True)` masks input), or committed files.
- New tunables follow the layering: env var > capabilities yaml > environment
  yaml, with a sane default so unset ≠ broken.

## General Python

- English everywhere (code, comments, docstrings, messages).
- Type hints on public signatures; `from __future__ import annotations` at
  module top.
- Prefer frozen dataclasses / immutable settings; mutation is a smell.
- Small files, small functions; comments explain constraints ("why"), never
  narrate the next line.
- Raise with context: error messages carry the element name / url / status —
  the failure must be diagnosable from the message alone.
- No new dependency without a reason a reviewer would accept.

## Verification gate (before claiming done)

```bash
uv run ruff check . && uv run pytest tests/unit -q
```

Framework-level logic (core/, config/, api/ base) gets unit tests in
`tests/unit/` — device-free, mock the driver/session boundary.
