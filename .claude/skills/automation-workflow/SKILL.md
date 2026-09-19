---
name: automation-workflow
description: Implement automation for existing @auto scenarios — fill in missing step definitions / Screen Objects / fixtures. Live-probe-first — a planner walks the real simulator/emulator via appium-mcp to extract real locators into an evidence map, a feasibility gate reviews it, then code is generated from evidence and verified with pytest; residual failures go to healing. Trigger when the user says "implement steps, write automation, screen object, automate this feature, fix locators, fix failing tests".
argument-hint: "<feature path | @tag | scenario name | empty = scan all gaps>"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Agent
---

# automation-workflow

Implements automation for **existing @auto scenarios**. Scenarios were already
reviewed at authoring time — this workflow never re-derives them. Core idea:
**live-probe-first** — walk the scenario on the real simulator/emulator, extract
real locators, judge feasibility, only then write code. This prevents
hallucinated selectors and flows.

> Feasibility = can the UI be driven and asserted (decided by walking the real
> screen). API is only a data-setup mechanism, evaluated **after** the UI is
> proven reachable — `NEEDS_API_SETUP` means "UI automatable, precondition data
> needs API", never "feasibility lives in the API".

> Never commit/push unless explicitly asked. After changes always run
> `uv run ruff check . && uv run pytest tests/unit -q`.

---

## Phase −1: Triage (don't default to the full pipeline)

The multi-agent pipeline exists for **batch implementation of many scenarios**.
Small tasks through it = waste: subagents cold-start, losing context the main
session already has.

| Situation | Route |
|---|---|
| Feasibility check for one scenario | Live-probe **inline** via appium-mcp; no planner agent |
| Locator/wait fix in existing code, single failing test | **Inline**: look at the real screen → fix Screen/step → rerun the subset |
| User already gave you the screen, context, and bug location | **Act directly** — don't send an agent to rediscover what you have |
| Batch implementation across scenarios/files, systematic exploration | Full pipeline below |

**Run tests via CLI, not MCP**: `uv run pytest tests/steps/<subset> --platform=<p>`.
appium-mcp is for interactive locator extraction only; if an MCP call errors or
the server is down, degrade to CLI/simctl/adb + screenshots — don't retry the
same MCP call.

**Appium constraints**: never drive iOS and Android concurrently through one
Appium server (UiAutomator2 crashes → all results invalid). Reuse the running
Appium/device session for probing; never rebuild WDA / reinstall / re-login for
a single task — rebuild only when the session is truly dead.

---

## Phase 0: Scope

1. Read README design decisions and `.claude/rules/gherkin.md`.
2. `.feature` files are the source of truth — **never write or edit them here**;
   scenario changes go back to the authoring/review stage.
3. Scope from argument: feature path = that file's un-implemented @auto
   scenarios / @tag = gaps under that tag / scenario name = single / empty =
   scan everything (list first, confirm scope).

## Phase 1: Gap Discovery

- `uv run pytest --generate-missing --feature features/` lists scenarios and
  steps without bindings.
- Per scenario, list which layer is missing: step / Screen method / fixture /
  API client. Don't guess unknowns — they go to Phase 2 for live probing.

## Phase 2–3: Live Exploration → Evidence Map

Walk each scenario on the running simulator/emulator (appium-mcp
`getPageSource` + interactions; degrade to `xcrun simctl`/`adb` + screenshots).
Produce an **evidence map** at `evidence/<feature-relative-path>.md`: per step,
the verified locator (prefer accessibility id — Flutter `Semantics` identifier),
observed state transitions, and feasibility.

## Phase 3.5: Feasibility Gate

From the evidence map, classify per scenario:

- `AUTOMATABLE` / `NEEDS_API_SETUP` → Phase 4
- `NOT_FEASIBLE` → keep manual; report why (candidate for removing `@auto`)
- `TC_STALE` → stop; the scenario no longer matches the product — send back to
  authoring; suspected product bug → file a bug, don't code around it

Small scope may self-review; large scope or any NOT_FEASIBLE/TC_STALE → list
for user confirmation before generating.

## Phase 4: Generate

For gate-passing scenarios, write code following repo conventions:

- Steps in `tests/steps/test_<feature>.py` (`scenarios()` binding, shared
  Givens in `tests/conftest.py` with `target_fixture`)
- Screen Objects in `screens/` — `Locator`/`by_a11y_id` declarations +
  business-named composite methods; waits via `wait_visible`/`wait_enabled`;
  never touch the raw driver
- One screen fixture per class in `tests/conftest.py`
- **Every selector must trace to the evidence map** — no invented locators

## Phase 5: Verify

`uv run pytest <generated subset> --platform=<p>` on the same device, then
`uv run ruff check . && uv run pytest tests/unit -q`. Green → report/PR;
failures → Phase 7.

## Phase 7: Heal (residual failures only)

At the failure point, inspect the real screen, classify the root cause, fix at
the Screen/step layer, rerun.

**Guardrails**: suspected product bug → stop and report, never code around it;
needs a `.feature` change → forbidden, send back to authoring; same test red 3
rounds → stop and escalate; never mask with skip/xfail — persistent flakiness
gets `@quarantine` + a tracking ticket.

---

## Anti-hallucination (whole flow)

- Every selector traces to a live-probed evidence map entry.
- Two human gates: feasibility gate (before code-gen) and PR review (after green).
- `.feature` files are read-only inputs; all artifacts live in this repo.
