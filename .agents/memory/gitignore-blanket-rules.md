---
name: Gitignore blanket rules can hide legitimate project files
description: When a .gitignore has broad rules added for one scaffold (e.g. all "package.json", all ".github/"), a later legitimate subproject with the same filename gets silently un-tracked too.
---

In a Python data-science repo that also had an unrelated Replit pnpm-workspace
scaffold sitting alongside it, an earlier cleanup pass added blanket
`.gitignore` rules like `package.json` and `.github/` to hide that scaffold's
files. Those rules are name/path based, not scaffold-based — they silently
ignored a legitimate `dashboard/frontend/package.json` and a legitimate
`.github/workflows/unittests.yml` added months later for the *actual* project.

**Why:** `git add -A` gives no error for ignored paths by default, so the
files just don't show up in `git status`, and it's easy to not notice they
were never committed until much later (or never).

**How to apply:** When adding a new file whose name matches a broad ignore
pattern that was written for a *different* purpose, either scope the ignore
rule to the specific directory (`/package.json` instead of `package.json`),
or add a `!/path/to/new/legit/file` negation exception right after it. Always
double check `git status --short` after `git add -A` lists everything you
expect — if an expected new file is missing, run
`git check-ignore -v <path>` to find the exact rule blocking it.
