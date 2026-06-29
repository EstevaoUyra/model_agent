#!/usr/bin/env python3
"""Build the deterministic-slice manifest for the agent-behavior catalog (Stage-1 map spine).

Walks the workflow sub-agent transcripts under the Claude Code project dir and emits one row per
agent with the fields the catalog's mining protocol (Pass 1/2/3) slices on. This is the reproducible
replacement for the ephemeral session-scratchpad manifest — commit the OUTPUT (manifest.jsonl) AND
this script so the map's spine is rebuildable and the entry-points don't rot.

Fields per row:
  path, wf, agentId, ts, date, branch, role, model (neuroscience target paper),
  claude_model (the LLM that ran — closes the model-version confound), narr_tok

Role attribution: from `skills/<name>` in the agent's first user prompt, falling back to known
role keywords. ~24% land as "unknown" (older inline-prompt agents) — treat that as a sampled
stratum, NOT as complete coverage. (Critic finding, 2026-06-29.)

Usage:
  python3 build_manifest.py            # writes manifest.jsonl next to this script
  python3 build_manifest.py --summary  # also print role/date/claude_model distributions
"""
import json, glob, re, os, sys, collections

PROJECT_DIR = os.path.expanduser("~/.claude/projects/-Users-estevaouyra-dev-model-agent")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manifest.jsonl")

SKILL = re.compile(r'skills/([a-z0-9\-_]+)')
ROLE_KW = re.compile(r'\b(extract-figure|digitize-figure|audit-digitization|audit-faithfulness|'
                     r'test-faithfulness|compare-figure|extract-spec|audit-spec|author-tests|'
                     r'audit-tests|run-tests|audit-process|implement|finalize|update-state|'
                     r'acquire-sources)\b')
MODEL = re.compile(r'models/([a-z0-9_]+)')


def build():
    files = glob.glob(os.path.join(PROJECT_DIR, "*/subagents/workflows/wf_*/agent-*.jsonl"))
    rows = []
    for f in files:
        agentId = ts = branch = None
        narr_tok = 0
        first_prompt = ""
        claude_models = collections.Counter()
        for l in open(f):
            try:
                d = json.loads(l)
            except Exception:
                continue
            agentId = agentId or d.get("agentId")
            ts = ts or d.get("timestamp")
            branch = branch or d.get("gitBranch")
            m = d.get("message")
            if not isinstance(m, dict):
                continue
            if m.get("role") == "user" and not first_prompt:
                c = m.get("content")
                if isinstance(c, str):
                    first_prompt = c
                elif isinstance(c, list):
                    first_prompt = " ".join(b.get("text", "") for b in c
                                            if isinstance(b, dict) and b.get("type") == "text")
            if m.get("role") == "assistant":
                if m.get("model"):
                    claude_models[m["model"]] += 1
                for b in m.get("content", []):
                    if isinstance(b, dict) and b.get("type") == "text":
                        narr_tok += len(b.get("text", "")) // 4
        sm = SKILL.search(first_prompt)
        if sm:
            role = sm.group(1)
        else:
            km = ROLE_KW.search(first_prompt)
            role = km.group(1) if km else "unknown"
        mm = MODEL.search(first_prompt)
        wf = re.search(r'wf_[0-9a-f]+', f)
        rows.append(dict(
            path=os.path.relpath(f, PROJECT_DIR), wf=wf.group(0) if wf else None,
            agentId=agentId, ts=ts, date=(ts or "")[:10], branch=branch, role=role,
            model=mm.group(1) if mm else None,
            claude_model=(claude_models.most_common(1)[0][0] if claude_models else None),
            narr_tok=narr_tok))
    return rows


def main():
    rows = build()
    with open(OUT, "w") as g:
        for r in rows:
            g.write(json.dumps(r) + "\n")
    print(f"wrote {len(rows)} rows -> {OUT}")
    print(f"total narration tokens: {sum(r['narr_tok'] for r in rows):,}")
    if "--summary" in sys.argv:
        print("\nrole:", dict(collections.Counter(r['role'] for r in rows).most_common()))
        print("\nclaude_model:", dict(collections.Counter(r['claude_model'] for r in rows)))


if __name__ == "__main__":
    main()
