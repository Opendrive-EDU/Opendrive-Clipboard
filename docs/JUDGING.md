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

- No live student records (synthetic demo data only in the public repo).
- No real OpenDrive Beacon telemetry in the public repo (synthetic recordings only).
- No service-account JSON files in the repo.
- No official LMS, DOL, certificate, or transcript writes from the demo.
- **No vehicle control** — Clipboard never touches brakes, throttle, steering, or any vehicle subsystem.
- **No covert audio capture** — the boundary mic captures only when both a physical hardware kill switch and a UI toggle are flipped on, with the mic state badge always visible to the student. Default mode is `stt_ephemeral_only` (audio discarded immediately after transcription); raw-audio retention requires explicit consent + reason code.

## Demo Video Beat

Target 1:45, hard cap 2:00:

1. Problem and business impact.
2. Synthetic scenario intake.
3. Agent trace and grounded draft.
4. Instructor review gate.
5. Safety boundary and Google Cloud architecture.
