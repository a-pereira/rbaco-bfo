# Expected results

What the checks must give when they are run again. Counts must match exactly; run times will not. The baseline was measured on Windows 11 in Git Bash, last on 2026-11-03 after the rename of design-record D20.

## Tools

| Tool | Version | Where from | SHA-256 |
|---|---|---|---|
| ROBOT, with HermiT 1.4.5.456 | 1.9.8 | https://github.com/ontodev/robot/releases/download/v1.9.8/robot.jar (81,524,668 bytes) | `6f518b0293d8146d8a5a168c53607a952effb66bcaf3c6539996d7ec5c5f05f8` |
| Prover9, Mace4, clausetester | LADR 2009-11A | built by `tools/ladr/build_ladr.sh` from github.com/ai4reason/Prover9 at commit `cdca95a51d3c3459b8fd2ebbb5ac1504be2172e3` | Windows builds of 2026-10-31: `prover9.exe` `abbfc4fe3f0d1173c98dea9c0fb746fdca0d3847a5bced487c63cff5570c97cb`, `mace4.exe` (512 MB stack) `f036c9f897495a5360ff09df7771561ffb32b4289040dcf2c7f7ad66352c1f4d`, `clausetester.exe` (512 MB stack) `73a9855f4b22899ecd776af8c06b6b790711dda94e8ede57946565f53b1776a0` |
| Python and rdflib | Python 3.13.14, rdflib 7.6.0 | | |
| Java | 24.0.2; ROBOT 1.9.8 needs 11 or later | | |

Under an rdflib other than 7.6.0, `tools/run_queries.py` runs without its evaluation shortcuts and takes more than ten times as long (design-record D17); its results should not change.

## run_all.sh, without --full

| Step | Expected |
|---|---|
| parse | every file parses; `rbaco-bfo.owl` and `rbaco-bfo-domain.owl` isomorphic to the Turtle; 38 and 8 borrowed IRIs, none missing from `imports/` |
| order | 0 forward references in each of the six data files |
| labels | no file stale |
| clif | 48 axioms, 48 distinct IDs, 82 predicates |
| queries | 32 of 32 run without error; probe expectations 15 of 15; `docs/query-results.md` and `data/derived/` as committed, line for line, apart from the Elapsed line |
| rowlbac | as in `docs/verification.md` § 4 |
| rl | 0 clashes in all six datasets; 4 of 4 negative controls detected |
| dl | 8 of 8 inputs consistent, no unsatisfiable classes; purchase: 653 individuals, 4,439 inferred type assertions; probes: 820 and 5,439 |
| dl-diff | 0 candidate merges |
| controls | 8 of 8 rejected |
| inferences | `docs/dl/inferences.txt` rewritten: 111 lines, a verdict for each of the 8 controls |
| fol | 18 proofs (17 goals, the lemma in both directions), 5 Mace4 models, 3 searches ending at max_seconds at size 3 (`m-t1-cr42-same-time-not-violated`, `m-t1-pdsd-same-content`, `m-t1-pdsd-same-instant`) |

## Hand-specified models

Not part of `run_all.sh`. The README's two `check_hand_model.py` commands: 137 of 137 and 149 of 149 formulas true and every goal true, as `docs/fol/model-results.txt` records.

## What a run may change

`run_all.sh` rewrites `docs/query-results.md`, `docs/fol-results.md`, `docs/dl/inferences.txt` and `data/derived/`. On the same inputs it reproduces them apart from run times, so `sha256sum -c MANIFEST.sha256` afterwards reports `docs/query-results.md` (its Elapsed line) and `docs/fol-results.md` (its times and run date) as changed, and no other file. On Linux, `docs/query-results.md`, `docs/fol-results.md` and `docs/dl/inferences.txt` also differ in line endings, because Python wrote CRLF on Windows (`CLAUDE.md`, known gap).

The generators of the other committed files reproduce them byte for byte: `tools/build_data.py`, `tools/annotate_ttl.py`, `tools/build_terms_csv.py` and `tools/build_iao_extract.py`. `tools/to_rdfxml.py` writes RDF/XML that is isomorphic to the committed files but not byte-identical, because rdflib's writer names and orders blank nodes differently from run to run; `parse` checks the isomorphism.
