#!/bin/sh
# Reason over the imports alone (BFO core, the CCO modules, the IAO extract), for comparison.
# Usage: imports_only.sh <rbo-dir> <robot.jar> <out-dir>. ROBOT's output goes to <out-dir>/imports-only.log,
# printed here without its warnings; the exit status is ROBOT's.
R="$1"; JAR="$2"; OUT="$3"; cd "$R" || exit 2
java -Xmx6G -jar "$JAR" --catalog catalog-v001.xml merge --input imports/bfo-core.ttl \
  --input imports/AgentOntology.ttl --input imports/EventOntology.ttl --input imports/InformationEntityOntology.ttl \
  --input imports/GeospatialOntology.ttl --input imports/TimeOntology.ttl --input imports/ExtendedRelationOntology.ttl \
  --input imports/ArtifactOntology.ttl --input imports/iao-extract.ttl \
  reason --reasoner HermiT --axiom-generators "SubClass EquivalentClass" --include-indirect true \
  --exclude-tautologies structural --output "$OUT/imports-only-reasoned.owl" > "$OUT/imports-only.log" 2>&1
rc=$?
grep -v WARNING "$OUT/imports-only.log"
echo "exit $rc"
exit $rc
