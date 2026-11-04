#!/bin/sh
# Run HermiT (via ROBOT) on the RBACO ontologies and on each dataset merged with its derived file (the
# regression probes also with data/purchase.ttl, which they extend).
# Usage: run_dl.sh <rbaco-bfo-dir> <robot.jar> <out-dir>
R="$1"; JAR="$2"; OUT="$3"
mkdir -p "$OUT"
cd "$R" || exit 2
robot() { java -Xmx6G -jar "$JAR" "$@"; }

for ont in rbaco-bfo rbaco-bfo-domain; do
  echo "=== $ont"
  robot --catalog catalog-v001.xml merge --input "$ont.ttl" --output "$OUT/$ont-merged.owl" || exit 3
  robot --catalog catalog-v001.xml reason --input "$OUT/$ont-merged.owl" --reasoner HermiT \
    --axiom-generators "SubClass EquivalentClass" --include-indirect true \
    --exclude-tautologies structural --dump-unsatisfiable "$OUT/$ont-unsat.txt" \
    --output "$OUT/$ont-reasoned.owl" > "$OUT/$ont-reason.log" 2>&1
  echo "exit $?"; tail -5 "$OUT/$ont-reason.log"
done

for ds in us-persons code-review abac rt-policy purchase probes; do
  echo "=== $ds"
  extra=""
  [ -f "data/derived/$ds-derived.ttl" ] && extra="--input data/derived/$ds-derived.ttl"
  base=""
  [ "$ds" = probes ] && base="--input data/purchase.ttl"
  robot --catalog catalog-v001.xml merge $base --input "data/$ds.ttl" $extra --output "$OUT/$ds-merged.owl" || exit 3
  robot --catalog catalog-v001.xml reason --input "$OUT/$ds-merged.owl" --reasoner HermiT \
    --axiom-generators "ClassAssertion" --include-indirect true \
    --dump-unsatisfiable "$OUT/$ds-unsat.txt" \
    --output "$OUT/$ds-reasoned.owl" > "$OUT/$ds-reason.log" 2>&1
  echo "exit $?"; tail -5 "$OUT/$ds-reason.log"
done
