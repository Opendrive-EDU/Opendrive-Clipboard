# OpenDrive Clipboard — What It Is and What It Is Not

**For:** Devpost judges, partner driving schools, families, public reviewers, WA DOL
**Author:** Mr. Law (Jason Law), licensed WA BTW instructor, Street Law OpenDrive
**Last updated:** 2026-05-01

This document is the regulatory boundary statement for **OpenDrive Clipboard** (the Devpost AI Agents Challenge submission product) and its relationship to **OpenDrive Beacon** (the in-vehicle sensor stack maintained in the private OpenDriveEDU mono-repo). It mirrors the public-facing `BEACON-IS-AND-IS-NOT.md` shipped at `streetlawopendrive.com/docs/beacon-is-and-is-not.md`.

---

## One sentence

OpenDrive Clipboard is a **post-drive debrief drafting agent** that produces drafts for a licensed human instructor to review and approve. The licensed instructor is, and remains, the **sole authority** during all behind-the-wheel sessions and over all delivered output.

---

## What OpenDrive Clipboard IS

- A **Gemini / ADK-ready agent workflow + MCP-style tools + review-gate UI** that can run on Cloud Run.
- A **drafting assistant** for the licensed instructor: it organizes a post-drive teachable moment into an instructor-ready draft debrief (safety summary, observed safety concern, suggested lesson focus, reflection prompt, practice assignment, language-access preview).
- A **demo-data-only system in this repository.** All scenarios are fake / seeded. No real student records, no real PII, no live OpenDrive Beacon production data, no Vault secrets.
- A **teachable-moment preservation tool**: it helps the instructor connect observations to specific skills and respectful next steps without turning the debrief into criticism or shame.

## What OpenDrive Clipboard IS NOT

- **Not an automated driving instructor.** It does not deliver instruction. It does not speak to the student in the vehicle. It does not exist in the cabin during the drive.
- **Not a coach.** The word "coach" is reserved for the human in the passenger seat. Clipboard does not coach.
- **Not a real-time system.** Clipboard runs **after** the lesson ends. It is not a live intervention or driver-assist system.
- **Not a vehicle-control or driver-assist system.** It does not touch brakes, throttle, steering, signals, or any vehicle subsystem.
- **Not a licensing or grading authority.** It does not issue, recommend, or influence pass/fail decisions. WA DOL standards apply; the licensed instructor evaluates.
- **Not a student-facing surveillance tool.** Outputs are reviewed and approved by the licensed instructor of record, governed by school policy and parental consent.
- **Not a microphone.** Clipboard does not capture cabin audio. OpenDrive Beacon (the upstream sensor stack) also does not capture cabin audio. **There is no microphone anywhere in the OpenDrive system.** Verbal interventions by the instructor are logged via an on-screen kiosk tap.

---

## Where the human authority lives

- All BTW instruction is delivered by a **WA-licensed instructor in the passenger seat**.
- The instructor is the **sole reviewer and approver** of any post-drive note, plan, or recommendation generated with Clipboard's assistance.
- Every Clipboard output is marked **`DRAFT — INSTRUCTOR REVIEW REQUIRED`** and cannot reach a student or family until the instructor approves it.
- The Devpost demo enforces this with a hard human-review gate: the agent loop **stops** at draft submission and does not advance until the instructor clicks Approve, Edit, Reject, or Regenerate.

---

## Relationship to OpenDrive Beacon

OpenDrive Beacon is the in-vehicle sensor stack: CAN bus, IMU, GPS, forward camera. It records what the vehicle did during a BTW lesson. It is maintained in a private repository and is **not part of the public Clipboard demo**.

For the Devpost submission, Clipboard reads from a **fake / seeded telemetry source** that mimics what real OpenDrive Beacon data looks like. No real Beacon recordings are exposed in this repo. No real driving sessions, no real student PII, no production secrets.

If, in the future, real OpenDrive Beacon recordings flow into Clipboard, they do so only:

1. With the licensed instructor reviewing every draft before delivery, and
2. Within Street Law OpenDrive's regulatory posture (RCW 46.82 + WAC 308-108), and
3. Without ever including cabin audio (because OpenDrive Beacon has no microphone).

---

## Sensor-by-sensor boundary statement (OpenDrive Beacon, for reference)

OpenDrive Beacon is the upstream system. None of these sensors live in this repo, but they are documented here for completeness because Clipboard's drafts are conceptually downstream of them.

| Sensor | What it does | What it does NOT do |
|---|---|---|
| **CAN bus reader (comma.ai Red Panda)** | Read-only logging of brake, throttle, steering, speed, RPM, turn-signal state. | Does not control any vehicle subsystem. Does not write to the bus. |
| **IMU (Phidget MOT0110_0)** | Records accelerometer + gyro for hard-brake / hard-turn timestamps. | Does not influence vehicle motion. Does not produce in-vehicle output. |
| **GPS (USB receiver)** | Records vehicle location, speed, and route for post-drive map review. | Does not share location externally during the drive. Not used for tracking outside the lesson. |
| **Forward camera (OAK-D Lite)** | Records the road scene for post-drive review and offline ML labeling. | Does not warn the driver. Does not display anything to the student. Not a driver-assist system. |
| **Instructor intervention tap** (kiosk on-screen button; future Bluetooth clicker) | Records the timestamp when the licensed instructor taps to flag a verbal intervention for post-drive review. | **Does not capture audio. OpenDrive Beacon never records, transmits, or processes audio of any kind from inside the vehicle.** |

---

## Regulatory posture

- Operates within **RCW 46.82** (Driver training schools and instructors) and **WAC 308-108**.
- Treats AI-assisted note-drafting as the same category as a digital intake form or a speech-to-text transcription tool: **a documentation aid for the licensed professional.**
- We invite WA DOL review of the system at any time.

---

## Companion documents

- `README.md` (repo root) — quick orientation to OpenDrive Clipboard
- `docs/PRODUCT_BRIEF.md` — full product spec
- `docs/ENGINEERING_PLAN.md` — agent architecture
- `docs/SUBMISSION_PLAN.md` — Devpost submission strategy
- Public Beacon boundary statement: `streetlawopendrive.com/docs/beacon-is-and-is-not.md`

---

## Contact

**Mr. Law (Jason Law)** — Founder + Lead Instructor, Street Law OpenDrive / OpenDriveEDU
mrlaw@streetlawopendrive.com
https://streetlawopendrive.com

---

*OpenDrive™, OpenDrive Beacon™, and OpenDrive Clipboard™ are common-law working names of Street Law OpenDrive. All marks are subject to counsel-led trademark clearance review.*
