---
name: git-pr
description: Pull Request title and description format for this project
---

# Pull Request Format

## Title

Same format as the commit subject:

```
<type>(<scope>): <subject>
```

Example: `feat(screens): add player screen with queue management`

## Description Template

```markdown
## What
<!-- What this PR does, one to three sentences -->

## Why
<!-- Motivation; which requirement or problem it addresses -->

## Code Changes
<!-- Key changes when useful, format: `path` — description -->
- `path/to/file`: description

## Related Tickets
<!-- ticket id, if any -->

## Test Plan
- [ ]
- [ ]
```

## Rules

- **What** describes the change itself, without repeating the title
- **Why** gives the motivation; link tickets or discussion when relevant
- **Code Changes** lists meaningful code changes (config/docs-only PRs may omit)
- **Test Plan** gives reviewers the verification steps (commands, platform,
  device); for automation PRs include the exact pytest subset that was run
- Omit sections that don't apply
