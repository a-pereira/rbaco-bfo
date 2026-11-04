# RBACO-BFO: instructions for Claude Code

This repository is RBACO-BFO, the BFO edition of RBACO, an ontology of role-based access control on BFO 2020, CCO v2.2 and IAO. `README.md` describes it. Sessions here reverify it or demonstrate it. Read `README.md` and `docs/expected-results.md` before running anything.

## Rules

- Work on a branch and open a pull request. Never push to `main`.
- Never edit `imports/`. Its files are byte copies that `SHA256SUMS` checks, apart from `iao-extract.ttl`, which only `tools/build_iao_extract.py` writes.
- Never add the three papers, or text copied from them. `sources/` holds their hashes and citations only.
- Generated files are written by their tools, never by hand: the `#:` comments in Turtle (`tools/annotate_ttl.py`), `data/*.ttl` (`tools/build_data.py`), `data/derived/`, `docs/query-results.md`, `docs/dl/inferences.txt` and `docs/fol-results.md` (`tools/run_all.sh`), the RDF/XML (`tools/to_rdfxml.py`), `rbaco-bfo-terms.csv` (`tools/build_terms_csv.py`) and `MANIFEST.sha256` (regenerate it after any change).
- `docs/expected-results.md` states what each check must give. When a run gives something else, report the difference and the output that shows it. Never change an expected value, a check or a test input to make a run match.
- Keep line endings as they are. `.gitattributes` turns conversion off, because `MANIFEST.sha256` hashes exact bytes.
- The documents cite the papers by printed page. When a claim rests on a paper you cannot read here, say so rather than restating it.

## Reverifying

1. Get the tools in `docs/expected-results.md`, and check each download's SHA-256 before using it.
2. Run `sh tools/run_all.sh <python> <robot.jar> <ladr-bin-dir> <work-dir>`, with the work directory outside the repository. It takes about 20 minutes, so run it in the background.
3. Compare each step's summary with `docs/expected-results.md`, then run `sha256sum -c MANIFEST.sha256`. Only the files and lines that the last section of `docs/expected-results.md` names may differ.
4. Run the two hand-model checks in `README.md`.
5. Report each expected result as matched or not, with the value measured.

`/reverify` (`.claude/commands/reverify.md`) runs these steps. In a Claude Code cloud session, the SessionStart hook `.claude/hooks/session-start.sh` installs the tools outside the repository, checks their SHA-256, and exports `RBACO_PY`, `RBACO_ROBOT` and `RBACO_LADR`, the first three arguments of step 2.

The checks run on Windows in Git Bash and on Linux, where `tools/ladr/build_ladr_linux.sh` builds the LADR binaries (design-record D21). Every text file they write has LF line endings on both, and no report holds a run time, so a run on the same inputs reproduces every file it writes, byte for byte. Known gap: the port of D21 has been run on Linux only; it has not been rerun on Windows yet.

## Demonstrating

`docs/mapping.md` maps each ROWLBAC pattern to the RBACO terms and queries that cover it, and `docs/query-results.md` holds the output of the last run. To show a decision, run `tools/run_queries.py` on the example data and follow a grant or denial in `data/derived/` to the request it decides on, the regulation it cites, and the axiom in `clif/rbaco-bfo-access.cl` behind it. `/demo` (`.claude/commands/demo.md`) runs this walkthrough.
