# Google Cloud Agent Setup Plan — OpenDrive Clipboard

**Project:** OpenDrive Clipboard  
**Subtitle:** An instructor-reviewed drafting assistant for post-drive teachable moments  
**Primary challenge track:** Track 1 — Build / Net-New Agents  
**Stretch challenge track:** Track 3 — Refactor / Marketplace & Enterprise Ready  
**Audience:** Mr. Law and the engineering team  
**Last updated:** 2026-05-01  

---

## 1. Core Challenge Interpretation

The Google for Startups AI Agents Challenge is not asking for a simple chatbot.

The project must demonstrate:

- multi-step workflow;
- specialized agents or agent-like modules;
- Gemini-powered reasoning;
- ADK or supported orchestration;
- Google Cloud deployment;
- meaningful action beyond chat;
- grounding / retrieval where useful;
- B2B use-case clarity;
- traceability through an inspector panel;
- safe human-review boundaries.

For this project, the meaningful action is:

```text
Save a reviewed demo log only after instructor approval.
```

The agent does not approve its own output.

---

## 2. Product Framing

Use this public framing:

```text
OpenDrive Clipboard is a B2B, instructor-reviewed multi-agent workflow that turns teachable driving moments into clear, respectful next steps.
```

Use this core line:

```text
AI organizes the moment. The instructor leads the lesson.
```

Use this secondary line:

```text
The assistant drafts. The instructor decides.
```

Do not frame this as:

- automated driving instructor;
- automated coach;
- automated instructor;
- student-facing tutor;
- driver readiness scorer;
- licensing evaluator;
- vehicle-control system;
- real-time in-car intervention;
- interior audio system.

Required boundary:

```text
Fake/demo data only. Instructor-reviewed. Post-drive only. No interior audio. No vehicle control. No licensing decisions.
```

---

## 3. Recommended Google Cloud Architecture

Use two deployable surfaces:

```text
Laravel / React / Inertia web app
  -> Cloud Run

Python ADK agent service
  -> Vertex AI Agent Engine OR Cloud Run
```

### Why two surfaces?

The web app should own the instructor workflow:

- dashboard;
- scenario intake form;
- review screen;
- approve/edit/reject/regenerate buttons;
- reviewed demo log;
- inspector panel;
- public scope/safety page.

The Python ADK agent service should own agent orchestration:

- orchestrator agent;
- specialized agent modules;
- tool contracts;
- Gemini calls;
- structured JSON responses.

This keeps Laravel focused on product workflow and keeps the agent runtime aligned with Google’s ADK / Agent Engine path.

---

## 4. Primary Google Cloud Tools

### 4.1 Gemini API / Vertex AI Gemini

Purpose:

```text
Gemini is the reasoning engine.
```

Use Gemini for:

- scenario organization;
- observed safety concern extraction;
- draft debrief note generation;
- reflection prompt generation;
- family-friendly summary generation;
- language-access preview.

Rules:

- Gemini output is always a draft.
- Gemini does not approve logs.
- Gemini does not make licensing, grading, readiness, diagnostic, or vehicle-control decisions.
- Instructor review is required before save.

---

### 4.2 Agent Development Kit / ADK

Purpose:

```text
ADK is the orchestration layer.
```

Use ADK to define:

- Orchestrator Agent;
- Scenario Intake Agent;
- Lesson Retrieval Agent;
- Debrief Draft Agent;
- Reflection / Family Summary Agent;
- Language Access Agent;
- Review Gate / Audit Log Agent.

ADK may be implemented as:

- true ADK agents;
- ADK tools;
- ADK-ready service modules;
- staged implementation where service classes become ADK tools later.

---

### 4.3 Vertex AI Agent Engine

Purpose:

```text
Managed deployment and scaling for the agent service.
```

Use Agent Engine if the project can complete Python ADK packaging cleanly before submission.

If Agent Engine setup slows the team down, deploy the Python ADK service to Cloud Run first, then document Agent Engine as the next step.

Decision rule:

```text
Track 1 demo must work first.
Agent Engine is ideal.
Cloud Run is acceptable if Agent Engine becomes a time blocker.
```

---

### 4.4 Cloud Run

Purpose:

```text
Deploy the web app and/or agent service as containers.
```

Use Cloud Run for:

- Laravel/React web app;
- public demo URL;
- optional Python ADK service;
- fast iteration and deployment.

Cloud Run should be the default deploy target for the public demo because it is simpler than GKE.

Do not use GKE unless required. GKE is overkill for the hackathon MVP.

---

### 4.5 Artifact Registry

Purpose:

```text
Store container images for Cloud Run.
```

Use Artifact Registry for:

- web app image;
- agent service image;
- versioned deploys.

Naming idea:

```text
us-west1-docker.pkg.dev/PROJECT_ID/opendrive-agent/web
us-west1-docker.pkg.dev/PROJECT_ID/opendrive-agent/adk-agent
```

---

### 4.6 Cloud Build

Purpose:

```text
Build containers and optionally automate deploys.
```

Use Cloud Build after local Docker deploy works.

Build order:

1. manual deploy;
2. scripted deploy;
3. Cloud Build / GitHub trigger only if time allows.

---

### 4.7 Secret Manager

Purpose:

```text
Store secrets outside code and Git.
```

Use Secret Manager for:

- Gemini / Vertex configuration;
- app keys;
- OAuth/client credentials if used;
- database credentials if moved beyond SQLite;
- any private service tokens.

Never commit:

- `.env`;
- Google service account JSON;
- API keys;
- OAuth client secrets;
- production credentials.

---

### 4.8 Cloud Logging

Purpose:

```text
Prove traceability and debug the demo.
```

Log:

- agent run started;
- scenario parsed;
- lesson context retrieved;
- draft generated;
- waiting for instructor review;
- instructor approved/rejected;
- reviewed demo log saved.

Do not log:

- real student data;
- real parent data;
- raw private notes in production;
- secrets;
- raw model prompts containing sensitive data.

---

### 4.9 Vertex AI Search / RAG Later

Purpose:

```text
Ground lesson retrieval.
```

MVP should start with a small local demo lesson library:

- 12 fake scenarios;
- 12 public-safe lesson focus records;
- Spanish glossary preview;
- no production OpenDrive private content unless rewritten as demo-safe summaries.

Stretch:

- Vertex AI Search;
- Cloud Storage demo docs;
- BigQuery demo logs;
- custom embeddings/RAG.

Do not block Track 1 on full Vertex AI Search.

---

### 4.10 BigQuery Later

Purpose:

```text
Analytics and reviewed demo logs later.
```

Do not use BigQuery as the first database.

Use BigQuery later for:

- anonymized demo workflow analytics;
- aggregate agent trace events;
- research-style reporting;
- future Beacon research exports after consent/review design exists.

MVP can use SQLite or simple database records.

---

### 4.11 A2A Later

Purpose:

```text
Track 3 interoperability.
```

Do not block Track 1 on A2A.

Track 3 stretch may include:

- `agent-card.json`;
- A2A-ready endpoint description;
- service account / agent identity notes;
- future enterprise interoperability page.

---

## 5. Required Multi-Agent Design

### 5.1 Orchestrator Agent

Responsibilities:

- receive structured scenario request;
- call specialized tools/agents in order;
- enforce JSON schema;
- enforce human-review gate;
- return trace events.

Inputs:

```json
{
  "scenario_text": "Student braked late near a marked crosswalk.",
  "location_type": "residential",
  "instructor_notes": "Student noticed pedestrian late.",
  "language_preview": "Spanish"
}
```

Outputs:

```json
{
  "run_id": "demo-run-001",
  "status": "waiting_for_instructor_review",
  "draft": {},
  "trace": []
}
```

---

### 5.2 Scenario Intake Agent

Tool contract:

```text
parse_scenario()
```

Purpose:

```text
Turn free-text instructor notes into structured public-safe fields.
```

Output example:

```json
{
  "observed_safety_concern": "late hazard recognition near crosswalk",
  "location_type": "residential",
  "suggested_lesson_focus": "visual scanning and crosswalk anticipation",
  "confidence": "demo_only"
}
```

---

### 5.3 Lesson Retrieval Agent

Tool contract:

```text
retrieve_lesson_context()
```

Purpose:

```text
Retrieve public-safe demo lesson context.
```

MVP retrieval source:

```text
resources/demo-data/lesson_focus_records.json
```

Output example:

```json
{
  "lesson_focus": "visual scanning",
  "practice_focus": "identify crosswalks before arrival",
  "source_title": "Demo Lesson Focus: Crosswalk Awareness",
  "source_type": "public_safe_demo_record"
}
```

---

### 5.4 Debrief Draft Agent

Tool contract:

```text
draft_debrief_note()
```

Purpose:

```text
Create an instructor-reviewed draft post-drive note.
```

Required label:

```text
DRAFT — INSTRUCTOR REVIEW REQUIRED
```

---

### 5.5 Reflection / Family Summary Agent

Tool contracts:

```text
generate_reflection_prompt()
generate_family_summary()
```

Purpose:

```text
Create a reflection prompt and family-friendly summary for instructor review.
```

Must avoid:

- blame;
- diagnosis;
- readiness decisions;
- official grading;
- language that says the AI taught or evaluated the student.

---

### 5.6 Language Access Agent

Tool contract:

```text
generate_language_preview()
```

Purpose:

```text
Generate a language-access preview.
```

Required disclaimer:

```text
Instructor-reviewed language-access preview. Not an official translation.
```

---

### 5.7 Review Gate / Audit Log Agent

Tool contract:

```text
save_reviewed_demo_log()
```

Purpose:

```text
Save the reviewed demo log only after instructor approval.
```

Hard rule:

```text
This tool may only run after instructor approval.
```

Required fields:

```json
{
  "review_status": "approved_by_instructor",
  "reviewed_by": "demo_instructor",
  "reviewed_at": "timestamp",
  "audit_hash": "hash",
  "demo_mode": true
}
```

---

## 6. Required Inspector Panel

Build an inspector panel in the web app.

It should show:

```text
Step 1: Scenario parsed
Step 2: Observed safety concern organized
Step 3: Lesson context retrieved
Step 4: Draft debrief note generated
Step 5: Reflection prompt generated
Step 6: Family summary generated
Step 7: Language-access preview prepared
Step 8: Waiting for instructor approval
Step 9: Reviewed demo log saved
```

This panel proves:

- this is not a chatbot;
- the workflow has multiple steps;
- the system waits for human approval;
- meaningful action occurs only after review.

---

## 7. Repository Structure Recommendation

```text
opendrive-clipboard/
├── README.md
├── LICENSE
├── .env.example
├── docs/
│   ├── GOOGLE_AI_AGENTS_CHALLENGE_RULES_REVIEW.md
│   ├── GOOGLE_CLOUD_AGENT_SETUP_PLAN.md
│   ├── ADK_AGENT_DESIGN.md
│   ├── DEMO_SCOPE_AND_SAFETY.md
│   ├── GOOGLE_CLOUD_ARCHITECTURE_MAP.md
│   └── TRACK_3_A2A_STRETCH_PLAN.md
├── web/
│   └── Laravel app
├── agent/
│   ├── README.md
│   ├── requirements.txt
│   ├── app/
│   │   ├── agent.py
│   │   ├── tools.py
│   │   ├── schemas.py
│   │   └── prompts.py
│   └── tests/
├── resources/
│   └── demo-data/
│       ├── scenarios.json
│       ├── lesson_focus_records.json
│       └── glossary_es.json
├── deploy/
│   ├── cloud-run-web.md
│   ├── cloud-run-agent.md
│   ├── agent-engine.md
│   └── secret-manager.md
└── scripts/
    ├── dev-check.sh
    ├── deploy-web-cloud-run.sh
    └── deploy-agent-cloud-run.sh
```

If using one Laravel repo instead of monorepo, keep the Python ADK service under:

```text
agent/
```

Do not mix agent secrets into Laravel config.

---

## 8. Google Cloud Setup Checklist

### 8.1 Pick project

Set:

```bash
export PROJECT_ID="YOUR_PROJECT_ID"
export REGION="us-west1"
gcloud config set project "$PROJECT_ID"
gcloud config set run/region "$REGION"
```

Recommended region:

```text
us-west1
```

or another US region available to your account.

### 8.2 Enable APIs

Use only what the MVP needs first:

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

Optional later:

```bash
gcloud services enable discoveryengine.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
```

### 8.3 Create Artifact Registry repo

```bash
gcloud artifacts repositories create opendrive-agent \
  --repository-format=docker \
  --location="$REGION" \
  --description="OpenDrive Clipboard containers"
```

### 8.4 Create service accounts

Create separate service accounts:

```bash
gcloud iam service-accounts create opendrive-web-runner \
  --display-name="OpenDrive web Cloud Run runtime"

gcloud iam service-accounts create opendrive-agent-runner \
  --display-name="OpenDrive ADK agent runtime"
```

Principle:

```text
Least privilege. Separate web service from agent service.
```

Do not use broad default service accounts unless there is no alternative.

### 8.5 Create secrets

Example:

```bash
printf "VALUE_HERE" | gcloud secrets create GEMINI_API_KEY --data-file=-
```

or for Vertex AI configuration, prefer workload identity / service account permissions instead of raw keys where possible.

### 8.6 Local auth

For local dev:

```bash
gcloud auth login
gcloud auth application-default login
```

For deployment:

```bash
gcloud auth configure-docker "$REGION-docker.pkg.dev"
```

---

## 9. Deployment Path

### Option A — Fastest Track 1 path

```text
Web app -> Cloud Run
Agent service -> Cloud Run
Gemini -> API / Vertex AI
```

Pros:

- fastest;
- easier debugging;
- good enough for Track 1;
- can show inspector panel and meaningful action.

Cons:

- less “enterprise Agent Engine” polish.

### Option B — Stronger Google-native path

```text
Web app -> Cloud Run
Agent service -> Vertex AI Agent Engine
Gemini -> Vertex AI
```

Pros:

- stronger Google Cloud alignment;
- closer to challenge language;
- better Track 3 story.

Cons:

- more setup;
- Python packaging and IAM may slow progress.

### Recommended

Build in this order:

1. Local web app + local agent service.
2. Cloud Run web app + Cloud Run agent service.
3. Agent Engine deployment if time allows.
4. A2A stretch documentation after the working demo.

---

## 10. Environment Variables

### Web app

```env
APP_NAME="OpenDrive Clipboard"
APP_ENV=local
APP_DEBUG=true
APP_URL=http://localhost:8000

AGENT_SERVICE_URL=http://localhost:8081
DEMO_MODE=true
SAVE_REVIEWED_LOG_REQUIRES_APPROVAL=true
INTERIOR_AUDIO_ENABLED=false
```

### Agent service

```env
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-west1
GEMINI_MODEL=gemini-2.5-pro
DEMO_MODE=true
INTERIOR_AUDIO_ENABLED=false
```

Model name should be verified against currently available Gemini models in the user’s Google Cloud project before coding.

---

## 11. Dev / Build Commands

### Laravel web app

```bash
composer install
npm install
cp .env.example .env
php artisan key:generate
php artisan migrate --seed
npm run build
php artisan test
php artisan serve
```

### Python agent service

```bash
cd agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
python app/server.py
```

### Docker build examples

```bash
docker build -t "$REGION-docker.pkg.dev/$PROJECT_ID/opendrive-agent/web:latest" ./web
docker build -t "$REGION-docker.pkg.dev/$PROJECT_ID/opendrive-agent/adk-agent:latest" ./agent
```

### Push images

```bash
docker push "$REGION-docker.pkg.dev/$PROJECT_ID/opendrive-agent/web:latest"
docker push "$REGION-docker.pkg.dev/$PROJECT_ID/opendrive-agent/adk-agent:latest"
```

### Deploy to Cloud Run

```bash
gcloud run deploy opendrive-debrief-web \
  --image "$REGION-docker.pkg.dev/$PROJECT_ID/opendrive-agent/web:latest" \
  --region "$REGION" \
  --service-account "opendrive-web-runner@$PROJECT_ID.iam.gserviceaccount.com" \
  --allow-unauthenticated

gcloud run deploy opendrive-debrief-agent \
  --image "$REGION-docker.pkg.dev/$PROJECT_ID/opendrive-agent/adk-agent:latest" \
  --region "$REGION" \
  --service-account "opendrive-agent-runner@$PROJECT_ID.iam.gserviceaccount.com" \
  --no-allow-unauthenticated
```

If the web app needs to call the private agent service, configure authenticated service-to-service calls or temporarily allow restricted access only for demo development.

---

## 12. Security / Safety Rules

Do not commit:

- `.env`;
- service account JSON;
- API keys;
- OAuth secrets;
- real student data;
- production OpenDriveEDU data;
- Beacon production data;
- Vault data;
- interior audio data;
- raw sensor logs.

Hardcoded safety flags:

```text
DEMO_MODE=true
INTERIOR_AUDIO_ENABLED=false
SAVE_REVIEWED_LOG_REQUIRES_APPROVAL=true
```

No tool can save a log without instructor approval.

---

## 13. Work Plan

### Task 0 — Docs first

Create:

```text
docs/GOOGLE_AI_AGENTS_CHALLENGE_RULES_REVIEW.md
docs/GOOGLE_CLOUD_AGENT_SETUP_PLAN.md
docs/ADK_AGENT_DESIGN.md
docs/DEMO_SCOPE_AND_SAFETY.md
docs/GOOGLE_CLOUD_ARCHITECTURE_MAP.md
docs/TRACK_3_A2A_STRETCH_PLAN.md
```

Commit docs before code.

### Task 1 — Demo data

Create:

```text
resources/demo-data/scenarios.json
resources/demo-data/lesson_focus_records.json
resources/demo-data/glossary_es.json
```

Use fake/demo data only.

### Task 2 — Web workflow

Build:

```text
Dashboard
New Demo Scenario
Draft Debrief Note Review
Language-Access Preview
Reviewed Demo Log
Scope Page
Inspector Panel
```

### Task 3 — Agent service skeleton

Build:

```text
agent/app/agent.py
agent/app/tools.py
agent/app/schemas.py
agent/app/prompts.py
agent/tests/
```

### Task 4 — Wire web app to agent service

Web app calls agent service.

Agent service returns structured JSON and trace steps.

### Task 5 — Human review gate

Implement:

```text
Approve
Edit
Reject
Regenerate
Save reviewed demo log
```

Save requires approval.

### Task 6 — Cloud Run deployment

Deploy web app and agent service to Cloud Run.

### Task 7 — Agent Engine deployment

Try Agent Engine if Track 1 demo is already working.

### Task 8 — Submission package

Create:

```text
README
screenshots
demo video script
architecture diagram
Devpost answers
rules compliance checklist
```

---

## 14. Stop Conditions

Stop and report if:

- ADK dependency conflicts with local Python;
- Gemini model access is blocked;
- Google Cloud billing/project setup is incomplete;
- Cloud Run deploy fails with unclear IAM errors;
- Agent Engine deploy blocks Track 1 progress;
- save_reviewed_demo_log can run without approval;
- any real student data appears;
- any interior audio feature appears;
- app is framed as AI instructor or student-facing autonomous teacher.

---

## 15. Track 1 Definition of Done

The Track 1 build is done when:

- web app is deployed or demoable;
- instructor enters fake scenario;
- agent workflow runs;
- inspector panel shows steps;
- draft debrief note appears;
- reflection prompt appears;
- family summary appears;
- language preview appears;
- instructor approves/rejects/regenerates;
- reviewed demo log saves only after approval;
- README explains Google Cloud / Gemini / ADK usage;
- demo uses fake data only;
- no interior audio;
- no vehicle control;
- no licensing/readiness decisions.

---

## 16. Track 3 Stretch Definition of Done

Only after Track 1 works:

- Cloud Run deployment hardened;
- Agent Engine deployment attempted or completed;
- A2A readiness documented;
- service accounts separated;
- agent card draft created;
- enterprise/B2B architecture page written.

---

## 17. Final Build Command

Use this command instruction:

```text
Do not start coding until docs/GOOGLE_AI_AGENTS_CHALLENGE_RULES_REVIEW.md and docs/GOOGLE_CLOUD_AGENT_SETUP_PLAN.md exist and have been read.

Build Track 1 first.

Keep Track 3 as stretch.

Use Gemini for reasoning.

Use ADK or ADK-ready orchestration.

Deploy to Google Cloud.

Use fake/demo data only.

No interior audio.

No vehicle control.

No AI instructor.

The reviewed demo log may save only after instructor approval.
```

---

## DOL Drive Sheet Grader (added 2026-05-13)

A second drafting artifact runs alongside the debrief: a **DOL-aligned drive
sheet draft + detailed student report**, modeled on WA DOL form **DTS-661-047
(N/12/24)** "Driver Training School Behind-the-Wheel Instruction Log"
(`docs/dol drive sheet.pdf`). The form has three sections — §1 drive log, §2
skill grid rated 1-4, §3 comments + reaction to coaching. Licensed instructors
already fill this by hand after every BTW lesson; Clipboard drafts it.

**Modules.**
- `opendrive_clipboard/dol_sheet.py` — canonical form constants
  (51 skill rows in form order, 1-4 rating scale verbatim from the DOL rubric,
  scenario-pattern → DOL-skill mapping).
- `opendrive_clipboard/beacon_demo.py` — deterministic synthetic Beacon
  recording (CAN, IMU, GPS, forward-camera text labels, intervention taps).
  `meta.has_audio` is always `False`; no `audio` / `microphone` / `cabin`
  keys exist anywhere in the payload.
- `opendrive_clipboard/grader.py` — deterministic rule-based grader that
  produces: §2 skill ratings with rationales, a blood-panel snapshot
  (smooth braking, throttle smoothness, mean following distance, peak
  lateral accel, mirror cadence, intervention count, lane-position variance,
  each with a reference range and an ok/watch/concern flag), an eco score
  (0-100, three bands), a calm/tentative/aggressive attitude profile that
  sums to 100, strengths/gaps lists, and a §3 comments draft + suggested
  reaction-to-coaching value.
- `opendrive_clipboard/tools.py::DriveSheetTools` — MCP-style wrapper.
- `opendrive_clipboard/agent.py::DriveSheetGraderAgent` — adds a single
  trace entry and attaches `drive_report` to the run payload.

**Deterministic numbers + optional Gemini prose split.**
Every 1-4 rating and every blood-panel number is computed by deterministic
rules over the synthetic telemetry. Two runs against the same scenario id
produce byte-identical JSON (guarded by tests). The existing optional Gemini
provider remains constrained to prose generation only — it never alters a
rating or a panel value. This preserves judge-reproducibility while leaving
room for richer narrative when a key is configured.

**Hard boundaries restated in code.**
- Every report ships with `status = DRAFT_INSTRUCTOR_REVIEW_REQUIRED` and
  `instructor_review_required = True`.
- Every payload carries `has_audio: False` and a `no_microphone_disclosure`
  string, both greppable.
- The grader does not write to DOL, an LMS, a transcript, or a certificate.
  It drafts a form for the licensed instructor to review.
- The blood panel, eco score, and attitude profile carry explicit
  "synthetic, derived from mock telemetry" disclosures.

**Server surface.**
- `GET /drive-sheet` — the workspace page.
- `POST /api/drive-reports` — runs the grader for a scenario.
- `GET /api/drive-reports/<id>` — fetches a saved draft.
- `PATCH /api/drive-reports/<id>/review` — records the instructor decision.

**UI.**
`web/drive-sheet.html` + `web/drive-sheet.js` render the synthetic Beacon
strip, the §1 drive log card, the §2 skill grid (collapsible by group, with
rationale tooltips and instructor-override dropdowns), the blood-panel table,
an SVG eco gauge, the attitude bar, strengths/gaps, the §3 comment textarea
with reaction-to-coaching radios, and the Approve / Edit / Reject / Regenerate
review-gate buttons. No external assets, no chart library.

