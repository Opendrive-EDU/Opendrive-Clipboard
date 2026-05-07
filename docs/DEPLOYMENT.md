# Cloud Run Deployment

The synthetic MVP is designed to deploy as one Cloud Run service. It uses the deterministic local draft provider by default so judges can test the demo without a Gemini key.

## Local Checks

```bash
python3 -m unittest discover -s tests
python3 -m opendrive_clipboard.server --host 127.0.0.1 --port 8080
```

Open `http://127.0.0.1:8080`.

## Deploy

```bash
export GOOGLE_CLOUD_PROJECT=opendrive-clipboard
export REGION=us-central1
export SERVICE=opendrive-clipboard-demo
scripts/deploy_cloud_run.sh
```

The deploy script uses `gcloud run deploy --source .` and keeps `OPENDRIVE_CLIPBOARD_ENABLE_GEMINI=false` for the stable public demo.

## Optional Gemini Mode

Use Secret Manager for keys. Do not commit `.env` files or service-account JSON.

```bash
gcloud run services update opendrive-clipboard-demo \
  --region us-central1 \
  --set-env-vars OPENDRIVE_CLIPBOARD_ENABLE_GEMINI=true
```

Attach `GEMINI_API_KEY` or `GOOGLE_API_KEY` as a secret-backed environment variable.
