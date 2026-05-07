#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m opendrive_clipboard.server --host "${HOST:-127.0.0.1}" --port "${PORT:-8080}"
