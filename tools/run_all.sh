#!/bin/sh
# Every check in docs/verification.md, in the order they depend on each other.
# Usage: run_all.sh <python> <robot.jar> <ladr-bin-dir> <work-dir> [--full]
#
# Run from anywhere; every path is an argument, and each may contain spaces. <python> needs rdflib 7.
# <work-dir> receives the reasoner and prover output and one log per step; nothing outside it and this
# directory is written. run_queries rewrites docs/query-results.md and data/derived/, and the two
# steps after it append to query-results.md, so the three run in this order or not at all. inferences
# rewrites docs/dl/inferences.txt from the dl and controls output.
# --full is passed to run_fol.py (adds the Mace4 searches over the BFO set, which run to their limits).
PY="$1"; JAR="$2"; BIN="$3"; W="$4"; FULL="$5"
R=$(cd "$(dirname "$0")/.." && pwd)
[ -n "$W" ] || { echo "usage: run_all.sh <python> <robot.jar> <ladr-bin-dir> <work-dir> [--full]" >&2; exit 2; }
mkdir -p "$W/dl" "$W/controls" "$W/fol"
fails=0
step() {
  name="$1"; shift
  printf '### %s\n' "$name"
  "$@" > "$W/$name.log" 2>&1
  rc=$?; echo "exit $rc"; tail -6 "$W/$name.log"
  [ $rc -eq 0 ] || fails=$((fails + 1))
}
py() { "$PY" -I -X utf8 "$@"; }

step parse         py "$R/tools/measure.py" "$R"
step order         py "$R/tools/ttl_ordered.py" "$R"/data/*.ttl
step labels        py "$R/tools/annotate_ttl.py" "$R" --check
step clif          py "$R/tools/check_clif.py" "$R/clif/rbaco-bfo-access.cl"
step queries       py "$R/tools/run_queries.py" "$R"
step rowlbac       py "$R/tools/rowlbac_checks.py" "$R"
step rl            py "$R/tools/rl_check.py" "$R"
step dl            sh "$R/tools/run_dl.sh" "$R" "$JAR" "$W/dl"
step dl-diff       py "$R/tools/dl_diff.py" "$W/dl"
step controls-make py "$R/tools/make_dl_controls.py" "$W/controls"
step controls      sh "$R/tools/run_dl_controls.sh" "$R" "$JAR" "$W/controls"
step inferences    sh "$R/tools/make_inferences.sh" "$PY" "$R" "$JAR" "$W/dl" "$W/controls" "$R/docs/dl/inferences.txt"
step fol          py "$R/tools/run_fol.py" "$R" "$BIN" "$W/fol" "$W/dl/rbaco-bfo-domain-reasoned.owl" $FULL
echo "### $fails step(s) exited non-zero"
[ $fails -eq 0 ]
