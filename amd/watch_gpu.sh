#!/usr/bin/env bash
set +x
set -euo pipefail
ASR_AMD_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "${AMD_PYTHON:-python3}" "$ASR_AMD_DIR/deployment.py" monitor "$@"
