# Expected results

What the checks must give when they are run again. Counts must match exactly; run times will not. The baseline was measured on Windows 11 in Git Bash, last on 2026-11-03 after the rename of design-record D20. On 2026-11-04, after the port of design-record D21, the checks were run on Linux and gave every count below (section Linux).

## Tools

| Tool | Version | Where from | SHA-256 |
|---|---|---|---|
| ROBOT, with HermiT 1.4.5.456 | 1.9.8 | https://github.com/ontodev/robot/releases/download/v1.9.8/robot.jar (81,524,668 bytes) | `6f518b0293d8146d8a5a168c53607a952effb66bcaf3c6539996d7ec5c5f05f8` |
| Prover9, Mace4, clausetester | LADR 2009-11A | built by `tools/ladr/build_ladr.sh` from github.com/ai4reason/Prover9 at commit `cdca95a51d3c3459b8fd2ebbb5ac1504be2172e3` | Windows builds of 2026-10-31: `prover9.exe` `abbfc4fe3f0d1173c98dea9c0fb746fdca0d3847a5bced487c63cff5570c97cb`, `mace4.exe` (512 MB stack) `f036c9f897495a5360ff09df7771561ffb32b4289040dcf2c7f7ad66352c1f4d`, `clausetester.exe` (512 MB stack) `73a9855f4b22899ecd776af8c06b6b790711dda94e8ede57946565f53b1776a0` |
| Python and rdflib | Python 3.13.14, rdflib 7.6.0 | | |
| Java | 24.0.2; ROBOT 1.9.8 needs 11 or later | | |

Under an rdflib other than 7.6.0, `tools/run_queries.py` runs without its evaluation shortcuts and takes more than ten times as long (design-record D17); its results should not change.

## Linux

Measured on 2026-11-04 in a Claude Code cloud container: Ubuntu 24.04.5 LTS on x86_64, Linux 6.18, 4 CPUs and 15 GB of memory. ROBOT is the `robot.jar` above, checked against the same SHA-256. The other tools:

| Tool | Version | Where from | SHA-256 |
|---|---|---|---|
| Prover9, Mace4, clausetester | LADR 2009-11A | built by `tools/ladr/build_ladr_linux.sh` from the same commit, with gcc 13.3.0 (Ubuntu 13.3.0-6ubuntu2~24.04.1), GNU Make 4.3 and glibc 2.39; two builds, in different directories, were byte-identical | `prover9` `06ad0e039bf9523d52c8dd71c2934a5f95d6a447e10e561776cc49720251b7b1`, `mace4` `9dc8ff8e9914b15489b6174b2d7eea58f0884a4d4b152d06359ad9fc19021975`, `clausetester` `67284b76ca24a2c739f8b38ac673feb4293b319c8a62ae6f9b44b2ae8a0f5cca` |
| Python and rdflib | Python 3.13.18; rdflib 7.6.0 and pyparsing 3.3.3, in a virtual environment | PyPI, as `tools/requirements.txt` pins them | wheels: `rdflib-7.6.0-py3-none-any.whl` `30c0a3ebf4c0e09215f066be7246794b6492e054e782d7ac2a34c9f70a15e0dd`, `pyparsing-3.3.3-py3-none-any.whl` `ece8c00a69cf01b45d0b1dedabb469c90d8caf996d4fda40f147627a122849a4` |
| Java | OpenJDK 21.0.12.1 (Ubuntu build 21.0.12.1+1-1-24.04.4) | | |

The Linux binaries have no stack size of their own: `run_fol.py` and `check_hand_model.py` start mace4 and clausetester with a soft stack limit of 512 MB, the stack the Windows builds are linked with (design-record D21). A build with another compiler may differ in its bytes. One with gcc 14.2.0, which needs `-fpermissive` (the script passes it from GCC 14 on), did, and gave the same verdicts, model sizes and proof labels on the 14 Prover9 runs `p1` to `p10d` and the four Mace4 runs that find a model in seconds, and the same counts on both hand-specified models. In a cloud session, `.claude/hooks/session-start.sh` installs all of these in `~/.cache/rbaco-bfo` and exports their paths as `RBACO_PY`, `RBACO_ROBOT` and `RBACO_LADR`.

## run_all.sh, without --full

| Step | Expected |
|---|---|
| parse | every file parses; `rbaco-bfo.owl` and `rbaco-bfo-domain.owl` isomorphic to the Turtle; 38 and 8 borrowed IRIs, none missing from `imports/` |
| order | 0 forward references in each of the six data files |
| labels | no file stale |
| clif | 48 axioms, 48 distinct IDs, 82 predicates |
| queries | 32 of 32 run without error; probe expectations 15 of 15; `docs/query-results.md` and `data/derived/` as committed, byte for byte |
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

`run_all.sh` rewrites `docs/query-results.md`, `docs/fol-results.md`, `docs/dl/inferences.txt` and `data/derived/`, and `run_fol.py` writes the two theories that `docs/fol/` keeps to `<work-dir>/fol/`. Since design-record D21 the reports hold no run time or run date, and the checks write every text file with LF line endings on every platform. On the same inputs a run therefore reproduces all of them byte for byte, and `sha256sum -c MANIFEST.sha256` afterwards reports no file as changed. The times are in the work directory: the query run's in `queries.log`, the first-order run's date and each run's seconds in `fol.log` and `fol/fol-results.md`. This held on Linux on 2026-11-04; the port has not been rerun on Windows yet.

The generators of the other committed files reproduce them byte for byte: `tools/build_data.py`, `tools/annotate_ttl.py`, `tools/build_terms_csv.py` and `tools/build_iao_extract.py`. `rbaco-bfo-terms.csv` has CRLF line endings, which Python's csv module writes on every platform. On Linux on 2026-11-04 the first three were rerun with that result; `build_iao_extract.py` was not, since the IAO release it reads is served from purl.obolibrary.org, which the container could not reach. `tools/to_rdfxml.py` writes RDF/XML that is isomorphic to the committed files but not byte-identical, because rdflib's writer names and orders blank nodes differently from run to run; `parse` checks the isomorphism.
