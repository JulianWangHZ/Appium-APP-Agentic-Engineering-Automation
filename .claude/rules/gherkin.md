---
description: Gherkin BDD writing rules and tag taxonomy for all .feature files
globs: ["**/*.feature"]
---

## Gherkin Principles

- Steps in English; concrete data in double quotes
- Steps describe the user's perspective — no API-layer or implementation detail;
  **never write "bypass the UI and call the API directly" scenarios** (developer
  perspective; backend hardening belongs to unit/integration tests)
- Every scenario runs independently (never depends on a previous scenario's state)
- Every scenario must trace to a requirement/ticket — no invented situations
- Feature preamble is mandatory (As a X / I want Y / So that Z)
- `Background:` only for preconditions truly shared by all scenarios (Given steps only)

## Declarative (WHAT, not HOW)

Steps express user intent, not UI mechanics:

| | Example |
|---|---|
| ✅ Declarative | `When I book the "10:00" slot on "2026/07/01"` |
| ❌ Imperative | `When I pick date "2026/07/01"` + `And I pick slot "10:00"` + `And I tap confirm` |

- A step maps to a business action, not a widget interaction (tap/type/select)
- Needing several imperative steps for one business action signals a missing
  composite method on the Screen Object — add the method, don't unroll the
  detail into the feature
- **Never mix imperative and declarative styles** — one leak and imperative
  steps spread

## Feature File Format

```gherkin
# Screen code path: {app-side path or module, if known}
# Note: {optional; cross-feature dependencies, may span lines}
Feature: {name}
  As a {role}
  I want {goal}
  So that {value}

  # ############################################
  # {section name}
  # ############################################
  @{screen} @{smoke/regression/auto}
  Scenario: ...
```

- Section separators group scenarios by business function
- Avoid `Scenario Outline / Examples` — enumerate cases as named scenarios so
  each failure reads as a business case, not a table row

## Tag Taxonomy

**Feature level**: role tags only when one feature serves multiple roles;
single-role features carry the role in the preamble instead.

**Scenario level** — three orthogonal axes; each tag answers exactly one question:

| Axis | Question | Tags |
|---|---|---|
| Suite | When does it run? | `@smoke` ⊂ `@regression` |
| Execution | Who runs it? | `@auto` (absent = manual) |
| Nature | What kind of case? | `@boundary` (absent = normal positive/negative) |

**Suite tags (mandatory)**

| Tag | Definition |
|---|---|
| `@regression` | Default for everything. Pre-release functional coverage — positive **and** negative. Only exploratory/one-off scenarios are excluded. |
| `@smoke` | Subset of `@regression`. First gate after a deploy — core happy paths only, usually 1–3 per feature. |

> Iron rule: `@boundary` is **not** a reason to drop `@regression`. Hard-to-build
> test data → mark manual (no `@auto`), don't kick it out of regression.

**Execution tag**

- `@auto`: programmatically executable **and** programmatically verifiable
  (text/state/visibility). API-based data setup is allowed. Excludes anything
  needing human judgment or uncontrollable externals (manual review, real SMS,
  visual comparison).
- `@auto` carries two-phase semantics: at authoring time it is a **feasibility
  candidate** (judge intrinsic automatability, not whether the screen is built
  yet); at implementation time a live probe on the real device is the
  **authoritative review** — demote (remove `@auto`) only with probe evidence,
  quarantine if flaky. "Feature not built yet" is never a reason to withhold
  `@auto`.

**Nature tag**

`@boundary` marks true extremes only — input-domain or state-space edges
(threshold values, resource exhaustion, races/timing, fault injection).
Invalid input, auth failures, and empty states are ordinary negatives:
`@regression` only. Deciding question: does the trigger occur in casual use
(ordinary negative) or must the system be pushed to a critical/exhausted/rare
state (`@boundary`)?

**Quick combos**

| Case | Tags |
|---|---|
| Core positive, automatable | `@smoke @regression @auto` |
| Core positive, manual | `@smoke @regression` |
| Ordinary negative, automatable | `@regression @auto` |
| Boundary, automatable | `@regression @auto @boundary` |
| Boundary, manual | `@regression @boundary` |

**Context tags (mandatory, ≥1)**: short noun phrase naming the business
condition — happy paths named by precondition/outcome (`@valid-account`),
negatives/boundaries by trigger (`@slot-taken`, `@session-expired`).

**Forbidden**: `@P0`/priority tags, version tags, scenario titles as tags,
whitespace inside tags. Register every new tag as a pytest marker in
pyproject.toml (`--strict-markers` is on).
