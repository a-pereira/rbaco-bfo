# Licenses

RBACO-BFO is under two licenses, by kind of file. The files in `imports/` are not RBACO's work and keep their own licenses.

| Files | License | Text |
|---|---|---|
| The scripts (`tools/`, and the Claude Code hook `.claude/hooks/session-start.sh` with its registration in `.claude/settings.json`), the SPARQL queries (`queries/`) and the hand-specified model specifications (`docs/fol/hand-*.py`) | BSD 3-Clause | [`LICENSES/BSD-3-Clause.txt`](LICENSES/BSD-3-Clause.txt) |
| Everything else outside `imports/` and `LICENSES/`: the ontology (`rbaco-bfo.*`, `rbaco-bfo-domain.*`, `rbaco-bfo-terms.csv`), the first-order axioms (`clif/`), the example data (`data/`) and the documents | Creative Commons Attribution 4.0 International (CC BY 4.0) | [`LICENSES/CC-BY-4.0.txt`](LICENSES/CC-BY-4.0.txt) |
| `imports/`: BFO 2020, seven CCO v2.2 modules and an extract of IAO | CC BY 4.0 (BFO, IAO) and BSD 3-Clause (CCO), as each file states | [`NOTICE.md`](NOTICE.md) |

Copyright 2026 Anil Pereira, for everything outside `imports/` and `LICENSES/`.

To reuse RBACO-BFO under CC BY 4.0, credit it and its author, link this repository, and say what you changed. `CITATION.cff` gives the citation.
