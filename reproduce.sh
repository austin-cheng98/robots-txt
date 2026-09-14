#!/usr/bin/env bash
set -euo pipefail

SNAPSHOT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SNAPSHOT_ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required" >&2
  exit 1
fi
if ! python3 -c 'import matplotlib' >/dev/null 2>&1; then
  echo "error: python3 matplotlib is required" >&2
  exit 1
fi

BUILD_MPLCONFIGDIR="${TMPDIR:-/tmp}/consent-audit-mpl-cache"
mkdir -p "$BUILD_MPLCONFIGDIR"

python3 analysis_revision.py
MPLCONFIGDIR="$BUILD_MPLCONFIGDIR" python3 make_fig_v2.py
cp fig_gradient_v2.pdf paper/fig_gradient_v2.pdf
MPLCONFIGDIR="$BUILD_MPLCONFIGDIR" python3 make_fig_estimands.py

echo "rebuilt analysis outputs and figure PDFs"
