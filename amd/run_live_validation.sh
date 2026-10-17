#!/usr/bin/env bash
set +x
set -euo pipefail
ASR_REPO_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ASR_REPO_DIR"
# Desktop requires host networking to be enabled first. No ports are published here.
exec docker compose -f "$ASR_REPO_DIR/docker-compose.yml" -f "$ASR_REPO_DIR/amd/docker-compose.live.yml" \
  run --rm --no-deps app python amd/deployment.py live "$@"
