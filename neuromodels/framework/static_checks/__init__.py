"""Static checks over the model corpus (stdlib + pyyaml only).

Currently one check: ``check_citations`` — a presence+resolution check that
every ``Citation: C-NNN`` / ``Assumption: A-NNN`` tag in a model's
``implementation/src/**/*.py`` resolves to an entry in that model's
``article_aware/spec/citations.yaml`` / ``assumptions.yaml``.

This enforces *presence and resolution* only — that tags point at real ledger
entries. It does NOT verify that the cited passage semantically supports the
function (that remains a periodic human audit; see DESIGN.md §8). Run
manually; no CI is wired.
"""
