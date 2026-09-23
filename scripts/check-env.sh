#!/usr/bin/env bash
# Local environment health-check for this pytest-bdd + Appium + iOS/Android framework.
# No third-party dependencies — pure bash + system tools.
set -u

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[OK]${NC}   $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
fail() { echo -e "${RED}[FAIL]${NC} $*"; FAILED=1; }
FAILED=0

IOS_BUNDLE="${IOS_BUNDLE:-com.example.spotifyClone}"
ANDROID_PACKAGE="${ANDROID_PACKAGE:-com.example.spotify_clone}"

echo "=== Appium pytest-bdd iOS/Android framework — env check ==="

# ── Python 3.11+ ──────────────────────────────────────────────────────────────
if command -v python3 >/dev/null 2>&1; then
  py_ver="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  major="$(python3 -c 'import sys; print(sys.version_info.major)')"
  minor="$(python3 -c 'import sys; print(sys.version_info.minor)')"
  if [[ "$major" -ge 3 && "$minor" -ge 11 ]]; then
    ok "Python $py_ver"
  else
    fail "Python $py_ver — framework requires >=3.11"
  fi
else
  fail "python3 not found"
fi

# ── uv ────────────────────────────────────────────────────────────────────────
if command -v uv >/dev/null 2>&1; then
  ok "uv $(uv --version 2>/dev/null | head -1)"
else
  fail "uv not found — install: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

# ── Project deps synced ───────────────────────────────────────────────────────
if [[ -d .venv ]]; then
  ok ".venv present (run 'uv sync' if stale)"
else
  warn ".venv missing — run: uv sync"
fi

# ── Appium ────────────────────────────────────────────────────────────────────
if command -v appium >/dev/null 2>&1; then
  ok "Appium $(appium -v 2>/dev/null)"

  driver_list="$(appium driver list 2>&1)"

  # XCUITest driver
  if echo "$driver_list" | grep -qi "xcuitest.*installed"; then
    ok "XCUITest driver installed"
  else
    fail "XCUITest driver missing — run: appium driver install xcuitest"
  fi

  # UiAutomator2 driver
  if echo "$driver_list" | grep -qi "uiautomator2.*installed"; then
    ok "UiAutomator2 driver installed"
  else
    fail "UiAutomator2 driver missing — run: appium driver install uiautomator2"
  fi
else
  fail "appium not found — run: npm install -g appium"
fi

# ── Appium port 4723 ──────────────────────────────────────────────────────────
if command -v lsof >/dev/null 2>&1; then
  appium_pid="$(lsof -ti :4723 -sTCP:LISTEN 2>/dev/null | head -1)"
  if [[ -n "$appium_pid" ]]; then
    ok "port 4723 listening (pid $appium_pid)"
  else
    warn "port 4723 not listening — start Appium: appium --port 4723"
  fi
else
  warn "lsof not available — cannot verify port 4723"
fi

# ── iOS simulator ─────────────────────────────────────────────────────────────
if [[ "$(uname)" == "Darwin" ]]; then
  if command -v xcrun >/dev/null 2>&1; then
    booted="$(xcrun simctl list devices booted 2>/dev/null | grep -c Booted || true)"
    if [[ "$booted" -gt 0 ]]; then
      ok "iOS simulator booted: $booted device(s)"

      # App installed on booted sim?
      if xcrun simctl listapps booted 2>/dev/null | grep -q "${IOS_BUNDLE}"; then
        ok "app installed on booted sim: ${IOS_BUNDLE}"
      else
        warn "app NOT installed on booted sim (${IOS_BUNDLE}) — deploy: xcrun simctl install booted apps/spotify-clone.app"
      fi
    else
      warn "no booted iOS simulator — open one in Xcode > Window > Devices and Simulators"
    fi
  else
    fail "xcrun not found — install Xcode Command Line Tools: xcode-select --install"
  fi
else
  warn "not macOS — iOS simulator checks skipped"
fi

# ── Android (adb + emulator) ──────────────────────────────────────────────────
if command -v adb >/dev/null 2>&1; then
  devices="$(adb devices 2>/dev/null | tail -n +2 | grep -v '^$')"
  device_count="$(echo "$devices" | grep -c . || true)"
  if [[ "$device_count" -gt 0 ]]; then
    ok "adb online devices: $device_count"

    # App installed on first online device?
    first_serial="$(echo "$devices" | head -1 | awk '{print $1}')"
    if adb -s "$first_serial" shell pm list packages 2>/dev/null | grep -q "${ANDROID_PACKAGE}"; then
      ok "app installed on $first_serial: ${ANDROID_PACKAGE}"
    else
      warn "app NOT installed on $first_serial (${ANDROID_PACKAGE}) — deploy: adb install apps/spotify-clone.apk"
    fi
  else
    warn "adb found but no online devices/emulators — start an AVD or connect a device"
  fi
else
  warn "adb not found — install Android SDK platform-tools and add to PATH"
fi

# ── Java (needed by some Android toolchain components) ───────────────────────
if command -v java >/dev/null 2>&1; then
  ok "Java $(java -version 2>&1 | head -1)"
else
  warn "java not found — some Android toolchain components require JDK"
fi

# ── Result ────────────────────────────────────────────────────────────────────
echo ""
if [[ "$FAILED" -eq 0 ]]; then
  echo -e "${GREEN}All checks passed.${NC}"
else
  echo -e "${RED}One or more checks FAILED — fix the items above before running tests.${NC}"
  exit 1
fi
