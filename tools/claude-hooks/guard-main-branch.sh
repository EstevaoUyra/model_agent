#!/usr/bin/env bash
# PreToolUse(Bash) guardrail — early, friendly block of direct writes to `main`.
#
# This is the ADVISORY layer. The AUTHORITATIVE layer is the repo's git hooks
# (.git/hooks/pre-commit + pre-push), which inspect the real operation and so are
# correct even across worktrees and other tools (Codex, terminal). Because this
# PreToolUse hook only sees the SESSION's cwd branch, it deliberately stays narrow
# to avoid false-positiving on legit worktree work (e.g. a session sitting on
# `main` that pushes a feature branch living in a /tmp worktree):
#
#   A) ALWAYS deny a push whose refspec explicitly targets main (cwd-independent).
#   B) When the command is NOT redirected elsewhere (no `cd`, `git -C`, --git-dir,
#      --work-tree) AND the session cwd is on `main`: deny commit/cherry-pick/
#      revert and a bare push (these would hit main here-and-now).
#   Everything else defers to the git hooks.
#
# Escape hatch (both layers): token ALLOW_MAIN_COMMIT in the command, or env
# ALLOW_MAIN_COMMIT=1. `gh pr merge` is a server-side merge, not a push → fine.
# Fails open: any parse error exits 0 (allow). A real block is exit 2.

payload="$(cat 2>/dev/null)"
cmd="$(printf '%s' "$payload" | python3 -c 'import sys, json
try:
    print(json.load(sys.stdin).get("tool_input", {}).get("command", ""))
except Exception:
    pass' 2>/dev/null)"

[ -z "$cmd" ] && exit 0
case "$cmd" in *git*) ;; *) exit 0 ;; esac
case "$cmd" in *ALLOW_MAIN_COMMIT*) exit 0 ;; esac

deny() { printf '%s\n' "$1" >&2; exit 2; }

# A) Explicit push to main — wrong regardless of where the session sits.
targets_main=0
case "$cmd" in *"origin main"*|*"HEAD:main"*|*":main"*) targets_main=1 ;; esac
case "$cmd" in
  *"git push"*) [ "$targets_main" = 1 ] && deny "🛑 Guardrail: refusing to push 'main'. Push a feature branch and open a PR (gh pr create / gh pr merge are fine). Genuine human-authorized hotfix? Add ALLOW_MAIN_COMMIT." ;;
esac

# Is the command operating somewhere other than the session cwd? Then the cwd
# branch is not a reliable signal — let the git hooks (which see the real target)
# decide.
redirected=0
case "$cmd" in *"cd "*|*" -C "*|*"--git-dir"*|*"--work-tree"*) redirected=1 ;; esac
[ "$redirected" = 1 ] && exit 0

# B) Naive direct COMMIT while standing on main in THIS directory. (Pushes are
# left entirely to the git pre-push hook, which inspects the real refspec and so
# never false-positives on explicit non-main pushes like `--delete wip/x` or
# `push origin feat/x` issued from a main cwd.)
branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
if [ "$branch" = "main" ]; then
  case "$cmd" in
    *"git commit"*|*"git cherry-pick"*|*"git revert"*)
      deny "🛑 Guardrail: you are on 'main'. Branch first (git checkout -b <name>), commit there, open a PR (gh pr create). Genuine human-authorized hotfix? Add ALLOW_MAIN_COMMIT." ;;
  esac
fi
exit 0
