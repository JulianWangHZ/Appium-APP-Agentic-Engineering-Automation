# Appium APP Agentic Engineering Automation

> A blueprint for agentic mobile E2E automation — Claude explores the live app, maps real locators, and generates BDD automation code. No manual selector hunting. No guessing.

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Appium](https://img.shields.io/badge/appium-3.x-6a4c93)](https://appium.io/)
[![pytest-bdd](https://img.shields.io/badge/pytest--bdd-7.x-0a9e5c)](https://pytest-bdd.readthedocs.io/)
[![uv](https://img.shields.io/badge/package_manager-uv-de7a2e)](https://github.com/astral-sh/uv)
[![Allure](https://img.shields.io/badge/report-allure-orange)](https://allurereport.org/)
[![Platform](https://img.shields.io/badge/platform-iOS%20%7C%20Android-lightgrey)]()

---

## Demo

<video src="https://github.com/user-attachments/assets/52750420-5995-49c1-b5f9-ee03b40b876a" controls autoplay loop muted width="100%"></video>

---

## What it does

| Capability | Detail |
|---|---|
| **Agentic exploration** | Planner agent walks each `@auto` scenario on the real device, extracts verified locators from the live Accessibility tree |
| **Evidence-driven generation** | Generator agent reads the evidence map and produces Screen Objects + step definitions — every selector traces back to live device proof |
| **Self-healing** | Healer agent reruns failing tests, inspects real device state, classifies root cause, applies minimal fixes |
| **Cross-platform** | Single codebase drives iOS (XCUITest) and Android (UiAutomator2); platform branches live inside Screen methods, not in test code |
| **BDD-first** | Feature files are the single source of truth; automation code is a derived artifact |
| **Parallel execution** | pytest-xdist distributes scenarios across workers; iOS and Android run in separate invocations |
| **Allure reporting** | Per-step screenshots, device metadata, and failure diffs in a hosted Allure report |

---

## Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Test runner | pytest | 8.x |
| BDD framework | pytest-bdd | 7.x |
| Mobile driver | Appium | 3.x |
| iOS automation | XCUITest driver | latest |
| Android automation | UiAutomator2 driver | latest |
| Python client | Appium-Python-Client | 4.x |
| Package manager | uv | latest |
| Config | pydantic-settings + YAML + .env | 2.x |
| Reporting | Allure | 2.x |
| Parallelism | pytest-xdist | 3.x |
| Data generation | Faker | 24.x |

---

## Architecture

Four layers. Dependencies point one way — top to bottom. No exceptions.

```
┌─────────────────────────────────────────────┐
│              Feature Files                  │  Gherkin — human-readable, @auto tagged
├─────────────────────────────────────────────┤
│              Step Definitions               │  Parse args → call Screen → assert
├─────────────────────────────────────────────┤
│              Screen Objects                 │  Business-intent methods over BaseScreen
├─────────────────────────────────────────────┤
│                   Core                      │  Appium driver, waits, locators, session
└─────────────────────────────────────────────┘
```

| Layer | Location | Rule |
|---|---|---|
| Feature files | `features/` | Source of truth; never modified by generator |
| Step definitions | `tests/steps/` | No selectors, no driver calls — parse args, call Screen, assert |
| Screen Objects | `screens/` | All Appium calls via `BaseScreen`; methods named by business intent |
| Core | `core/` | Never imports from `screens/`, `tests/`, or `api/` |

---

## Project Structure

```
├── features/                  # Gherkin feature files (@auto scenarios)
│   ├── auth/
│   └── home/
├── tests/
│   ├── steps/                 # Step definitions per feature
│   │   ├── test_signup.py
│   │   └── test_home.py
│   ├── unit/                  # Device-free unit tests (core, config, api)
│   └── conftest.py
├── screens/                   # Screen Objects
│   ├── catalog.py             # Lazy cached_property registry
│   ├── home_screen.py
│   ├── signup_screen.py
│   └── ...
├── core/
│   ├── base_screen.py         # All Appium calls funnel here
│   ├── locator.py             # Locator(by, value, name)
│   ├── wait.py                # wait_visible / wait_not_visible / wait_enabled
│   ├── driver_factory.py
│   └── app_session.py
├── config/
│   ├── settings.py            # Pydantic Settings; env var > caps yaml > env yaml
│   ├── capabilities/          # ios.yaml / android.yaml
│   └── environments/          # staging.yaml / prod.yaml
├── api/                       # Thin HTTP client for test data setup
├── flows/                     # Cross-screen reusable flows
├── utils/                     # Faker-backed data factory
├── evidence/                  # Planner output: real locators per scenario
├── apps/                      # App binaries (.app / .apk) — gitignored
└── scripts/
    └── check-env.sh           # Local environment health-check
```

---

## Requirements

| Tool | Version | Purpose |
|---|---|---|
| Python | ≥ 3.11 | Runtime |
| uv | latest | Package & venv management |
| Appium | 3.x | Mobile automation server |
| XCUITest driver | latest | iOS (`appium driver install xcuitest`) |
| UiAutomator2 driver | latest | Android (`appium driver install uiautomator2`) |
| Xcode + xcrun | latest | iOS simulator management (macOS only) |
| Android SDK (adb) | latest | Android emulator / device |

Run the health-check to verify everything at once:

```bash
bash scripts/check-env.sh
```

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/JulianWangHZ/Appium-APP-Agentic-Engineering-Automation.git
cd Appium-APP-Agentic-Engineering-Automation

# 2. Install dependencies
uv sync

# 3. Configure
cp .env.example .env   # then edit .env — see Configuration section below

# 4. Start Appium
appium --port 4723

# 5. Run
uv run pytest -m smoke --platform=ios
```

---

## Running Tests

### By suite

```bash
uv run pytest -m smoke      --platform=ios
uv run pytest -m regression --platform=android
```

### By scenario keyword

```bash
uv run pytest -k "user signs up with valid credentials" --platform=ios
```

### Parallel execution

```bash
uv run pytest -m regression --platform=ios -n 2
```

### Rerun failures only

```bash
uv run pytest --lf --platform=ios
```

### Generate Allure report

```bash
uv run pytest -m regression --platform=ios --alluredir=allure-results
allure serve allure-results
```

---

## Command Reference

| Command | Purpose |
|---|---|
| `bash scripts/check-env.sh` | Full environment health-check (Python, uv, Appium, drivers, simulator, emulator) |
| `uv sync` | Install / update all dependencies |
| `uv run pytest -m smoke --platform=ios` | Run iOS smoke suite |
| `uv run pytest -m smoke --platform=android` | Run Android smoke suite |
| `uv run pytest -m regression -n 2` | Run full regression in parallel |
| `uv run pytest --lf` | Rerun last-failed scenarios only |
| `uv run ruff check .` | Lint — required before commit |
| `uv run pytest tests/unit -q` | Device-free unit tests — required before commit |

---

## Configuration

Copy the template and fill in your machine-specific values:

```bash
cp .env.example .env
```

`.env` is gitignored — never commit it. In CI, set the same variable names as repository secrets.

```dotenv
# ── App builds (required) ────────────────────────────────────────────────────
IOS_APP_PATH=apps/spotify-clone.app       # absolute or relative path to .app
ANDROID_APP_PATH=apps/spotify-clone.apk  # absolute or relative path to .apk

# ── Device targeting (overrides capabilities yaml) ───────────────────────────
# DEVICE_NAME=iPhone 18 Pro              # simulator name or emulator serial
# UDID=                                  # pin a specific device / simulator

# ── Parallel workers (xdist) ─────────────────────────────────────────────────
# One set per worker when running -n N:
# DEVICE_NAME_GW0=  UDID_GW0=  APPIUM_SERVER_URL_GW0=
# DEVICE_NAME_GW1=  UDID_GW1=  APPIUM_SERVER_URL_GW1=

# ── Tuning ───────────────────────────────────────────────────────────────────
# APPIUM_SERVER_URL=http://127.0.0.1:4723   # default
# EXPLICIT_WAIT=15                           # element wait in seconds
# RERUNS=1                                   # flaky-retry count

# ── App identity (only if testing a different build flavour) ─────────────────
# IOS_APP_ID=com.example.spotifyClone
# ANDROID_APP_ID=com.example.spotify_clone
```

**Priority chain:** env var → `capabilities/<platform>.yaml` → `environments/<env>.yaml`

The only values you *must* set are the app paths. Everything else has a working default.

---

## Inspecting Locators

Use **Appium Locators Inspector** — a Chrome extension that connects to your local Appium session and shows the live element tree with ranked, verified locators.

[![Install on Chrome](https://img.shields.io/badge/Chrome-Add%20to%20Chrome-4285F4?logo=googlechrome&logoColor=white)](https://chromewebstore.google.com/detail/appium-locators-inspector/annejeomdlkidljonmpmhcdnekkadjfb)

### Installation

1. Click **Add to Chrome** on the [Web Store listing](https://chromewebstore.google.com/detail/appium-locators-inspector/annejeomdlkidljonmpmhcdnekkadjfb)
2. Open the extension → **Settings → Setup** → install the local companion (one command, auto-generated)

   ![Setup](https://raw.githubusercontent.com/JulianWangHZ/Appium-Locators-Inspector/main/docs/images/hero-setup.png)

3. Run **Environment Doctor** inside the extension — it reports exactly what's missing

### What it gives you

![Inspector](https://raw.githubusercontent.com/JulianWangHZ/Appium-Locators-Inspector/main/docs/images/hero-inspector.png)

| Feature | Detail |
|---|---|
| **Live UI Tree** | Real-time element tree from a running iOS simulator or Android emulator |
| **Ranked locators** | Candidates evaluated against page source — unique ones flagged **Recommended**, fragile ones flagged **Brittle** |
| **Locator strategies** | `accessibility id`, `resource-id`, `UiAutomator2`, iOS predicate string & class chain, XPath |
| **Copy as Code** | One-click export as Python, Java, or TypeScript |
| **Record → Test** | Tap through the app; each gesture becomes a step; exports as a runnable test file |
| **100% local** | Communicates only with localhost — nothing leaves your machine |

**Recording workflow:**

<table>
<tr>
<td><img src="https://raw.githubusercontent.com/JulianWangHZ/Appium-Locators-Inspector/main/docs/images/hero-record.png" alt="Recording"/></td>
<td><img src="https://raw.githubusercontent.com/JulianWangHZ/Appium-Locators-Inspector/main/docs/images/hero-recorded.png" alt="Recorded test"/></td>
</tr>
<tr>
<td align="center">Tap through the app to record steps</td>
<td align="center">Export as a runnable test file</td>
</tr>
</table>

### Workflow

```
1. Boot simulator / emulator
2. Start Appium:  appium --port 4723
3. Open Chrome → Appium Locators Inspector
4. Create a session (or attach to existing)
5. Tap any element in the mirrored screen → copy the Recommended locator
6. Paste into your Screen Object's Locator declaration
```

---

## Locator Priority

```
accessibility id  →  id  →  iOS predicate / Android uiautomator  →  xpath (last resort)
```

No `time.sleep` anywhere. Always wait on a business anchor:

| Method | When to use |
|---|---|
| `wait_visible(locator)` | Element must appear before interaction |
| `wait_not_visible(locator)` | Element must disappear (e.g. loading spinner) |
| `wait_enabled(locator)` | Element must become interactive |
| `tap_stable(locator)` | Re-render flakiness — taps after stability check |

