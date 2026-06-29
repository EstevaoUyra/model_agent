#!/usr/bin/env python3
"""Phase-0 census detector — deterministic high-recall candidate scan for the agent-behavior catalog.

NOT a counter of true instances: it counts CANDIDATE agents whose narration matches a behavior's
high-recall signature (seeded from the thread's verified quotes + vocabulary). Candidates overcount
(a word can appear in a legitimate context) and slightly undercount (alternate phrasings). Phase 1
(LLM adjudication of a stratified sample) turns candidate-rate -> true-rate × precision with a CI.

What this gives cheaply, with no LLM: per behavior, the DENOMINATOR SHAPE — candidate counts by
date / role / model — which reveals the un-referenced volume and the parallel-batch concentration.

Reads each transcript ONCE, applies ALL signatures. Output: evidence/census-phase0.md + stdout.
Usage: python3 census_detect.py
"""
import json, re, os, collections, glob

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = os.path.join(HERE, "corpus-snapshot")
MAN = os.path.join(HERE, "manifest.jsonl")
PARALLEL_DAYS = {"2026-06-02", "2026-06-03", "2026-06-12", "2026-06-13"}  # big concurrent-batch days

# High-recall signatures (case-insensitive). Pattern-detectable threads only; relational/process
# threads (C6/C7/M5/M6/S1/S3/S4/D1-3/T1/T3/U1) have no verbal signature -> not censusable here.
SIG = {
 "E1a leniency-acquit":      r"genuine[_ ]divergence|defensible disambiguation|disclosed (illustrative|constructed)|illustrative[- ]?(parameter|constructed|artifact)",
 "E1b perceptual-blindspot": r"plateau|interior peak|monotonic|leftmost (visible )?point",
 "E2 leniency-drift":        r"grading own homework|tripwire|toward (the )?green|flipped .*(must[- ]?pass|red)|drift(ing)?",
 "E3 tool-rubber-stamp":     r"overlay (tracks|looks)|adversarial(ly)? (re)?check|trust the tool|rubber[- ]?stamp",
 "E5 self-certification":    r"all .*tests pass|audited:\s*false|correct,? faithful state|green.*=>?\s*done|no implementation change needed",
 "E6 reads-expected-shape":  r"inverted[- ]?u|interior peak|monotonically decreasing|peaks? at (intermediate|c=0)",
 "E7 wrong-absolute-scale":  r"shape[- ]?faithful|scale .*(off|wrong)|absolute magnitude|fit[- ]?scaled axis|~?\d+ ?[x×] (too|off)",
 "E8 normalization-override":r"per[- ]?panel .*normal|normaliz.*(1\.0|max)|shared scale|pin.*(each|own) max",
 "E9 illustrative-escape":   r"illustrative[- ]?not[- ]?reproduced|may never show plain green|not[- ]?reproduced|descope",
 "E10 false-paper-attrib":   r"paper[_ ]?issue|resolved[- ]?by[- ]?paper|suspected[- ]?paper|paper underdetermin|laundered contradiction|retracted",
 "E11 magnitude-in-testcode":r"audited:\s*false|ref[- ]?impl|threshold .*(test|code)|binding .*threshold",
 "E12 stale-artifact":       r"stale (figure|render|png|artifact)|never regenerat|out[- ]?of[- ]?date render|regenerate before",
 "G1 confabulate-fabricate": r"confabulat|invent(ed)? .*(mechanism|claim)|fabricat|unsupported (inequality|claim)|falsely[- ]?cited",
 "G2 stub-drew-the-answer":  r"drew the answer|hand[- ]?(built|enter)|constructed (result|stub)|frozen stub|tautolog",
 "X1 over-route-human":      r"route.*human|human (decision|only)|open_for_human|DECISION \(human|needs a human",
 "X2 ladder-under-walked":   r"rung[- ]?\d|escalation ladder|resolvable .*human|cap[- ]?artifact",
 "X3 misroute-tune-knob":    r"suppressive_drive_gain|tune (a |the )?gain|per[- ]?(figure|panel) gain|gain (bumped|4|12|16)",
 "T2 matplotlib-substrate":  r"matplotlib|no module named|\.venv|framework (module )?(isn'?t|not) installed",
 "T5 law-of-instrument":     r"curve tracer .*(dictionary|filter)|wrong tool|mode[- ]?[12]|no[- ]?tool|tool[- ]?misuse",
}
SIG = {k: re.compile(v, re.I) for k, v in SIG.items()}


def narration(path):
    full = os.path.join(SNAP, path)
    if not os.path.exists(full):
        return ""
    out = []
    for l in open(full, errors="replace"):
        try:
            d = json.loads(l)
        except Exception:
            continue
        m = d.get("message")
        if isinstance(m, dict):
            c = m.get("content")
            if isinstance(c, list):
                for b in c:
                    if isinstance(b, dict) and b.get("type") == "text":
                        out.append(b.get("text", ""))
    return "\n".join(out)


def referenced_agents():
    refs = set()
    for f in glob.glob(os.path.join(HERE, "*.quotes.jsonl")):
        for l in open(f):
            try:
                refs.add(json.loads(l)["path"])
            except Exception:
                pass
    return refs


def main():
    rows = [json.loads(l) for l in open(MAN)]
    refs = referenced_agents()
    # per behavior: set of candidate agent paths; and per-stratum counters
    hits = {k: set() for k in SIG}
    byday = {k: collections.Counter() for k in SIG}
    bymodel = {k: set() for k in SIG}
    byrole = {k: collections.Counter() for k in SIG}
    for r in rows:
        txt = narration(r["path"])
        if not txt:
            continue
        for k, pat in SIG.items():
            if pat.search(txt):
                hits[k].add(r["path"])
                byday[k][r["date"]] += 1
                if r["model"]:
                    bymodel[k].add(r["model"])
                byrole[k][r["role"]] += 1

    lines = ["# Phase-0 census — deterministic candidate scan (NOT true counts)\n",
             "Candidate = an agent whose narration matches a high-recall signature; overcounts "
             "(needs Phase-1 adjudication for precision). Reveals denominator shape + concurrency "
             "concentration. Generated by `census_detect.py` over all 2062 transcripts.\n",
             f"Referenced agents across all current ledgers: **{len(refs)}** (of 2062). "
             "Everything below beyond that is un-referenced candidate volume.\n",
             "| Behavior | cand. agents | distinct models | un-ref'd | parallel-day share | top roles |",
             "|---|---:|---:|---:|---|---|"]
    total_cand = set()
    for k in SIG:
        ag = hits[k]
        total_cand |= ag
        unref = len(ag - refs)
        pday = sum(byday[k][d] for d in PARALLEL_DAYS)
        tot = sum(byday[k].values())
        pshare = f"{100*pday//tot}%" if tot else "-"
        roles = ", ".join(f"{r}:{c}" for r, c in byrole[k].most_common(3))
        lines.append(f"| {k} | {len(ag)} | {len(bymodel[k])} | {unref} | {pshare} ({pday}/{tot}) | {roles} |")
    lines += ["",
              f"**Union of candidate agents across all behaviors: {len(total_cand)} of 2062 "
              f"({100*len(total_cand)//2062}%).** Referenced so far: {len(refs)}. "
              f"Un-referenced candidate agents: ~{len(total_cand - refs)}.",
              "",
              "## Per-behavior date histograms (concurrency check)"]
    for k in SIG:
        hist = " ".join(f"{d[5:]}:{byday[k][d]}" for d in sorted(byday[k]))
        lines.append(f"- **{k}** — {hist}")
    out = os.path.join(HERE, "census-phase0.md")
    open(out, "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[:6]))
    print(f"\n... full table + histograms -> {os.path.relpath(out, HERE)}")
    print(f"union candidates {len(total_cand)} / 2062 | referenced {len(refs)} | "
          f"un-referenced ~{len(total_cand - refs)}")


if __name__ == "__main__":
    main()
