#!/bin/sh
# Write docs/dl/inferences.txt from a DL run and the negative controls: dl_diff.py's report, the inferred
# subclass links among imported classes checked against the imports reasoned alone (imports_only.sh, run
# here if its output is missing), then one line per negative control with the reasoner's verdict.
# Usage: make_inferences.sh <python> <rbaco-bfo-dir> <robot.jar> <dl-dir> <controls-dir> <out-file>
# Exits 1 if a step fails or a control log holds no verdict, after writing the file.
PY="$1"; R="$2"; JAR="$3"; DL="$4"; C="$5"; OUT="$6"
[ -n "$OUT" ] || { echo "usage: make_inferences.sh <python> <rbaco-bfo-dir> <robot.jar> <dl-dir> <controls-dir> <out-file>" >&2; exit 2; }
if [ ! -f "$DL/imports-only-reasoned.owl" ]; then
  sh "$R/tools/imports_only.sh" "$R" "$JAR" "$DL" >&2 || exit 1
fi
rc=0
{
  "$PY" -I -X utf8 "$R/tools/dl_diff.py" "$DL" || rc=1
  echo
  echo "== inferred subClassOf among imported classes (rbaco-bfo-reasoned vs the imports reasoned alone)"
  "$PY" -I -X utf8 "$R/tools/dl_imported.py" "$DL" || rc=1
  echo
  echo "== negative controls"
  for f in "$C"/c*.log; do
    v=$(grep -v WARNING "$f" | grep -iE 'inconsistent|unsatisfiable' | head -1 |
        sed -E 's/.*ReasonerHelper - //; s/[.] TIP.*//; s/ in the ontology[.].*//')
    [ -n "$v" ] || { v="(no verdict in the log)"; rc=1; }
    echo "$(basename "$f" .log): $v"
  done
} > "$OUT"
echo "wrote $OUT: $(wc -l < "$OUT") lines, $(grep -c '^c[0-9]' "$OUT") controls"
exit $rc
