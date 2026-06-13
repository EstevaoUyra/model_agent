#!/usr/bin/env python3
"""Estimate the API token cost of reproducing a model from the full-pass workflow transcripts.

Every full-pass run spawns a fleet of subagents (extract / digitize / audit / implement / …),
each of which is one Claude conversation logged as a `.jsonl` transcript under the Claude Code
project dir. This script recovers those transcripts, sums the billed tokens per agent and per
token type, and prices them at STANDARD Claude Opus 4.8 API rates.

What it counts
--------------
- Scope: agents under `<project>/*/subagents/workflows/wf_*/agent-*.jsonl` — i.e. agents spawned
  by a `full-pass` workflow run. One `wf_<id>` dir == one run (one model, one from-mode). A model's
  cost is the SUM over every run that targeted it (the first extract/build pass + any later fix
  passes). One-off directed-resolver agents spawned outside a workflow are NOT counted (they are a
  rare minority); the figure is "the cost of the full-pass runs", which is the dominant cost.
- De-dup: streaming writes the same assistant message many times as the output grows. Messages are
  collapsed by their API `message.id`, taking the MAX `output_tokens` (the final cumulative) and the
  (constant) input / cache-write / cache-read for that message. Agents are de-duped by `agentId`, so
  a run resumed from cache (which replays finished agents) is never double-counted.
- Model attribution: each agent's prompt embeds the model path (`models/<name>`) via the workflow's
  SK() helper; a run's model is the most common such path across its agents.

Pricing (standard Claude Opus 4.8, $/1M tokens)
-----------------------------------------------
    input            $5.00     output           $25.00
    cache read       $0.50     (0.10x input)
    cache write 5m   $6.25     (1.25x input)
    cache write 1h   $10.00    (2.00x input)
The `[1m]` implementer is the same per-token rate (a context-window selector, not a price tier).

Usage
-----
    python3 tools/repro_cost.py                      # summary table: every recoverable model
    python3 tools/repro_cost.py models/flash_hogan_1985            # human breakdown for one model
    python3 tools/repro_cost.py models/flash_hogan_1985 --markdown # the README "Reproduction cost" section
    python3 tools/repro_cost.py models/flash_hogan_1985 --json     # machine-readable

The finalize step of full-pass.js calls `--markdown` and pastes the output as the README's final
section, so every reproduced model carries its own measured cost.
"""
import sys, json, glob, os, re
from collections import defaultdict

PROJECT_DIR = os.path.expanduser(
    "~/.claude/projects/-Users-estevaouyra-dev-model-agent")
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# standard Opus 4.8 rates, $ per 1M tokens
RATE = {"input": 5.0, "output": 25.0, "cache_read": 0.50,
        "cache_write_5m": 6.25, "cache_write_1h": 10.0}

SKILL_RE = re.compile(r"skills/([a-z0-9-]+)/SKILL\.md")
MODEL_RE = re.compile(r"models/([a-z0-9_]+)")


def _first_user_text(lines):
    for l in lines:
        m = l.get("message", {})
        if isinstance(m, dict) and m.get("role") == "user":
            c = m.get("content")
            return c if isinstance(c, str) else json.dumps(c)
    return ""


# keyword → role for the older workflow generation that used inline prompts (no SK() skill ref).
# Ordered: first match wins. Keeps the "by agent role" table meaningful across both generations.
LEGACY_ROLES = [
    ("LAND THE RESULT IN ITS OWN REPO", "finalize"),
    ("DOCUMENTING the reproduced model", "finalize"),
    ("REFRESHING the README", "update-state"),
    ("ARTICLE EXTRACTOR", "extract-spec"),
    ("Phase-A contract editor", "paper-fix"),
    ("ADVERSARIAL SPEC-REVIEW", "audit-spec"),
    ("PHASE-B IMPLEMENTATION", "implement"),
    ("VLM VERIFIER", "vlm-verify"),
    ("visual-faithfulness auditor", "audit-faithfulness"),
    ("REGENERATE figures", "render-figures"),
    ("Finalize", "finalize"),
]


def _role(prompt):
    m = SKILL_RE.search(prompt)
    if m:
        return m.group(1)
    for kw, role in LEGACY_ROLES:
        if kw in prompt:
            return role
    return "other"


def _agent_usage(lines):
    """Collapse streaming deltas by message id → per-type token totals for one agent."""
    by_msg = {}  # msg_id -> dict
    for l in lines:
        m = l.get("message", {})
        if not isinstance(m, dict):
            continue
        u = m.get("usage")
        if not u:
            continue
        mid = m.get("id") or l.get("uuid")
        cc = u.get("cache_creation") or {}
        rec = by_msg.setdefault(mid, {
            "input": u.get("input_tokens", 0),
            "cache_read": u.get("cache_read_input_tokens", 0),
            "cache_write_5m": cc.get("ephemeral_5m_input_tokens",
                                     u.get("cache_creation_input_tokens", 0)),
            "cache_write_1h": cc.get("ephemeral_1h_input_tokens", 0),
            "output": 0,
        })
        rec["output"] = max(rec["output"], u.get("output_tokens", 0))
    tot = defaultdict(int)
    for rec in by_msg.values():
        for k, v in rec.items():
            tot[k] += v
    return dict(tot)


def scan():
    """Return {model: {runs: {wf_id: {...}}, agents: {agentId: {role, run, usage}}}}."""
    models = defaultdict(lambda: {"runs": defaultdict(lambda: {"agents": 0, "usage": defaultdict(int)}),
                                  "agents": {},
                                  "roles": defaultdict(lambda: {"n": 0, "usage": defaultdict(int)}),
                                  "usage": defaultdict(int)})
    seen_agents = set()
    for wf_dir in glob.glob(os.path.join(PROJECT_DIR, "*", "subagents", "workflows", "wf_*")):
        run_id = os.path.basename(wf_dir)
        files = glob.glob(os.path.join(wf_dir, "agent-*.jsonl"))
        if not files:
            continue
        # first pass: determine this run's model (most common models/<name> across agents)
        votes = defaultdict(int)
        parsed = {}
        for f in files:
            try:
                lines = [json.loads(x) for x in open(f) if x.strip()]
            except Exception:
                continue
            parsed[f] = lines
            mm = MODEL_RE.search(_first_user_text(lines))
            if mm:
                votes[mm.group(1)] += 1
        # keep only real model dirs — drops false matches (e.g. a session-id path in a prompt)
        votes = {m: v for m, v in votes.items()
                 if os.path.isdir(os.path.join(REPO_ROOT, "models", m))}
        if not votes:
            continue
        model = max(votes, key=votes.get)
        rec = models[model]
        for f, lines in parsed.items():
            agent_id = os.path.basename(f)[len("agent-"):-len(".jsonl")]
            if agent_id in seen_agents:      # resume-replay safety: count each agent once
                continue
            seen_agents.add(agent_id)
            usage = _agent_usage(lines)
            if not usage:
                continue
            role = _role(_first_user_text(lines))
            rec["agents"][agent_id] = {"role": role, "run": run_id, "usage": usage}
            r = rec["runs"][run_id]
            r["agents"] += 1
            rl = rec["roles"][role]
            rl["n"] += 1
            for k, v in usage.items():
                r["usage"][k] += v
                rl["usage"][k] += v
                rec["usage"][k] += v
    return models


def cost(usage):
    return sum(usage.get(k, 0) / 1e6 * RATE[k] for k in RATE)


def _fmt_tok(n):
    if n >= 1e6:
        return f"{n/1e6:.1f}M"
    if n >= 1e3:
        return f"{n/1e3:.0f}k"
    return str(n)


# canonical token-type display order
ORDER = ["input", "cache_write_5m", "cache_write_1h", "cache_read", "output"]
LABEL = {"input": "input", "cache_write_5m": "cache write 5m",
         "cache_write_1h": "cache write 1h", "cache_read": "cache read", "output": "output"}


def markdown(model, rec):
    u, n_agents, n_runs = rec["usage"], len(rec["agents"]), len(rec["runs"])
    total = cost(u)
    out = []
    out.append("## Reproduction cost")
    out.append("")
    out.append(f"Estimated at **standard Claude Opus 4.8 API rates** "
               f"($5 / $25 per 1M input/output; cache read $0.50/1M, cache write $6.25/1M) "
               f"from this model's full-pass workflow agent transcripts — summed across all "
               f"{n_runs} run(s) (initial pass + any later fixes).")
    out.append("")
    out.append(f"**Estimated total: ${total:,.2f}** "
               f"— {n_runs} run(s), {n_agents} agents, "
               f"{_fmt_tok(sum(u.get(k,0) for k in RATE))} tokens.")
    out.append("")
    out.append("### By token type")
    out.append("")
    out.append("| token type | tokens | $/1M | cost |")
    out.append("|---|--:|--:|--:|")
    for k in ORDER:
        t = u.get(k, 0)
        if t == 0 and k == "cache_write_1h":
            continue
        out.append(f"| {LABEL[k]} | {t:,} | {RATE[k]:.2f} | ${t/1e6*RATE[k]:,.2f} |")
    out.append(f"| **total** | **{sum(u.get(k,0) for k in RATE):,}** | | **${total:,.2f}** |")
    out.append("")
    out.append("### By agent role")
    out.append("")
    out.append("| agent | runs× | input | cache-write | cache-read | output | cost |")
    out.append("|---|--:|--:|--:|--:|--:|--:|")
    for role, rl in sorted(rec["roles"].items(), key=lambda kv: -cost(kv[1]["usage"])):
        ru = rl["usage"]
        cw = ru.get("cache_write_5m", 0) + ru.get("cache_write_1h", 0)
        out.append(f"| {role} | {rl['n']} | {_fmt_tok(ru.get('input',0))} | "
                   f"{_fmt_tok(cw)} | {_fmt_tok(ru.get('cache_read',0))} | "
                   f"{_fmt_tok(ru.get('output',0))} | ${cost(ru):,.2f} |")
    out.append("")
    out.append(f"<sub>Measured from agent transcripts via `tools/repro_cost.py`. "
               f"Messages de-duped by API id (max cumulative output); agents de-duped by id "
               f"(cache-replayed resumes not double-counted). The in-flight report phase of the "
               f"latest run may be slightly undercounted.</sub>")
    return "\n".join(out)


def human(model, rec):
    print(markdown(model, rec))
    print("\n--- per-run ---")
    for run_id, r in sorted(rec["runs"].items()):
        print(f"  {run_id}: {r['agents']:>3} agents  ${cost(r['usage']):>8,.2f}  "
              f"({_fmt_tok(sum(r['usage'].get(k,0) for k in RATE))} tok)")


def summary(models):
    print(f"{'model':<34}{'runs':>5}{'agents':>8}{'tokens':>10}{'cost ($)':>12}")
    print("-" * 69)
    rows = sorted(models.items(), key=lambda kv: -cost(kv[1]["usage"]))
    gt = ga = gr = 0.0
    for model, rec in rows:
        tok = sum(rec["usage"].get(k, 0) for k in RATE)
        c = cost(rec["usage"])
        gt += c; ga += len(rec["agents"]); gr += len(rec["runs"])
        print(f"{model:<34}{len(rec['runs']):>5}{len(rec['agents']):>8}{_fmt_tok(tok):>10}{c:>12,.2f}")
    print("-" * 69)
    print(f"{'TOTAL':<34}{int(gr):>5}{int(ga):>8}{'':>10}{gt:>12,.2f}")


def main():
    argv = sys.argv[1:]
    fmt = "human"
    for flag in ("--markdown", "--json", "--summary"):
        if flag in argv:
            fmt = flag[2:]
            argv.remove(flag)
    model = argv[0].replace("models/", "").rstrip("/") if argv else None
    models = scan()
    if model is None or fmt == "summary":
        summary(models)
        return
    rec = models.get(model)
    if not rec or not rec["agents"]:
        if fmt == "markdown":
            # no recoverable data → emit nothing (finisher skips the section)
            return
        if fmt == "json":
            print(json.dumps({"model": model, "recoverable": False}))
            return
        print(f"No recoverable full-pass transcripts for '{model}'.", file=sys.stderr)
        sys.exit(1)
    if fmt == "markdown":
        print(markdown(model, rec))
    elif fmt == "json":
        print(json.dumps({
            "model": model, "recoverable": True,
            "runs": len(rec["runs"]), "agents": len(rec["agents"]),
            "total_cost_usd": round(cost(rec["usage"]), 2),
            "by_type": {k: rec["usage"].get(k, 0) for k in RATE},
            "by_role": {role: {"n": rl["n"], "cost_usd": round(cost(rl["usage"]), 2),
                               "usage": dict(rl["usage"])}
                        for role, rl in rec["roles"].items()},
        }, indent=2))
    else:
        human(model, rec)


if __name__ == "__main__":
    main()
