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

Proof of concept

### Which specific feature of Agent Platform was most critical to your project's impact, and what is one thing it's currently missing?

The most critical feature is ADK-style agent orchestration: the ability to break one business workflow into specialized agent steps instead of producing a single chatbot response.

For OpenDrive Clipboard, the workflow needs to parse a demo driving scenario, retrieve lesson context, draft a post-drive debrief note, generate reflection and family-summary support, prepare a language-access preview, and then pause at a human-review gate before saving a reviewed demo log.

I am currently at the idea / early prototype stage and have not shipped on Agent Platform yet. As of 2026-05-01, the opendrive-clipboard GCP project is provisioned, billing is linked, required APIs are being enabled, and a Gemini 2.5 Flash round-trip is working under ADC. The next build phases are ADK agent setup, MCP tool wiring, and Cloud Run deployment.

The thing I would value most is a first-class human-review gate pattern for safety-sensitive workflows. It would help if Agent Platform had a standard reviewed-action template where an agent can draft, retrieve, and summarize, but cannot save, send, submit, or publish until a human approves.

### If you could add one specific API capability or integration that would have saved you 2+ hours of work, what would it be?

A first-class ADK MCP scaffold: generate typed tool schemas, test stubs, agent wiring, and Cloud Run deploy files from Python functions. MCP wiring and container packaging are the slowest path from prototype to hosted demo.
