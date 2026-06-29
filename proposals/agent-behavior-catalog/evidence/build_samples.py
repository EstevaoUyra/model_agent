#!/usr/bin/env python3
"""Phase-1a sampler — build stratified candidate samples for LLM adjudication.

For each behavior signature (from census_detect), collect candidate agents, extract a short
verifiable excerpt around the first match, stratify by parallel-batch-day vs other, and sample up
to N per behavior (oversampling the parallel + early windows the project lead flagged). Writes
evidence/samples/<bid>.jsonl with {bid, path, date, role, model, excerpt}. Adjudication subagents
then label each excerpt true/false-positive — no corpus re-scan needed.

Usage: python3 build_samples.py [N_per_behavior=30]
"""
import json, os, re, sys, random, collections
from census_detect import SIG, narration, PARALLEL_DAYS, MAN, HERE

N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
OUTDIR = os.path.join(HERE, "samples")
os.makedirs(OUTDIR, exist_ok=True)
random.seed(7)


def bid(key):  # "E1a leniency-acquit" -> "E1a"
    return key.split()[0]


def excerpt(text, pat, width=140):
    m = pat.search(text)
    if not m:
        return ""
    a, b = max(0, m.start() - width), m.end() + width
    return re.sub(r"\s+", " ", text[a:b]).strip()


def main():
    rows = [json.loads(l) for l in open(MAN)]
    # one pass: per behavior collect candidates with excerpt + stratum
    cand = {bid(k): [] for k in SIG}
    for r in rows:
        txt = narration(r["path"])
        if not txt:
            continue
        for k, pat in SIG.items():
            if pat.search(txt):
                cand[bid(k)].append(dict(bid=bid(k), path=r["path"], date=r["date"],
                                         role=r["role"], model=r["model"],
                                         stratum="parallel" if r["date"] in PARALLEL_DAYS else "other",
                                         excerpt=excerpt(txt, pat)))
    summary = []
    for b, items in cand.items():
        par = [x for x in items if x["stratum"] == "parallel"]
        oth = [x for x in items if x["stratum"] == "other"]
        # half from each stratum (or all if fewer), to guarantee parallel-window coverage
        take_p = random.sample(par, min(len(par), N // 2))
        take_o = random.sample(oth, min(len(oth), N - len(take_p)))
        sample = take_p + take_o
        random.shuffle(sample)
        with open(os.path.join(OUTDIR, f"{b}.jsonl"), "w") as g:
            for x in sample:
                g.write(json.dumps(x) + "\n")
        summary.append((b, len(items), len(sample), len(take_p)))
    print(f"wrote samples for {len(summary)} behaviors -> {os.path.relpath(OUTDIR, HERE)}/")
    print(f"{'behavior':28s} {'candidates':>10s} {'sampled':>8s} {'from-parallel':>14s}")
    for b, c, s, p in summary:
        print(f"  {b:26s} {c:10d} {s:8d} {p:14d}")


if __name__ == "__main__":
    main()
