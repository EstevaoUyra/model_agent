# Evidence layer — agent-behavior catalog

Durable, verifiable backing for the catalog (see `../INDEX.md`). The catalog's honesty claim
("quotes verified verbatim against source") is only meaningful if the source survives — so the
primary corpus is snapshotted here, out from under Claude Code's rotation of `~/.claude`.

| Item | What | Tracked? |
|------|------|----------|
| `manifest.jsonl` | 2062 rows, one per workflow subagent: `path, wf, agentId, ts, date, branch, role, model, claude_model, narr_tok`. The deterministic-slice spine of all mining. | ✅ committed |
| `build_manifest.py` | Rebuilds `manifest.jsonl` from the corpus. The spine is scripted, not hand-made. | ✅ committed |
| `corpus-snapshot.SHA256SUMS` | `path → sha256` for every file in the snapshot. Integrity / tamper check. | ✅ committed |
| `E1.bundle.md` | E1's quote ledger: 93 provenance-tagged narration excerpts / 21 agents. | ✅ committed |
| `corpus-snapshot/` | **1.8 GB** full copy of the Claude Code project dir (2062 agent transcripts + sessions). The primary evidence. | ❌ **gitignored** (too large) |

## Rebuild / refresh
```
python3 build_manifest.py --summary                 # regenerate manifest.jsonl
rsync -a ~/.claude/projects/-Users-estevaouyra-dev-model-agent/ corpus-snapshot/   # refresh snapshot
cd corpus-snapshot && find . -type f -not -name SHA256SUMS | sort | xargs shasum -a 256 > ../corpus-snapshot.SHA256SUMS
```
Verify integrity: `cd corpus-snapshot && shasum -a 256 -c ../corpus-snapshot.SHA256SUMS`.

## Notes / caveats (carried from the catalog-stage critique, 2026-06-29)
- **Snapshot is gitignored**, so a fresh clone won't have it — re-run the rsync from the original
  (or restore from wherever the 1.8 GB is archived). The SHA256 manifest IS tracked, so a restored
  copy can be verified against what the catalog was built on.
- `claude_model` in the manifest is the LLM (constant `claude-opus-4-8`); `model` is the
  neuroscience target paper. Do not confuse them.
- 493/2062 agents have `role = unknown` (older inline-prompt format) — a 24% recall hole for any
  role-keyed slice; treat as a sampled stratum.
- Quote verification is mechanical: every promoted quote should be a `(source_path, substring)`
  pair that greps to a unique hit under `corpus-snapshot/`.
