#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

: "${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT before deploying.}"
: "${REGION:=us-central1}"
: "${SERVICE:=opendrive-clipboard-demo}"

gcloud run deploy "$SERVICE" \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --region "$REGION" \
  --source . \
  --allow-unauthenticated \
  --set-env-vars OPENDRIVE_CLIPBOARD_ENABLE_GEMINI=false
