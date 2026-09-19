---
name: Commit
description: 'Read the staged changes and generate a <type>(<scope>): <subject> commit message per .claude/rules/git-commit.md; commit after confirmation. Commit only — never push.'
argument-hint: "[optional: type/scope hint, e.g. fix docs, or a one-line message]"
---

**Goal**: turn the currently staged changes into one commit that follows
`.claude/rules/git-commit.md`.

**Steps**

1. Check what's staged: `git diff --cached --stat`.
   - **Nothing staged**: run `git status --short`, then ask the user —
     "stage everything (`git add -A`)" / "stage a subset (name the paths)" /
     "cancel". Cancel ends here.
   - Something staged: continue (never sweep unstaged changes in uninvited).

2. Read the full staged diff: `git diff --cached`. Analyze the **nature** of
   the change (what behavior changed and why) — not just the file names.

3. Pick `<type>` (one, per git-commit.md): `feat` / `fix` / `refactor` /
   `test` / `chore` / `docs` / `ci`.

4. Pick `<scope>`: the smallest meaningful area (`core` / `screens` / `steps` /
   `features` / `api` / `config` / `rules` / `ci` ...). Multiple areas → omit
   or use the nearest parent.

5. Write `<subject>`: English, imperative, ≤ 72 chars, no period. If the user
   passed an argument, honor its type/scope hint or message intent.

6. Body only when the motivation isn't obvious — explain **why**, wrap at 72
   chars. Obvious small changes get subject-only.

7. Confirm the full message with the user: "commit as is" / "let me edit" /
   "cancel". Cancel = no commit.

8. Commit via a temp file: `git commit -F <file>` (avoids multiline/escaping
   issues), then report with `git log -1 --stat`.

9. Done. **Never `git push`** — pushing is a separate, explicit request.

**Principles**
- One semantically cohesive commit at a time; if the staged diff clearly mixes
  unrelated topics, suggest splitting before continuing.
- Co-author trailers follow the repo's git convention; this command doesn't add
  its own.
