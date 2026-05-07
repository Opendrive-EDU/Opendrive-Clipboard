# OpenDrive Clipboard

A public-safe AI agent prototype that helps **licensed driving instructors** turn teachable driving moments into simple, structured, evidence-informed debriefs, student reflection prompts, lesson recommendations, language-access summaries, and audit-style demo logs.

| Field | Value |
|---|---|
| Organization | Street Law OpenDrive / OpenDriveEDU |
| Prepared for | Google / Devpost AI Agents Challenge planning |
| Owner | Mr. Law — Founder, Lead Instructor, and Product Lead |
| Build lane | OpenDrive AI Lab — prototype/testing lane before production use |
| Prototype boundary | Fake/demo data only; instructor-supervised; not a licensing or vehicle-control tool |

---

## What this is NOT

**This is not an automated driving instructor.**

- It does not communicate with students during a drive.
- It does not control or assist the vehicle.
- It does not make licensing, grading, or pass/fail decisions.
- It does not run in real-time during behind-the-wheel sessions.

The licensed human instructor remains the sole authority for behind-the-wheel instruction. This tool only generates **post-drive debrief drafts** that the instructor reads, edits, and approves before anything reaches a student or family. Compliant with WA RCW 46.82 + WAC 308-108. See `docs/dol-edu/BEACON-IS-AND-IS-NOT.md` for the full boundary statement.

---

## 1. Executive Summary

OpenDrive Clipboard is a focused, hackathon-safe version of the larger OpenDriveEDU safety vision. It does not try to replace the instructor, run a full LMS, process student records, control a vehicle, or expose OpenDrive Beacon production concepts. It demonstrates one valuable layer: turning a **post-drive teachable moment** into a **reviewed debrief** that the licensed instructor approves before delivery.

The agent receives a demo driving scenario such as late braking near a crosswalk, speed creep in a residential area, or uncertainty at a yellow light. It then organizes the moment into an **instructor-ready debrief note** with a safety summary, risk pattern, suggested lesson focus, reflection prompt, practice assignment, language-access preview, and saved demo log. **The instructor approves, edits, or rejects every output. Nothing reaches a student or family without instructor sign-off.**

---

## 2. Problem Worth Solving

Behind-the-wheel lessons should be learning experiences, not pass/fail moments or overwhelming correction lists.

In a good drive lesson, the student practices skills and drills, learns as they go, and receives simple follow-up from the instructor: "work on this next." But in real-world instruction, some lessons drift toward evaluation-heavy instruction, where the student feels like every drive is a test. Other lessons end with too many corrections at once, leaving the student discouraged or unsure what actually matters most.

Students need clear, respectful feedback they can digest. A young adult, international student, or student without strong practice support at home may need more than "brake earlier" or "watch your speed." They need to understand the specific skill to work on, why it matters, and what practice step comes next.

OpenDrive Clipboard helps licensed instructors preserve teachable moments, connect observations to specific skills, and send students home with respectful next steps.

This problem is especially important when instruction includes young drivers, new adult drivers, international students, language-access needs, and families who need clear after-lesson summaries. The goal is not to create a bigger pile of notes. The goal is to give the licensed instructor a better post-drive debrief workflow.

---

## 3. Target User

| User | Need |
|---|---|
| **Driving instructor** (primary) | Clear post-drive debrief language after a teachable moment; full edit/approve/reject control |
| **Student driver** | A clear reflection prompt and a next practice focus, delivered by the instructor |
| **Family / support person** | A short, plain-language follow-up summary without private system data, delivered by the instructor |

---

## 4. Product Concept

The app is a **web-based instructor dashboard**. The instructor selects or enters a demo event, asks the agent to draft a post-drive debrief note, reviews the note, optionally generates a language-access preview, and saves the **approved** demo record.

| Feature | What it proves in the demo |
|---|---|
| Scenario Intake | A structured form captures a fake/demo drive event, location type, observed concern, and instructor notes. |
| Debrief Draft | Gemini/agent workflow classifies the safety concern and drafts a post-drive debrief note for the instructor to review. |
| Suggested Lesson Focus (instructor confirms) | The agent suggests a lesson focus such as scanning, intersections, speed control, following distance, or emotional self-control — the instructor confirms before it is saved. |
| Reflection Prompt Suggestion (instructor confirms) | The agent drafts a student-friendly reflection question and practice assignment for the instructor to confirm. |
| Language Access Preview | An instructor-reviewed bilingual support preview demonstrates future access for students and families. |
| Human Review Gate | Instructor can approve, edit, reject, or regenerate before anything is saved. **Hard gate, not optional.** |
| Demo Log | Saved workflow records prove the agent completes a real post-drive task beyond chat. |

---

## 5. Agent Workflow

```
Instructor enters demo event
        ↓
Agent classifies safety concern + drafts debrief note
        ↓
Agent suggests lesson focus + reflection prompt
        ↓
[ HUMAN REVIEW GATE — instructor approves / edits / rejects ]
        ↓
Approved note saved to demo log (with language-access preview if requested)
```

The Human Review Gate is a hard gate. No output reaches a student or family record without instructor sign-off.

---

## 6. Recommended Hackathon Stack

The prototype should stay clean and demo-focused. The strongest build is a new public repo that references OpenDriveEDU but does not merge private OpenDriveEDU, Beacon, Vault, or production student-data systems.

| Layer | Recommended choice | Reason |
|---|---|---|
| Frontend | React + Inertia + Tailwind | Matches the DriveDesk WA OpenDrive UI lane and keeps Beacon/Clipboard surfaces on the current frontend stack. |
| Backend | Laravel | Strong routing, auth-ready structure, policies, controllers, and service classes. |
| Agent | Gemini + Google Cloud Agent Builder / ADK-ready design | Shows a real agent workflow that classifies, retrieves, drafts, **waits for instructor review**, and saves. |
| Data | MongoDB or SQLite demo store; BigQuery later | MongoDB is strong for partner-track retrieval; SQLite keeps local demo simple; BigQuery fits future research logs. |
| Language access | Curated glossary + Gemini/Translation preview | Safe preview of bilingual support without claiming official translation. |
| Deployment | Hosted web demo; Google Cloud Run is a good target | Easy for judges to test; aligns with Google Cloud. |

---

## 7. Simple Architecture

```
Instructor Web UI
        ↓
Laravel Services (routes, policies, workflow records)
        ↓
Agent + Tool Layer (Gemini reasoning, lesson retrieval, language preview)
        ↓
[ HUMAN REVIEW GATE ]
        ↓
Reviewed Output (approved debrief note, audit-style demo log)
```

---

## 8. Public Repo Boundary

A new public repository, demo data only, no live student PII, no Beacon production secrets, complete open-source license visible.

---

## 9. MVP Pages for the Demo

| Page | Purpose |
|---|---|
| Dashboard | Explains the mission, shows demo status, and starts the workflow. |
| New Demo Event | Instructor enters a fake driving situation and submits it to the agent. |
| Debrief Note Review | Agent output appears with approve, edit, reject, and regenerate actions. **The hard human-review gate.** |
| Language Access Preview | Shows instructor-reviewed bilingual support for the approved note. |
| Demo Log | Shows saved workflow records and proves the agent completed a post-drive task. |
| Boundary | Links to `docs/dol-edu/BEACON-IS-AND-IS-NOT.md` — explicit IS / IS NOT statement for any regulator, judge, or partner who lands on the demo. |
| Public Safety / Architecture | Explains why the project matters and how the agent/tool layers work, with the human-review gate called out. |

---

## 10. Three-Minute Demo Script

| Time | What to show |
|---|---|
| 0:00–0:25 | Problem: instructors need a fast, safer way to turn post-drive moments into reviewed debrief notes. |
| 0:25–0:55 | Enter a fake event: late braking near a crosswalk, speed pressure, or yellow-light indecision. |
| 0:55–1:35 | Run the agent: classify risk, retrieve lesson context, draft post-drive debrief note. |
| 1:35–2:10 | **Instructor review (on-screen text: "the human instructor reviews and approves before anything is saved")**: edit/approve; show the human-in-the-loop gate explicitly. |
| 2:10–2:35 | Language-access preview: show support summary and vocabulary disclaimer. |
| 2:35–3:00 | Demo log: saved record, privacy boundary, future roadmap. |

---

## 11. Submission Planning

Current planning assumption: build a public-safe demo early, then use the final days for README, license, deployment, screenshots, demo video, and Devpost form. Confirm the exact deadline and final rules from the acceptance page because public program pages can differ.

| Asset | Status target |
|---|---|
| Hosted demo URL | Working by MVP freeze. |
| Public code repository | New repo only; complete open-source license visible. |
| README + setup instructions | Clear local install, env examples, fake-data seed command. |
| Demo video | About 3 minutes; show workflow, **human review gate**, and privacy boundary. |
| Screenshots | Dashboard, event intake, debrief note review, language preview, demo log, Boundary page. |

---

## Safety statement

Fake data only; not a licensing, diagnostic, enforcement, or vehicle-control tool. Not an automated driving instructor. The licensed human instructor is the sole authority for behind-the-wheel instruction; this tool only drafts post-drive debrief materials for the instructor to review and approve. Operates within WA RCW 46.82 + WAC 308-108.

---

## Source note

This brief replaces and supersedes the prior `OpenDrive_Safety_Coach_Project_Brief.txt` (deprecated 2026-04-30). Renamed and reframed to make the human-instructor authority and post-drive boundary explicit at every public surface. Treat official Devpost contest rules and deadlines as pending until confirmed after acceptance.
