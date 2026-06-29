#!/usr/bin/env python3
"""Mechanical quote verifier for the agent-behavior catalog.

Every quote a mining subagent promotes into an entry must appear in a JSONL ledger
(`evidence/<thread>.quotes.jsonl`) as `{"id","path","quote"}`. This harness checks each `quote`
verbatim against its source transcript under `evidence/corpus-snapshot/`, so verification is a
single script run instead of the orchestrator re-reading bundles by hand (which gets rubber-stamped
— see memory `vlm-eye-is-arbiter-over-tools`, `faithfulness-critics-want-to-find-issues`).

Matching: the quote must be a substring of the transcript's concatenated message TEXT (assistant
narration + any text blocks), after whitespace normalization (collapse runs of whitespace; the
bundle/manifest collapse newlines, so source text is normalized the same way). Case-sensitive by
default. Also reports a uniqueness warning if the quote appears in >1 transcript across the ledger's
files (distinctive substrings should be unique), but uniqueness is a warning, not a failure.

Exit code: 0 if every ledger line matches its source; 1 otherwise (CI/gate-friendly).

Usage:
  python3 verify_quotes.py                      # verify all evidence/*.quotes.jsonl
  python3 verify_quotes.py E1                   # verify evidence/E1.quotes.jsonl
  python3 verify_quotes.py path/to/x.quotes.jsonl ...
"""
import json, sys, os, re, glob

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = os.path.join(HERE, "corpus-snapshot")
_WS = re.compile(r"\s+")


def norm(s: str) -> str:
    return _WS.sub(" ", s).strip()


def transcript_text(path: str) -> str:
    """Concatenated message text (any role) from a .jsonl transcript, whitespace-normalized."""
    full = os.path.join(SNAP, path)
    if not os.path.exists(full):
        return None  # signals missing file
    chunks = []
    for line in open(full, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        m = d.get("message")
        if not isinstance(m, dict):
            continue
        c = m.get("content")
        if isinstance(c, str):
            chunks.append(c)
        elif isinstance(c, list):
            for b in c:
                if isinstance(b, dict) and b.get("type") in ("text", "thinking"):
                    chunks.append(b.get("text") or b.get("thinking") or "")
    return norm("\n".join(chunks))


def resolve_ledgers(args):
    if not args:
        return sorted(glob.glob(os.path.join(HERE, "*.quotes.jsonl")))
    out = []
    for a in args:
        if os.path.exists(a):
            out.append(a)
        elif os.path.exists(os.path.join(HERE, f"{a}.quotes.jsonl")):
            out.append(os.path.join(HERE, f"{a}.quotes.jsonl"))
        else:
            print(f"  ! no ledger found for '{a}'")
    return out


def main():
    ledgers = resolve_ledgers(sys.argv[1:])
    if not ledgers:
        print("no ledgers to verify (expected evidence/*.quotes.jsonl)")
        return 0
    cache = {}
    total = ok = 0
    failures = []
    seen = {}  # normalized quote -> set(paths) for uniqueness check
    for led in ledgers:
        print(f"\n== {os.path.relpath(led, HERE)} ==")
        for ln, raw in enumerate(open(led), 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                rec = json.loads(raw)
            except Exception:
                failures.append((led, ln, "BAD JSON", raw[:60]))
                print(f"  ✗ line {ln}: bad JSON")
                continue
            total += 1
            path, quote, qid = rec.get("path"), rec.get("quote"), rec.get("id", "?")
            if path not in cache:
                cache[path] = transcript_text(path)
            text = cache[path]
            if text is None:
                failures.append((led, ln, "MISSING FILE", path))
                print(f"  ✗ [{qid}] missing source: {path}")
                continue
            nq = norm(quote or "")
            if nq and nq in text:
                ok += 1
                seen.setdefault(nq, set()).add(path)
                print(f"  ✓ [{qid}] {nq[:64]}")
            else:
                failures.append((led, ln, "NOT FOUND", f"[{qid}] {nq[:60]}"))
                print(f"  ✗ [{qid}] NOT in source {path}: {nq[:60]}")
    dupes = {q: ps for q, ps in seen.items() if len(ps) > 1}
    print(f"\n{'='*50}\nverified {ok}/{total} quotes across {len(ledgers)} ledger(s)")
    if dupes:
        print(f"⚠ {len(dupes)} quote(s) matched >1 transcript (not unique) — consider a longer substring")
    if failures:
        print(f"✗ {len(failures)} FAILURE(S):")
        for led, ln, why, what in failures:
            print(f"   {os.path.relpath(led, HERE)}:{ln}  {why}  {what}")
        return 1
    print("✓ all quotes verified verbatim against corpus-snapshot")
    return 0


if __name__ == "__main__":
    sys.exit(main())
