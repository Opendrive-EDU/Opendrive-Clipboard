# OpenDrive Beacon — Full System Architecture

**For:** Devpost judges, partner driving schools, technical reviewers
**Author:** Mr. Law (Jason Law), licensed WA BTW instructor, Street Law OpenDrive
**Last updated:** 2026-05-14
**Scope:** This document describes the *production* OpenDrive Beacon system at a system-design level. The public `opendrive-clipboard` repo you are reading is the **post-drive review surface** — the deliberately thin, synthetic-data, instructor-in-the-loop slice of a much larger production stack. This document explains what is behind it.

> **Why this document exists.** A reviewer looking only at the public Clipboard demo would reasonably conclude it is "score-lite" — synthetic post-drive grading with a review gate. That is the *public* surface by design (demo-data-only, no student PII, Apache-2.0). The production Beacon stack — in-vehicle edge compute, real CAN-bus telemetry, a deployed ML context model, and a sensor-fusion roadmap — already exists and is bench-verified. It is not published here because it contains hardware bring-up details, ML training assets, and integration secrets that do not belong in a public repo. **A curated, sanitized, judge-invite-only companion repo is available for verification — see "Verification access" at the end.**

---

## One-paragraph summary

OpenDrive Beacon is a passive in-vehicle evidence recorder for behind-the-wheel (BTW) driving lessons. A Jetson edge node reads the vehicle CAN bus (read-only), an IMU, GPS, and a forward camera, runs a small deployed ML model that classifies 30-second windows of driving into context categories, and — for the DOL "practice commentary driving" exercise only — captures student commentary through an opt-in microphone with a hardware kill switch and ephemeral speech-to-text. After the drive, that structured evidence flows to OpenDrive Clipboard (this repo's agent), which drafts an instructor-ready debrief. **A licensed instructor reviews and approves every draft. Nothing reaches a student without that human sign-off.** Beacon never controls the vehicle, never writes to the CAN bus, and never captures audio covertly.

---

## The full stack

```
┌──────────────────────────────────────────────────────────────────────────┐
│  IN-VEHICLE EDGE  (OpenDrive Beacon — private, bench-verified)             │
│                                                                            │
│  Jetson Orin Nano Super (8GB, 67 TOPS INT8, TensorRT + CUDA)              │
│    ├── Red Panda Rev D + Toyota Type A harness                            │
│    │     read-only CAN (SAFETY_SILENT hardware-enforced — never writes)    │
│    ├── Phidget MOT0110_0 IMU      (accel + gyro, hard-event timestamps)    │
│    ├── BU-353N5 USB GPS           (route, speed — local offsets only)      │
│    ├── OAK-D Lite forward camera  (road-scene text labels, no images out)  │
│    ├── Opt-in boundary microphone (Audio-Technica ATR4697-USB)            │
│    │     hardware USB kill switch + UI toggle + ephemeral STT             │
│    │     ONLY for DOL "practice commentary driving" exercise              │
│    └── Instructor "TAG INTERVENTION" kiosk tap (timestamp only, no audio)  │
│                                                                            │
│  ContextScorer v0.1.0  (deployed, TensorRT FP16, ~0.6 ms inference)       │
│    classifies 30-sec CAN/accel/GPS windows → 8 context labels             │
│    + severity adjustment + domain + confidence                            │
│    confidence < 0.7 → rule-based heuristic fallback                       │
└────────────────────────────────┬───────────────────────────────────────────┘
                                  │ store-and-forward (HMAC-signed device auth)
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  CLOUD  (OpenDrive Clipboard — THIS public repo + Cloud Run)              │
│                                                                            │
│  Gemini / ADK-ready agent + MCP-style tools + review-gate UI              │
│  Multi-agent loop: scenario intake → curriculum retrieval →               │
│    draft assembly → REVIEW GATE (hard stop) → demo log                     │
│  Driver Health Panel: Safety · Smoothness · Attention · Control · Eco      │
│  Synthetic-but-format-accurate data mirrors real ContextScorer output      │
└────────────────────────────────┬───────────────────────────────────────────┘
                                  │ DRAFT — instructor reviews + approves
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  LMS  (OpenDrive EDU — private, Laravel/Vue, not part of this submission)  │
│  Instructor approves → student record → parent-facing PDF → audit trail    │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Hardware (production, bench-verified)

| Component | Role | Status |
|---|---|---|
| **Jetson Orin Nano Super** (8 GB, 67 TOPS INT8) | In-vehicle edge compute; runs ContextScorer inference + store-and-forward | Bench-verified; in-car bring-up Phase D1 (RPM ID) verified 2026-04-29 |
| **Red Panda Rev D** (comma.ai) + Toyota Type A harness | Read-only CAN bus reader. **SAFETY_SILENT mode is hardware-enforced** — the device physically cannot write to the bus. panda library pinned. | Bench-verified 2026-04-24; ~50 miles of real bench data logged |
| **Phidget MOT0110_0** | IMU — accelerometer + gyro, used for hard-brake / hard-turn timestamps | Bench-verified |
| **BU-353N5** | USB GPS — route + speed for post-drive map review. Local offsets only; not reverse-geocodable in the demo data. | Bench-verified |
| **OAK-D Lite** | Forward camera — emits **text scene labels only**, never image bytes or URLs out of the vehicle | Bench-verified; v2 vision-fusion architecture is a roadmap target |
| **Audio-Technica ATR4697-USB** + Cable Matters USB 3.0 cable with hardware on/off switch | Opt-in boundary mic for the DOL "practice commentary driving" exercise. Hardware kill switch + UI toggle + always-visible state badge. Ephemeral STT — audio discarded after transcription, transcript-only retention. | Posture defined (see `docs/BOUNDARY.md`); hardware integration in progress |
| **Instructor TAG INTERVENTION tap** (kiosk button) | Timestamp-only marker for instructor verbal interventions. Independent of the mic. Captures no audio. | Working |

---

## ML — ContextScorer v0.1.0 (deployed)

A small (~3.4 M parameter) CNN + Transformer model that classifies 30-second windows of CAN + accelerometer + GPS + event-history into a **context label** that explains *why* a telematics event happened — not just *that* it happened.

**The 8 context labels:**

```
appropriate_response      merge_acceleration       fatigue
tailgating                school_zone_violation    road_condition
distraction               weather_response
```

Each window also gets a **severity adjustment**, a **domain** tag, and a **confidence** score. When confidence < 0.7 the model defers to a deterministic rule-based heuristic — the model never silently guesses on low confidence.

- Deployed on the Jetson as a TensorRT FP16 engine; sub-millisecond inference.
- High held-out accuracy on the synthetic training distribution; real-world labels accumulate through the instructor review loop (this is exactly what the Clipboard review gate produces — instructor-confirmed labels become training data over time).
- A future student-type model (Variational Preference Learning / conditional VAE) is designed but training-gated: it does not deploy until enough instructor-confirmed labels exist. All adaptation runs **post-drive in instructor review tooling, never in the vehicle**.

The public Clipboard demo's synthetic data is shaped to match this exact output format (8 labels + confidence + severity + domain), so a reviewer can see what real ContextScorer output looks like flowing through the agent — without any real telemetry being exposed.

---

## Voice coaching + scene narration (architecture defined, runtime gated)

- **Voice coaching:** clip-based dragon-coaching audio with per-student-type cooldowns (anxious students get less frequent prompts; over-confident get more). Configured, anti-nag cooldown logic defined, runtime disabled by default.
- **Scene narration:** push-to-talk vision-language description of the road scene for post-drive review. Architecture defined (VLM + TTS), not yet bench-verified end-to-end.

Both are post-drive / instructor-tool features. Neither speaks to the student during the drive. Neither is in scope for the Devpost submission; both are documented here for completeness.

---

## What is real today vs roadmap

| Capability | Status |
|---|---|
| Read-only CAN telemetry (Red Panda, SAFETY_SILENT) | ✅ Bench-verified, ~50 mi real data |
| IMU / GPS / forward-camera capture | ✅ Bench-verified |
| ContextScorer v0.1.0 (8-label context model) | ✅ Deployed on Jetson (TensorRT FP16) |
| Jetson edge compute + store-and-forward | ✅ Bench-verified; in-car Phase D1 done |
| HMAC-signed device → LMS ingest | ✅ Working in the LMS |
| Instructor review + approve loop | ✅ Working (this repo's review gate + LMS BeaconReviewer) |
| Opt-in commentary mic + ephemeral STT | 🔭 Posture defined; hardware integration in progress |
| v2 multi-modal vision fusion (~50 M params) | 🔭 Roadmap target |
| VPL student-type model (CVAE) | 🔭 Designed; training-gated |
| In-car full sensor integration (Phase L6–L12) | 🔭 Post-bench, post-Devpost |
| Cabin-facing driver-state monitor (v3) | 🔭 Future; separate from any audio |

---

## Boundary (unchanged — see `docs/BOUNDARY.md`)

- Beacon **never controls the vehicle** and **never writes to the CAN bus** (SAFETY_SILENT is hardware-enforced).
- The licensed instructor is the **sole authority**. Every Clipboard output is `DRAFT — INSTRUCTOR REVIEW REQUIRED`.
- The microphone is **opt-in only**, with a hardware kill switch + UI toggle + always-visible state badge, used **only** for the DOL "practice commentary driving" exercise. Ephemeral STT; transcript-only retention by default. (Full detail in `docs/BOUNDARY.md`.)
- The public repo contains **synthetic demo data only** — no real student PII, no real Beacon recordings, no production secrets, no copy of the Beacon source code.

---

## Verification access

The production hardware bring-up logs, ML architecture write-ups (sanitized of secrets/IPs), bench-verification photos, and a short bench-running video are maintained in a **private companion repository** for reviewers who want to verify the claims in this document.

**To request access:** email `mrlaw@streetlawopendrive.com` with your GitHub username and Devpost-judge identifier. You will be added as a read-only collaborator to the private companion repo for the duration of Devpost judging. Access is revoked after judging closes (2026-06-22).

The public `opendrive-clipboard` agent is fully reviewable as-is — the private companion exists only to substantiate the production-stack claims (hardware, ML) that cannot be open-sourced without exposing secrets or student data.

---

*OpenDrive™, OpenDrive Beacon™, and OpenDrive Clipboard™ are common-law working names of Street Law OpenDrive. All marks are subject to counsel-led trademark clearance review.*