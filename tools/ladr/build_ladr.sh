#!/bin/sh
# Build prover9, mace4 and clausetester from LADR source on Windows, with mingw-w64 gcc and make.
# Usage: build_ladr.sh <Prover9-source-dir> <out-dir> <toolchain-bin-dir>
#
# Source: github.com/ai4reason/Prover9 at commit cdca95a51d3c3459b8fd2ebbb5ac1504be2172e3, unmodified.
# Toolchain: w64devkit 2.10.0 (gcc, make); pass its bin/ folder. The binaries load only KERNEL32.dll
# and msvcrt.dll, so they run without the toolchain afterwards.
#
# LADR is POSIX code. Three headers in win-shim/ beside this script stand in for what Windows lacks:
# sys/resource.h (getrusage from clock(); affects printed timing only), sys/wait.h (fork, pipe and
# wait stubs that fail; prover9 never calls the forking search), and compat.h, force-included, which
# maps SIGUSR1 to SIGBREAK. -fpermissive lets gcc 16 accept LADR's old-style C.
#
# clausetester and mace4 are relinked with a 512 MB stack. clausetester needed it for the 20-element
# explicit model of 2026-10-29, since retired (docs/design-record.md D18): without it, it exited 127 with
# no output. Mace4's search needs it for the theory of 2026-10-31: with the linker's default 2 MB, it
# exits 127 after "starting on domain size 3" (Windows status 0xC00000FD, a stack overflow).
#
# make splits XFLAGS on spaces, so the shim path must contain none. The script copies the shim into
# <out-dir> and stops if that path has a space.
set -e
SRC="$1"; OUT="$2"; TC="$3"
[ -d "$SRC/ladr" ] || { echo "not a LADR source tree: $SRC" >&2; exit 2; }
[ -x "$TC/gcc.exe" ] && [ -x "$TC/make.exe" ] || { echo "no gcc.exe and make.exe in: $TC" >&2; exit 2; }
PATH="$(cygpath -u "$TC"):$PATH"; export PATH
mkdir -p "$OUT"
HERE=$(cd "$(dirname "$0")" && pwd)
rm -rf "$OUT/win-shim"; cp -r "$HERE/win-shim" "$OUT/win-shim"
WM=$(cygpath -m "$OUT/win-shim")
case "$WM" in *" "*) echo "the shim path has a space, which make cannot pass: $WM" >&2; exit 2;; esac
X="-DPRIMITIVE_ENVIRONMENT -fpermissive -I$WM -include $WM/compat.h"

(cd "$SRC/ladr" && make libladr.a "XFLAGS=$X") > "$OUT/ladr-build.log" 2>&1
(cd "$SRC/provers.src" && make prover9 "XFLAGS=$X") > "$OUT/prover9-build.log" 2>&1
(cd "$SRC/mace4.src" && make libmace4.a mace4 "XFLAGS=$X" \
  && gcc -O -o mace4.exe mace4.o libmace4.a ../ladr/libladr.a -Wl,--stack,536870912) \
  > "$OUT/mace4-build.log" 2>&1
(cd "$SRC/apps.src" && make clausetester "XFLAGS=$X" \
  && gcc -O -o clausetester.exe clausetester.o ../ladr/libladr.a -Wl,--stack,536870912) \
  > "$OUT/clausetester-build.log" 2>&1

cp "$SRC/provers.src/prover9.exe" "$SRC/mace4.src/mace4.exe" "$SRC/apps.src/clausetester.exe" "$OUT/"
(cd "$OUT" && sha256sum prover9.exe mace4.exe clausetester.exe)
