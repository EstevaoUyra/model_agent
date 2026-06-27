# tools/claude-hooks/

Claude Code **harness** hooks (PreToolUse/etc.), versioned here so they're
reproducible. These are distinct from the repo's **git** hooks in
[`tools/hooks/`](../hooks/) — different mechanism, different layer.

## The two-layer main-branch guard

Direct writes to `main` are blocked by **two complementary layers** (see WORKFLOW.md §9):

1. **Advisory — `guard-main-branch.sh` (this dir).** A Claude Code `PreToolUse(Bash)`
   hook: it inspects the *command string* before it runs and blocks an obvious direct
   commit/push to `main`, with a friendly message, before any work happens. Because it
   only sees the **session cwd branch**, it stays deliberately narrow (it always denies an
   explicit `push … main`, but defers `cd`/`git -C`/worktree-redirected commands to the
   git hooks). Escape hatch: the token `ALLOW_MAIN_COMMIT` in the command, or env
   `ALLOW_MAIN_COMMIT=1` (needed e.g. to seed a brand-new repo's `main`).

2. **Authoritative — the git hooks in [`tools/hooks/`](../hooks/)** (`pre-commit` +
   `pre-push`, installed via `git config core.hooksPath tools/hooks`). They inspect the
   **real operation/refspec**, so they're correct even across worktrees and other tools
   (terminal, Codex). `pre-push` is the authoritative push guard this advisory hook's
   header refers to.

The advisory layer is "fail-friendly + early"; the authoritative layer is "correct +
unbypassable-by-accident". You want both.

## Installing the advisory hook (per machine)

This snapshot is the source of truth; the **live** copy a session actually runs is
machine-local at `~/.claude/hooks/guard-main-branch.sh`, wired in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash",
        "hooks": [ { "type": "command",
                     "command": "/absolute/path/to/guard-main-branch.sh" } ] }
    ]
  }
}
```

On a fresh machine, copy this script to `~/.claude/hooks/` (or point the `command` at this
repo copy) and add the wiring above. It is intentionally **not** wired into the repo's
`.claude/settings.json` — doing so would double-fire alongside an existing user-global
hook. Refresh this snapshot after editing the live hook:

```sh
cp ~/.claude/hooks/guard-main-branch.sh tools/claude-hooks/guard-main-branch.sh
```
