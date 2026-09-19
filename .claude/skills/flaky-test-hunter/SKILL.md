---
name: flaky-test-hunter
description: Quantify flaky tests from GitHub Actions CI history — per-test failure rates, root-cause patterns, quarantine recommendations. Trigger when the user says "flaky test, unstable tests, false failures, passes on retry, CI unstable, quarantine, hunt flaky".
allowed-tools: Read, Grep, Glob, Write, Edit, Bash
argument-hint: "[workflow name] [--days=30] [--threshold=1%]"
---

# flaky-test-hunter

Quantify which tests are flaky in CI, with data that persuades the team to fix.

## Phase 1: Collect CI failure history

```bash
# Workflow name from $1; if absent, `gh workflow list` and pick (default: mobile-tests.yml)
WF="${1:-mobile-tests.yml}"
gh run list --workflow="$WF" --limit=100 --json databaseId,conclusion,createdAt
gh run view <id> --log-failed
```

Default window: last 30 days.

## Phase 2: Flakiness score

```
flakiness_score = (failing_in_otherwise_passing_runs / total_runs) × 100%
```

- **Stable**: 0% — always passes
- **Stable-fail**: >80% and always fails → real bug, not flaky
- **Flaky**: 1–80% — alternates

Report the flaky band only.

## Phase 3: Severity

| Level | Flakiness | Action |
|---|---|---|
| 🔴 High | > 30% | quarantine now + fix |
| 🟡 Medium | 10–30% | quarantine, schedule fix |
| 🟢 Low | 1–10% | monitor |

## Phase 4: Root-cause patterns

| Pattern | Example | Fix direction |
|---|---|---|
| Hard-coded sleep | `time.sleep(2)` | `poll_until` / `wait_visible` (core/wait.py) |
| One-shot visibility check | `is_visible()` racing an animation | `wait_visible` (stale-safe poll) |
| Element-level tap on re-rendering view | "element found then detached" | `tap_stable` |
| Shared state across scenarios | login state leaking between tests | `app_session.relaunch_to_root` / fresh driver |
| Device/session contention | two workers on one device | per-worker `DEVICE_NAME_GW<n>` mapping |
| Random data without seed | Faker without fixed seed | fix the seed or assert on invariants |
| Real external calls | real SMS/push in test path | mock at the API boundary |

## Phase 5: Report

```markdown
# Flaky Test Report · {workflow} · {date}

## Overall
- Window: last 30 days (n=X runs)
- Total tests: X — Flaky: X (X%), target < 2%

## 🔴 High flaky (> 30%)

### #1 `tests/steps/test_playlist.py::Create playlist shows confirmation` (47%)
- Failed: 23 / 49 runs
- Suspected cause: one-shot `is_visible` during list refresh (screens/playlist_screen.py:42)
- Suggestion: switch to `wait_visible`
- Action: tag `@quarantine` (CI warns, doesn't block)

## Action items
- [ ] Quarantine X high-flaky scenarios
- [ ] Open one tracking ticket per high-flaky test
```

## Phase 6: Ask before touching anything

- Add `@quarantine` tags / skip annotations? (register the marker in pyproject)
- Open tracking tickets?

Default: **report only, no test-code changes**.

## Guardrails

- ❌ Never disable a test without explicit consent
- ❌ Never label stable-fail (a real bug) as flaky
- ✅ Quarantine markers must carry `must-fix-by: YYYY-MM-DD`
- ✅ One tracking ticket per high-flaky test
