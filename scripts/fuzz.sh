#!/usr/bin/env bash
set -euo pipefail

echo "[fuzz] running Hypothesis fuzz profile"
HYPOTHESIS_PROFILE=fuzz uv run --group dev pytest tests/test_properties.py
echo "[fuzz] done"
