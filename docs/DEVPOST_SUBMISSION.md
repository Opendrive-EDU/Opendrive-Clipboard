# Devpost Submission Draft

## Project

OpenDrive Clipboard

## Problem To Solve

Behind-the-wheel lessons should be learning experiences, not pass/fail moments or overwhelming correction lists.

In a good drive lesson, the student is practicing skills and drills, learning as they go, and receiving simple follow-up from the instructor: "work on this next." But in real-world instruction, two problems can happen. Some lessons drift toward evaluation-heavy instruction, where the student feels like every drive is a test. Other lessons end with too many corrections at once, leaving the student discouraged or unsure what actually matters most.

Students need clear, respectful feedback they can digest. A young adult, international student, or student without strong practice support at home may need more than "brake earlier" or "watch your speed." They need to understand the specific skill to work on, why it matters, and what practice step comes next.

OpenDrive Clipboard helps licensed instructors turn teachable moments into instructor-reviewed debriefs that are simple, structured, and evidence-informed. A moment such as taking right turns too fast, missing signals, drifting into one-handed control, following too closely, or braking late can become a clear practice focus without turning the debrief into criticism or shame.

The goal is not to replace instructor judgment. The goal is to help instructors preserve the lesson, connect observations to specific skills, and send students home with respectful next steps they can actually use.

AI organizes the moment. The instructor leads the lesson.

## Our Solution

OpenDrive Clipboard is a Gemini-powered, ADK-ready agent workflow that drafts post-drive debrief materials for a licensed instructor to review and approve.

It runs after the lesson, not during the drive. It does not exist in the vehicle cabin. It does not capture interior audio. It does not control the vehicle, grade readiness, make licensing decisions, or communicate with the student during a drive.

The agent takes a demo driving scenario, such as late braking near a crosswalk, residential speed creep, following too closely, missed signaling, or yellow-light indecision, and produces an instructor-ready draft containing:

1. Safety summary
2. Observed safety concern
3. Suggested lesson focus
4. Student reflection prompt
5. Practice assignment
6. Family-friendly summary
7. Language-access preview
8. Reviewed demo log entry

Every output is marked: `DRAFT - INSTRUCTOR REVIEW REQUIRED`.

The draft is held at a hard human-review gate. The licensed instructor clicks Approve, Edit, Reject, or Regenerate. Nothing reaches a student or family without the instructor's sign-off. This is the product's safety boundary, regulatory boundary, and core differentiator.

Architecture:

- Gemini for reasoning and classification
- Google ADK / ADK-ready orchestration
- Typed tool layer for demo drive events, lesson-context retrieval, debrief drafting, language-access preview, and instructor review decisions
- Instructor review-gate dashboard
- Google Cloud Run deployment target for the dashboard and agent services

The public demo uses demo data only: no real student records, no PII, no production OpenDrive Beacon data, no interior audio, and no production secrets in the public repo.

Two products, one umbrella:

OpenDrive Beacon is the private in-vehicle evidence layer: CAN bus, IMU, GPS, and forward-road camera data for future instructor-reviewed post-drive analysis.

OpenDrive Clipboard is this public hackathon submission: the post-drive drafting and review layer that turns demo driving scenarios into instructor-reviewed debrief materials.

Beacon records. Clipboard drafts. The licensed instructor decides.

Regulatory posture:

OpenDrive Clipboard supports licensed-instructor documentation and review. AI-assisted note drafting is treated as a documentation aid for the licensed professional, similar to a digital intake form, structured event log, or lesson-summary drafting aid.

The system is not an automated driving instructor, vehicle-control system, licensing evaluator, diagnostic tool, enforcement tool, or readiness grader.

OpenDrive, OpenDrive Beacon, and OpenDrive Clipboard are working names of Street Law OpenDrive.

## Submission Questions

### On a scale from 1-5, how familiar are you with Google Cloud products?

1

### On a scale from 1-5, how familiar are you with Google AI Studio?

2

### Describe the readiness of your project for launch.

Beta. The public demo is live on Google Cloud Run (project `opendrive-clipboard`, service `opendrive-clipboard-demo`, region `us-central1`) with `allUsers` granted `roles/run.invoker`, returning 200 to anyone with the URL. The branded apex domain `opendriveclipboard.com` is purchased and DNS verification + Cloud Run domain mapping are in progress. The full repo — agent workflow, MCP-style typed tools, Cloud Run Dockerfile, deploy script, 26-test suite, product/architecture/boundary docs — is public under Apache 2.0. The deterministic local draft provider is the default on the public demo so reviewers can evaluate the agent workflow without a Gemini API key; the optional Gemini 2.5 Flash provider can be flipped on via the `OPENDRIVE_CLIPBOARD_ENABLE_GEMINI` environment flag.

### Which specific feature of Agent Platform was most critical to your project's impact, and what is one thing it's currently missing?

The most critical feature is ADK-style multi-agent orchestration: breaking one business workflow into specialized agent steps with typed tool boundaries between them, instead of producing a single chatbot response.

OpenDrive Clipboard runs five specialized agents chained by typed MCP-style tools — Scenario Intake, Curriculum Retrieval, Draft Assembly, Review Gate, and Drive Sheet Grader. The Review Gate agent halts the workflow at `DRAFT - INSTRUCTOR REVIEW REQUIRED` and cannot advance until the licensed instructor clicks Approve, Edit, Reject, or Regenerate. Every output carries the draft-state label; nothing reaches a student or family without instructor sign-off. As of 2026-05-14 the workflow is live on Cloud Run with the deterministic provider as default and the Gemini 2.5 Flash provider available via environment flag.

The thing I would value most from Agent Platform is a first-class human-review-gate primitive for safety-sensitive workflows. The pattern Clipboard implements — agent drafts, retrieves, and summarizes but cannot save, send, submit, or publish until a human approves — should be a stock template with built-in audit trail and decision capture, not something each team rebuilds. A standard reviewed-action state machine would speed adoption in regulated domains: driving instruction, healthcare documentation, education record-keeping, anywhere a licensed human is the legal authority and the agent is a drafting aid.

### If you could add one specific API capability or integration that would have saved you 2+ hours of work, what would it be?

A first-class ADK MCP scaffold: generate typed tool schemas, test stubs, agent wiring, and Cloud Run deploy files from Python functions. MCP wiring and container packaging are the slowest path from prototype to hosted demo.

A close second: Marketplace billing + Identity Token auth that Cloud Run could mount as a sidecar. Productizing the agent past the demo means per-tenant auth, usage metering, and Marketplace integration — all currently bespoke work that would benefit from a stock template.

## Production plan

OpenDrive Clipboard's productization target is the **Google Cloud AI Agent Marketplace** (not the generic Cloud Marketplace SaaS listing). The Devpost submission is the public demo; the Marketplace listing is the commercial path that follows. The architecture decisions in this repo — Cloud Run packaging, multi-agent decomposition, typed MCP-style tools, hard review gate, ADK-ready agent surface — are the same decisions the Marketplace listing will lean on. No throwaway scaffolding.

### Phase A — Devpost submission (now → 2026-06-05)

- Public demo live on Cloud Run (`opendrive-clipboard-demo`, project `opendrive-clipboard`, region `us-central1`, `allUsers` → `roles/run.invoker`).
- Branded apex `opendriveclipboard.com` purchased; TXT verification + Cloud Run domain mapping + A/AAAA records in flight at Network Solutions.
- Architecture intentionally ADK-ready — specialized agents and typed MCP-style tools structured to wrap cleanly in `google.adk.agents.Agent` later — but with no hard dependency on `google-adk` so judges can run the demo without external network calls.

### Phase B — Standalone-ready ADK conversion (2026-06-06 → 2026-08-31)

Sold to WA-DOL-licensed BTW driving schools whether or not they use OpenDrive Beacon hardware. Standalone scenario intake = instructor types or dictates a post-drive scenario in free text or picks from a dropdown. No Beacon dependency for buyers.

- Wrap `opendrive_clipboard/agent.py` in `google.adk.agents.Agent`; convert `tools.py` MCP-style stubs to ADK function-calling tools.
- Flip Gemini default ON for paying tenants; deterministic provider stays default on the free public demo so reviewers can always smoke-test offline.
- Multi-tenancy: per-tenant scenario isolation, per-tenant audit log, per-tenant instructor accounts.
- Cloud SQL Postgres for per-tenant scenario history; Marketplace Identity Token auth; Cloud Logging + Cloud Trace.
- Pilot with 2–3 WA driving schools. **Gate to Phase C:** 50 real instructor-approved drafts, < 30 % edit distance vs. final approved text, zero false student deliveries (the review gate held every time).

### Phase C — AI Agent Marketplace listing (2026-09-01 → 2026-11-30)

- Producer Portal listing application. Counsel review of trademark + Terms of Service + Privacy Policy + Producer Agreement (trademark filings precede commercial listing per brand posture).
- Marketplace usage metering wired (per-draft or per-seat). Pricing model decided on Phase B pilot data — recommended starting point: $25 / instructor / month subscription, or $2 per draft, whichever is greater, capped at $200 / school / month.
- AI safety disclosure documented around the existing `DRAFT - INSTRUCTOR REVIEW REQUIRED` boundary — the same boundary that gates the public demo gates the paid product.

### Phase D — Live in Marketplace (Q1 2027)

- 4–12 week Google review window after Phase C submission. Address reviewer feedback on security, billing, copy.
- Public listing at `console.cloud.google.com/marketplace/.../opendrive-clipboard`. Marketing landing on `opendriveclipboard.com/marketplace`.
- Outbound to WA driving schools → OR, ID → national. **KPI:** 10 paying schools / 50 instructor seats by Q3 2027.

### Why AI Agent Marketplace, not generic SaaS Marketplace

- Brand fit: Gemini / ADK-built agents belong in the agent storefront, not buried in generic SaaS.
- Lower revenue share (~3 % vs ~10–20 %).
- Devpost AI Agents Challenge winners are fast-tracked through listing review.
- The Devpost narrative and the Marketplace narrative are the same story — multi-agent workflow with a hard review gate, sold to a regulated profession (licensed driving instructors). Judging reviewers and listing reviewers see the same architecture.
