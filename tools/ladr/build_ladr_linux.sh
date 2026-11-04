#!/bin/sh
# Build prover9, mace4 and clausetester from LADR source on Linux, with the system's gcc, make and git.
# Usage: build_ladr_linux.sh <out-dir> [<Prover9-source-dir>]
#
# Source: github.com/ai4reason/Prover9 at commit cdca95a51d3c3459b8fd2ebbb5ac1504be2172e3 (LADR 2009-11A),
# unmodified. Without a source directory the script fetches that commit into <out-dir>/src and checks that it
# has it. A source directory that is a git checkout must be at that commit; one that is not is used as it is.
# The binaries, a log per build and their SHA-256 go to <out-dir>.
#
# LADR is POSIX code: it builds with its own makefiles and flags, and needs none of the shims and defines
# build_ladr.sh uses on Windows. Built so, the banner and exit lines give the real process ID, user and host
# where the Windows builds print 0 and "unknown"; nothing else differs. The compiler is $CC, default gcc.
# GCC 14 made implicit int an error, and mace4's select.c and msearch.c use it, so from GCC 14 on the script
# passes -fpermissive, which makes it a warning again, as build_ladr.sh does for gcc 16. With GCC 13 it passes
# nothing (docs/expected-results.md, section Linux).
#
# The Windows builds of mace4 and clausetester are linked with a 512 MB stack (build_ladr.sh). On Linux a
# program's stack is set when it starts, by the soft limit (ulimit -s, 8 MB by default), not by the binary,
# so run_fol.py and check_hand_model.py raise that limit to 512 MB for these two programs when they run them.
set -e
OUT="$1"; SRC="$2"; CC="${CC:-gcc}"
COMMIT=cdca95a51d3c3459b8fd2ebbb5ac1504be2172e3
[ -n "$OUT" ] || { echo "usage: build_ladr_linux.sh <out-dir> [<Prover9-source-dir>]" >&2; exit 2; }
for t in "$CC" make; do
  command -v "$t" > /dev/null || { echo "$t not found" >&2; exit 2; }
done
X=""
if "$CC" -v 2>&1 | grep -q '^gcc version' && [ "$("$CC" -dumpversion | cut -d. -f1)" -ge 14 ]; then
  X="-fpermissive"
fi
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
if [ -z "$SRC" ]; then
  command -v git > /dev/null || { echo "git not found" >&2; exit 2; }
  SRC="$OUT/src"
  rm -rf "$SRC"; git init -q "$SRC"
  git -C "$SRC" fetch -q --depth 1 https://github.com/ai4reason/Prover9.git "$COMMIT"
  git -C "$SRC" -c advice.detachedHead=false checkout -q FETCH_HEAD
fi
[ -d "$SRC/ladr" ] || { echo "not a LADR source tree: $SRC" >&2; exit 2; }
if [ -e "$SRC/.git" ]; then
  head=$(git -C "$SRC" rev-parse HEAD)
  [ "$head" = "$COMMIT" ] || { echo "$SRC is at $head, not $COMMIT" >&2; exit 3; }
else
  echo "$SRC is not a git checkout; its commit is not checked" >&2
fi

build() {
  log="$OUT/$1-build.log"; dir="$SRC/$2"; shift 2
  (cd "$dir" && make "CC=$CC" "XFLAGS=$X" "$@") > "$log" 2>&1 \
    || { tail -20 "$log" >&2; echo "build failed, see $log" >&2; exit 4; }
}
build ladr ladr libladr.a
build prover9 provers.src prover9
build mace4 mace4.src libmace4.a mace4
build clausetester apps.src clausetester

cp "$SRC/provers.src/prover9" "$SRC/mace4.src/mace4" "$SRC/apps.src/clausetester" "$OUT/"
(cd "$OUT" && sha256sum prover9 mace4 clausetester)
