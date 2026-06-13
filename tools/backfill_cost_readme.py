#!/usr/bin/env python3
"""One-off backfill: insert the "## Reproduction cost" section into each recoverable model's README.

Idempotent. For every model with recoverable full-pass transcripts, regenerate the cost section
(via repro_cost.markdown) and splice it into models/<name>/README.md as the FINAL section,
replacing any existing "## Reproduction cost" block. Does NOT touch git — prints the list of
changed READMEs so the caller can commit per-submodule.

    python3 tools/backfill_cost_readme.py            # list recoverable models (dry)
    python3 tools/backfill_cost_readme.py --write     # write the READMEs
"""
import os, sys, re
import repro_cost as rc

HEADER = "## Reproduction cost"


def splice(readme_text, section):
    """Replace an existing '## Reproduction cost' block (to next top-level ## or EOF), else append."""
    section = section.rstrip() + "\n"
    idx = readme_text.find(HEADER)
    if idx == -1:
        sep = "" if readme_text.endswith("\n\n") else ("\n" if readme_text.endswith("\n") else "\n\n")
        return readme_text.rstrip("\n") + "\n\n" + section
    # find the next top-level "## " header after this one
    rest = readme_text[idx + len(HEADER):]
    m = re.search(r"\n## ", rest)
    tail = rest[m.start():] if m else ""
    return readme_text[:idx] + section.rstrip("\n") + ("\n" + tail.lstrip("\n") if tail else "\n")


def main():
    write = "--write" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    models = rc.scan()
    changed = []
    for model, rec in sorted(models.items()):
        if not rec["agents"]:
            continue
        if only and model not in only:
            continue
        readme = os.path.join(rc.REPO_ROOT, "models", model, "README.md")
        if not os.path.isfile(readme):
            print(f"SKIP  {model}: no README.md")
            continue
        section = rc.markdown(model, rec)
        old = open(readme).read()
        new = splice(old, section)
        if new == old:
            print(f"same  {model}")
            continue
        changed.append(model)
        if write:
            open(readme, "w").write(new)
            print(f"WROTE {model}  (${rc.cost(rec['usage']):,.2f})")
        else:
            print(f"would write {model}  (${rc.cost(rec['usage']):,.2f})")
    print(f"\n{len(changed)} README(s) {'written' if write else 'to write'}")
    # emit the list for the git driver
    print("MODELS:" + " ".join(changed))


if __name__ == "__main__":
    main()
