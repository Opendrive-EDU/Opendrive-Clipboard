#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

: "${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT before deploying.}"
: "${REGION:=us-central1}"
: "${SERVICE:=opendrive-clipboard-demo}"

# Optional Speechify TTS. Default OFF so the public demo runs with zero secrets.
# To enable, store the key in Secret Manager once:
#   printf '%s' "$SPEECHIFY_API_KEY" | gcloud secrets create SPEECHIFY_API_KEY \
#     --project "$GOOGLE_CLOUD_PROJECT" --data-file=-
# then deploy with ENABLE_TTS=true (the key is mounted from the secret, never
# passed as plaintext env).
: "${ENABLE_TTS:=false}"
: "${SPEECHIFY_VOICE_DEFAULT:=scott}"
: "${SPEECHIFY_VOICE_YOUTH:=$SPEECHIFY_VOICE_DEFAULT}"

env_vars="OPENDRIVE_CLIPBOARD_ENABLE_GEMINI=false,SPEECHIFY_ENABLE_TTS=${ENABLE_TTS}"
secret_args=()
if [ "$ENABLE_TTS" = "true" ]; then
  env_vars="${env_vars},SPEECHIFY_VOICE_DEFAULT=${SPEECHIFY_VOICE_DEFAULT},SPEECHIFY_VOICE_YOUTH=${SPEECHIFY_VOICE_YOUTH}"
  secret_args=(--set-secrets "SPEECHIFY_API_KEY=SPEECHIFY_API_KEY:latest")
fi

gcloud run deploy "$SERVICE" \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --region "$REGION" \
  --source . \
  --allow-unauthenticated \
  --set-env-vars "$env_vars" \
  "${secret_args[@]}"
