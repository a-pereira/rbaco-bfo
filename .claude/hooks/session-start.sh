#!/bin/bash
# SessionStart hook: prepare a Claude Code cloud session to run RBACO-BFO's checks (CLAUDE.md, "Reverifying").
# Runs only when CLAUDE_CODE_REMOTE is true. Installs, outside the repository, in $RBACO_TOOLS (default
# ~/.cache/rbaco-bfo):
#   venv/      Python with the packages of tools/requirements.txt, each wheel checked by its SHA-256
#   robot.jar  ROBOT, from the URL and checked against the SHA-256 that docs/expected-results.md gives
#   ladr/      prover9, mace4 and clausetester, built by tools/ladr/build_ladr_linux.sh
# and exports RBACO_PY, RBACO_ROBOT and RBACO_LADR to the session (CLAUDE_ENV_FILE). An install is skipped when
# the files that decide it are unchanged since it last succeeded. From an empty cache it took 18 s on 2026-11-04.
set -euo pipefail
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
R="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
T="${RBACO_TOOLS:-$HOME/.cache/rbaco-bfo}"
mkdir -p "$T"
HOOK="$R/.claude/hooks/session-start.sh"

# Java 11 or later for ROBOT; gcc, make and git for LADR. Installed only if missing.
java_major() {
  v=$(java -version 2>&1 | sed -n 's/.* version "\([0-9][0-9]*\).*/\1/p' | sed -n 1p)
  echo "${v:-0}"
}
need=""
{ command -v java > /dev/null && [ "$(java_major)" -ge 11 ]; } || need="$need default-jre-headless"
{ command -v gcc > /dev/null && command -v make > /dev/null; } || need="$need build-essential"
command -v git > /dev/null || need="$need git"
if [ -n "$need" ]; then
  apt-get update -q > /dev/null
  # shellcheck disable=SC2086
  DEBIAN_FRONTEND=noninteractive apt-get install -y -q $need > /dev/null
fi

# Python and rdflib
V="$T/venv"
if ! sha256sum --check --status "$V/.session-start.sha256" 2> /dev/null \
   || ! "$V/bin/python" -I -c "import rdflib" 2> /dev/null; then
  rm -rf "$V"
  python3 -m venv "$V"
  "$V/bin/python" -m pip install -q --disable-pip-version-check --require-hashes -r "$R/tools/requirements.txt"
  sha256sum "$HOOK" "$R/tools/requirements.txt" > "$V/.session-start.sha256"
fi

# ROBOT: the first line of docs/expected-results.md with a robot.jar URL and a SHA-256 gives both
row=$(grep -m1 'https://[^ ]*/robot\.jar.*`[0-9a-f]\{64\}`' "$R/docs/expected-results.md" || true)
url=$(printf '%s\n' "$row" | grep -o 'https://[^ ]*/robot\.jar' || true)
sha=$(printf '%s\n' "$row" | grep -o '`[0-9a-f]\{64\}`' | tr -d '`' || true)
[ -n "$url" ] && [ -n "$sha" ] || { echo "no robot.jar URL and SHA-256 in docs/expected-results.md" >&2; exit 1; }
J="$T/robot.jar"
if ! echo "$sha  $J" | sha256sum --check --status 2> /dev/null; then
  d=$(mktemp -d "$T/robot.XXXXXX")
  curl -fsSL --retry 4 -o "$d/robot.jar" "$url"
  echo "$sha  $d/robot.jar" | sha256sum --check --status \
    || { echo "robot.jar from $url does not have SHA-256 $sha" >&2; rm -rf "$d"; exit 1; }
  mv "$d/robot.jar" "$J"; rmdir "$d"
fi

# LADR
L="$T/ladr"
if ! sha256sum --check --status "$L/.session-start.sha256" 2> /dev/null; then
  rm -f "$L/.session-start.sha256"
  sh "$R/tools/ladr/build_ladr_linux.sh" "$L" > /dev/null
  sha256sum "$HOOK" "$R/tools/ladr/build_ladr_linux.sh" "$L/prover9" "$L/mace4" "$L/clausetester" \
    > "$L/.session-start.sha256"
fi

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  printf 'export RBACO_PY="%s"\nexport RBACO_ROBOT="%s"\nexport RBACO_LADR="%s"\n' "$V/bin/python" "$J" "$L" \
    >> "$CLAUDE_ENV_FILE"
fi
echo "RBACO-BFO checks: RBACO_PY=$V/bin/python RBACO_ROBOT=$J RBACO_LADR=$L"
(cd "$L" && sha256sum prover9 mace4 clausetester)
