#!/usr/bin/env bash
set -euo pipefail

# Preview deploy — creates a tagged revision without shifting traffic.
# Used for the brand-kit re-skin pre-hackathon: deploy to a tagged URL,
# eyeball it live, then promote traffic on visual OK.
#
# After preview eyeball passes, promote with:
#   gcloud run services update-traffic opendrive-clipboard-demo \
#     --to-tags preview=100 --region "$REGION"
#
# Rollback (if promote goes wrong) — list revisions and revert traffic:
#   gcloud run revisions list --service opendrive-clipboard-demo --region "$REGION"
#   gcloud run services update-traffic opendrive-clipboard-demo \
#     --to-revisions <prior-revision-name>=100 --region "$REGION"

SERVICE="opendrive-clipboard-demo"
REGION="${REGION:-us-central1}"
ENABLE_TTS="${ENABLE_TTS:-false}"

: "${GOOGLE_CLOUD_PROJECT:?GOOGLE_CLOUD_PROJECT must be set (export it before running)}"

echo "=== Preview deploy: ${SERVICE} (region=${REGION}, project=${GOOGLE_CLOUD_PROJECT}) ==="
echo "    Tag: preview · Traffic: 0% (no promote until explicit) · TTS: ${ENABLE_TTS}"
echo

gcloud run deploy "$SERVICE" \
  --project "$GOOGLE_CLOUD_PROJECT" \
  --region "$REGION" \
  --source . \
  --tag preview \
  --no-traffic \
  --allow-unauthenticated \
  --set-env-vars "OPENDRIVE_CLIPBOARD_ENABLE_GEMINI=false,SPEECHIFY_ENABLE_TTS=${ENABLE_TTS}"

echo
echo "=== Preview revision deployed ==="
echo "The tagged URL is printed above (look for: 'preview---opendrive-clipboard-demo-…')."
echo "Eyeball it on the Mac Mini. If good, promote traffic with:"
echo
echo "    gcloud run services update-traffic ${SERVICE} \\"
echo "      --to-tags preview=100 --region ${REGION}"
echo
