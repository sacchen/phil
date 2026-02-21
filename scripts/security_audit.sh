#!/usr/bin/env bash
set -euo pipefail

echo "[security] auditing Python dependencies for known vulnerabilities"
tmp_requirements="$(mktemp)"
trap 'rm -f "$tmp_requirements"' EXIT

uv export \
  --format requirements.txt \
  --group dev \
  --locked \
  --no-hashes \
  --no-header \
  --no-emit-project \
  --output-file "$tmp_requirements"

uv run --group dev --with pip-audit pip-audit --strict --no-deps --disable-pip -r "$tmp_requirements"
echo "[security] done"
