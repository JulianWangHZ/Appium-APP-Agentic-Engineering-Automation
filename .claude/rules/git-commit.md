---
name: git-commit
description: Conventional Commits format for this project
---

# Commit Message Format

## Structure

```
<type>(<scope>): <subject>

[body — optional]
```

## Types

| Type | When |
|---|---|
| `feat` | new capability, new skill, new script |
| `fix` | corrects wrong behavior |
| `refactor` | restructuring without behavior change |
| `test` | test cases (features, steps, unit tests) |
| `chore` | config, maintenance, dependency updates |
| `docs` | documentation, examples |
| `ci` | CI/CD pipeline changes |

## Scope

The smallest meaningful area touched, e.g.:

- layers: `core`, `screens`, `steps`, `features`, `api`, `config`, `utils`
- meta: `rules`, `skills`, `agents`, `docs`, `deps`, `ci`

Spanning several areas → omit the scope or use the nearest parent.

## Rules

- English only, imperative verbs (`add`, not `added`)
- Subject ≤ 72 chars, no trailing period
- Body wraps at 72 chars and explains **why**, not what

## Examples

```
feat(core): add stale-safe tap with click-success convergence
fix(config): let platform-specific app path beat generic APP_PATH
test(steps): implement playlist creation scenarios
chore(deps): bump appium-python-client to 4.1
ci: gate emulator job behind lint and unit tests
```
