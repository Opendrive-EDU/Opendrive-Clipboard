# OpenDrive Clipboard Architecture

OpenDrive Clipboard is a synthetic-data Track 1 Build demo for the Google for Startups AI Agents Challenge. It demonstrates a multi-step debrief workflow rather than a chatbot.

## Runtime Surfaces

```text
Browser demo UI
  -> Python demo API
  -> ClipboardRunner
  -> Scenario Intake Agent
  -> Curriculum Retrieval Agent
  -> Draft Assembly Agent
  -> Review Gate Agent
```

The local MVP is dependency-free so judges and reviewers can run it quickly. The production challenge target replaces the local draft provider with Gemini and deploys the app on Google Cloud.

## Agent Collaboration

| Agent | Responsibility | Tool surface |
|---|---|---|
| Scenario Intake Agent | Normalizes a fake drive scenario and fake OpenDrive Beacon-like events. | `drive_context.get_demo_drive`, `drive_context.get_intervention_events` |
| Curriculum Retrieval Agent | Grounds the draft with reviewed curriculum snippets. | `curriculum.lookup_lesson`, `curriculum.get_standard` |
| Draft Assembly Agent | Creates draft debrief artifacts. | `draft.local_template`, optional `draft.gemini_api_optional` |
| Review Gate Agent | Creates demo-only draft state and stops at instructor review. | `review.create_draft`, `review.submit_for_review`, `review.record_decision` |

## Bounded Action

The meaningful action is routing a clear, respectful draft debrief package to licensed instructor review. The demo must not create official LMS, licensing, certificate, transcript, or DOL records.

## Google Cloud Target

- Intelligence: Gemini API or Vertex AI-hosted Gemini.
- Orchestration: Google ADK or a supported framework managed on Google Cloud.
- Tool access: MCP-style tools for drive context, curriculum lookup, draft assembly, and review.
- Infrastructure: Cloud Run first; Agent Runtime or Agent Engine when packaging is ready.
- Grounding: Agent Search, Vertex AI Search, or a reviewed JSON/RAG fallback for the first judge build.

## Safety Boundary

The public repo uses synthetic data only. It contains no real student records, real OpenDrive Beacon telemetry, private production code, Vault documents, or service-account credentials.
