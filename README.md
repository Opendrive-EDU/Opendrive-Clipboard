# OpenDrive Clipboard

> **AI organizes the moment. The instructor leads the lesson.**

OpenDrive Clipboard is the **Devpost submission product** for the [Google for Startups AI Agents Challenge](https://googleforstartups.devpost.com/) (event #3197, due **June 5, 2026 5:00 PM PT**). It helps licensed instructors turn teachable driving moments into simple, structured, evidence-informed debriefs that students can actually use.

**Tagline:** *Beacon records. Clipboard drafts. The licensed instructor decides.*

## Problem to solve

Behind-the-wheel lessons should be learning experiences, not pass/fail moments or overwhelming correction lists.

In a good drive lesson, the student practices skills and drills, learns as they go, and receives simple follow-up from the instructor: "work on this next." But in real-world instruction, two problems can happen. Some lessons drift toward evaluation-heavy instruction, where the student feels like every drive is a test. Other lessons end with too many corrections at once, leaving the student discouraged or unsure what actually matters most.

Students need clear, respectful feedback they can digest. A young adult, international student, or student without strong practice support at home may need more than "brake earlier" or "watch your speed." They need to understand the specific skill to work on, why it matters, and what practice step comes next.

OpenDrive Clipboard helps licensed instructors turn moments such as taking right turns too fast, missing signals, drifting into one-handed control, following too closely, or braking late into instructor-reviewed debriefs that are simple, structured, and evidence-informed.

The goal is not to replace instructor judgment. The goal is to help instructors preserve the lesson, connect observations to specific skills, and send students home with respectful next steps.

---

## What it does

OpenDrive Clipboard receives a fake / demo post-drive scenario, such as late braking near a crosswalk, residential speed creep, following too closely, missed signaling, right turns taken too fast, or yellow-light indecision. It turns that moment into an **instructor-ready draft debrief** with:

- Safety summary
- Observed safety concern
- Suggested lesson focus
- Reflection prompt for the student
- Practice assignment for next session
- Language-access preview
- Saved demo log entry

**Every output is marked `DRAFT — INSTRUCTOR REVIEW REQUIRED` and cannot reach a student or family until the licensed human instructor approves it.** Nothing reaches a delivered state without the instructor's sign-off. This is the regulatory boundary, the product differentiator, and the load-bearing safety claim.

---

## ICP — who this is built for

**Licensed Washington State Behind-the-Wheel (BTW) driving instructors at small driving schools who currently write post-drive notes by hand.** Mr. Law (founder, licensed BTW instructor) is the persona the product is designed for.

The agent is sold to driving schools, not to teen drivers, families, or car manufacturers. The student in the passenger seat is a downstream beneficiary, not a user.

---

## Two products, one umbrella

| Product | Role | Repository |
|---|---|---|
| **OpenDrive Beacon** | In-vehicle sensor stack (CAN, IMU, GPS, forward camera) — passive recorder, no microphone | private mono-repo |
| **OpenDrive Clipboard** *(this repo)* | Post-drive debrief drafting and review agent (Gemini ADK + MCP-style tools + instructor review-gate UI) | this repo |

OpenDrive is the company / umbrella brand sitting above both products.

---

## Status — Synthetic MVP

This repository now includes a dependency-free synthetic MVP:

- Python agent-like workflow with specialized modules for scenario intake, curriculum retrieval, draft assembly, and review gate.
- MCP-style typed tools for synthetic drive context, lesson context, draft creation, and instructor review decisions.
- Browser demo UI served by a tiny Python HTTP server.
- Synthetic scenarios only; no real OpenDrive Beacon records, student PII, or official LMS writes.
- Optional Gemini API provider guarded behind environment variables. The deterministic local provider is the default for reliable judge testing.

Run locally:

```bash
python3 -m unittest discover -s tests
python3 -m opendrive_clipboard.server --host 127.0.0.1 --port 8080
```

Open:

```text
http://127.0.0.1:8080
```

See `docs/DEVPOST_SUBMISSION.md` for the submission copy, `docs/SUBMISSION_PLAN.md` for the full plan, `docs/ENGINEERING_PLAN.md` for the agent architecture, and `docs/PRODUCT_BRIEF.md` for the product spec.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Browser demo UI  (Cloud Run target)                     │
│  - Scenario Intake                                        │
│  - Debrief Note Review (HUMAN-REVIEW GATE — hard stop)   │
│  - Language Access Preview                                │
│  - Demo Log                                               │
│  - Boundary page (links to BOUNDARY.md)                  │
└──────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│  Python agent workflow  (ADK-ready, Gemini optional)     │
│  Loop: plan → MCP tool call → reflect → ... → stop       │
└──────────────────────────────────────────────────────────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
       ┌──────────┐ ┌─────────┐ ┌────────────────┐
       │ beacon-  │ │curric-  │ │ instructor-    │
       │ telemetry│ │ ulum-   │ │ review-tools   │
       │ -tools   │ │ tools   │ │ (MCP)          │
       │ (MCP)    │ │ (MCP)   │ │                │
       └──────────┘ └─────────┘ └────────────────┘
```

---

## Hard boundaries

These are non-negotiable and will not change:

1. **The licensed human instructor is the sole authority.** Clipboard never instructs the student.
2. **No microphone.** The vehicle cabin is never recorded.
3. **`DRAFT — INSTRUCTOR REVIEW REQUIRED`** appears on every agent output. Approval is required before any delivery.
4. **Demo data only in this repo.** No live student records, no PII, no production OpenDrive Beacon secrets.
5. **The agent assists the instructor, never the student.** Clipboard is a post-drive drafting aid, not an automated instructor, automated evaluator, or student tutor.

See `docs/BOUNDARY.md` for the full statement.

---

## License

Apache License 2.0 — see `LICENSE`.

---

## Contact

**Mr. Law (Jason Law)** — Founder + Lead Instructor, Street Law OpenDrive / OpenDriveEDU
mrlaw@streetlawopendrive.com
https://streetlawopendrive.com

---

*OpenDrive™, OpenDrive Beacon™, and OpenDrive Clipboard™ are common-law working names of Street Law OpenDrive. All marks are subject to counsel-led trademark clearance review.*
