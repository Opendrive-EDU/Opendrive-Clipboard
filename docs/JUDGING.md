# Judge Testing Guide

## Quick Start

```bash
python3 -m unittest discover -s tests
python3 -m opendrive_clipboard.server --host 127.0.0.1 --port 8080
```

Open:

```text
http://127.0.0.1:8080
```

No API key is required for the default synthetic demo.

Cloud Run deployment notes live in `docs/DEPLOYMENT.md`.

## Optional Gemini Preview

The local draft provider is deterministic by default. To test the optional Gemini provider, set:

```bash
export OPENDRIVE_CLIPBOARD_ENABLE_GEMINI=true
export GEMINI_API_KEY=...
```

If the API key is missing or the network call fails, the demo falls back to the deterministic provider so judge testing remains stable.

## What To Verify

- The scenario list loads.
- Running the agent produces a trace with specialized agents and MCP-style tools.
- The draft is marked `DRAFT - INSTRUCTOR REVIEW REQUIRED`.
- Approve, edit, reject, and regenerate only update demo state.
- The boundary panel states fake data, post-drive only, and instructor review.

## Non-Negotiable Boundaries

- No live student records.
- No real OpenDrive Beacon telemetry.
- No service-account JSON files.
- No official LMS, DOL, certificate, or transcript writes.
- No in-vehicle audio capture or vehicle control.

## Demo Video Beat

Target 1:45, hard cap 2:00:

1. Problem and business impact.
2. Synthetic scenario intake.
3. Agent trace and grounded draft.
4. Instructor review gate.
5. Safety boundary and Google Cloud architecture.
