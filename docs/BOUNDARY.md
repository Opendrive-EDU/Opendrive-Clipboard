# OpenDrive Clipboard — What It Is and What It Is Not

**For:** Devpost judges, partner driving schools, families, public reviewers, WA DOL
**Author:** Mr. Law (Jason Law), licensed WA BTW instructor, Street Law OpenDrive
**Last updated:** 2026-05-14

> **Update note (2026-05-14):** A prior version of this document committed to "no microphone anywhere in OpenDrive." That commitment is rescinded. The WA DOL DTS-661-047 form has **"Practice commentary driving"** as one of the 50 scored skills, and scoring that skill requires capturing the student's spoken commentary. The replacement posture is: **opt-in microphone, hardware kill switch (physical USB on/off cable), UI toggle, ephemeral speech-to-text, transcript-only retention by default.** The hardware kill switch is load-bearing — student or instructor can physically cut mic power without touching software. This is a stronger trust posture than the prior blanket ban, not a weaker one. Details below.

This document is the regulatory boundary statement for **OpenDrive Clipboard** (the Devpost AI Agents Challenge submission product) and its relationship to **OpenDrive Beacon** (the in-vehicle sensor stack maintained in the private OpenDriveEDU mono-repo). It mirrors the public-facing `BEACON-IS-AND-IS-NOT.md` shipped at `streetlawopendrive.com/docs/beacon-is-and-is-not.md`.

> For the full production system design (Jetson edge stack, ContextScorer ML model, sensor-fusion roadmap) and how judges can request verification access to a sanitized private companion repo, see [`docs/FULL_BEACON_ARCHITECTURE.md`](FULL_BEACON_ARCHITECTURE.md). This BOUNDARY statement governs the public Clipboard demo specifically; FULL_BEACON_ARCHITECTURE.md describes the broader Beacon system that sits behind it.

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
- **Not a covert microphone.** OpenDrive Beacon includes a **single opt-in boundary microphone** (Audio-Technica ATR4697-USB) used ONLY for capturing student commentary during the WA DOL "practice commentary driving" exercise. Three controls govern it:
  1. **Hardware kill switch** on the USB cable (Cable Matters 5 Gbps USB 3.0 with physical on/off toggle). Student or instructor can physically cut power. When off, the mic cannot capture anything, period.
  2. **UI toggle** in the demo and in the instructor dashboard. Software-layer on/off in addition to the hardware switch.
  3. **Mic state badge always visible** to the student. Four states: `HARD_OFF` (hardware cut), `MUTED` (hardware on, UI off), `ACTIVE` (capturing), `UNKNOWN` (pre-poll).

  Default audio mode is `stt_ephemeral_only` — audio is captured, speech-to-text runs, audio is discarded immediately. Only the transcript text is retained. Retaining raw audio requires explicit consent with a reason code and an audit-log entry. The default is never `raw_audio_retained`.

  Verbal **instructor interventions** are logged via an on-screen kiosk tap event (unchanged from the prior design) — that's distinct from commentary-driving mic capture.

---

## Where the human authority lives

- All BTW instruction is delivered by a **WA-licensed instructor in the passenger seat**.
- The instructor is the **sole reviewer and approver** of any post-drive note, plan, or recommendation generated with Clipboard's assistance.
- Every Clipboard output is marked **`DRAFT — INSTRUCTOR REVIEW REQUIRED`** and cannot reach a student or family until the instructor approves it.
- The Devpost demo enforces this with a hard human-review gate: the agent loop **stops** at draft submission and does not advance until the instructor clicks Approve, Edit, Reject, or Regenerate.

### Read-aloud (Speechify TTS) posture

- Text-to-speech is an **optional accessibility add-on**, OFF by default (`SPEECHIFY_ENABLE_TTS`). The public demo ships with zero secrets and no audio.
- Audio can only ever read back text the licensed instructor has **already approved** — the `/api/tts` endpoint pulls the comment from the stored, approved artifact, never from the client. There is no path to voice an unreviewed draft.
- The judge-facing default is a **professional voice**. "Youth Mode" (an energetic / celebrity voice such as Snoop Dogg) is opt-in, instructor-gated, and intended only for the learner's own approved copy — never the judge demo default.
- A celebrity voice is used **only** if it is licensed for redistribution on the configured Speechify plan; any voice/SDK/network error automatically falls back to the professional voice and is flagged. Speechify never authors or alters a debrief — it only reads approved text.

---

## Relationship to OpenDrive Beacon

OpenDrive Beacon is the in-vehicle sensor stack: CAN bus, IMU, GPS, forward camera. It records what the vehicle did during a BTW lesson. It is maintained in a private repository and is **not part of the public Clipboard demo**.

For the Devpost submission, Clipboard reads from a **fake / seeded telemetry source** that mimics what real OpenDrive Beacon data looks like. No real Beacon recordings are exposed in this repo. No real driving sessions, no real student PII, no production secrets.

If, in the future, real OpenDrive Beacon recordings flow into Clipboard, they do so only:

1. With the licensed instructor reviewing every draft before delivery, and
2. Within Street Law OpenDrive's regulatory posture (RCW 46.82 + WAC 308-108), and
3. With cabin audio captured ONLY when the hardware kill switch is on AND the UI toggle is enabled AND the session is mid commentary-driving exercise. Audio is processed ephemerally — STT runs, audio is discarded, transcript-only retained.

---

## Sensor-by-sensor boundary statement (OpenDrive Beacon, for reference)

OpenDrive Beacon is the upstream system. None of these sensors live in this repo, but they are documented here for completeness because Clipboard's drafts are conceptually downstream of them.

| Sensor | What it does | What it does NOT do |
|---|---|---|
| **CAN bus reader (comma.ai Red Panda)** | Read-only logging of brake, throttle, steering, speed, RPM, turn-signal state. | Does not control any vehicle subsystem. Does not write to the bus. |
| **IMU (Phidget MOT0110_0)** | Records accelerometer + gyro for hard-brake / hard-turn timestamps. | Does not influence vehicle motion. Does not produce in-vehicle output. |
| **GPS (USB receiver)** | Records vehicle location, speed, and route for post-drive map review. | Does not share location externally during the drive. Not used for tracking outside the lesson. |
| **Forward camera (OAK-D Lite)** | Records the road scene for post-drive review and offline ML labeling. | Does not warn the driver. Does not display anything to the student. Not a driver-assist system. |
| **Instructor intervention tap** (kiosk on-screen button; future Bluetooth clicker) | Records the timestamp when the licensed instructor taps to flag a verbal intervention for post-drive review. | Does not itself capture audio. The intervention tap and the boundary mic are independent — tapping always works regardless of mic state. |
| **Boundary mic** (Audio-Technica ATR4697-USB, omnidirectional condenser, USB) | Captures cabin audio ONLY when (a) the hardware USB kill switch is on AND (b) the UI toggle is enabled AND (c) the session is mid commentary-driving exercise. STT runs ephemerally; raw audio discarded immediately. Transcript-only retained. Used for DOL "practice commentary driving" skill scoring. | Does not capture covertly. Mic state badge always visible to the student. Default mode is `stt_ephemeral_only` — `raw_audio_retained` mode requires explicit consent log entry with reason code. |

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
