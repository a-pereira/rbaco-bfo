#!/bin/sh
# Usage: run_dl_controls.sh <rbaco-bfo-dir> <robot.jar> <controls-dir>
R="$1"; JAR="$2"; C="$3"
cd "$R" || exit 2
for f in "$C"/c*.ttl; do
  n=$(basename "$f" .ttl)
  java -Xmx6G -jar "$JAR" --catalog catalog-v001.xml reason --input "$f" --reasoner HermiT \
    --output "$C/$n-out.owl" > "$C/$n.log" 2>&1
  echo "$n: exit $? :: $(grep -v WARNING "$C/$n.log" | grep -iE 'inconsistent|unsatisfiable|error' | head -2 | tr '\n' ' ')"
done
