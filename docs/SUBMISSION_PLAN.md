# Google for Startups AI Agents Challenge — submission plan

## Context

The user (Mr. Law) is **already registered** for the Google for Startups AI Agents Challenge on Devpost (event #3197). Submissions are due **June 5, 2026 at 5:00 PM PT** — five weeks from today (2026-05-01). Kickoff is May 7 with an Addy Osmani intro session. Total prize pool $90K + Cloud credits + Bay Area VIP tickets + virtual coffee with Addy Osmani.

This challenge is the formal home for the **OpenDrive Clipboard** — the rebrand the user shipped this morning as part of the DOL framing scrub. The brief at `.mdfiles/beacon/OpenDrive_Instructor_Debrief_Assistant_Brief.md` is the product spec; this plan is the **submission strategy and build schedule** that lands it on Devpost.

This file previously held the DOL framing scrub plan. That work is now tracked entirely through `TaskList` (tasks #36–#39) and the shipped working tree; this plan is a fresh, different task and overwrites the previous content per plan-mode rules.

---

## Challenge at a glance

| Field | Value |
|---|---|
| Name | Google for Startups AI Agents Challenge |
| Devpost ID | 3197 |
| Submissions open | Apr 22, 2026 |
| Kickoff (Addy Osmani intro) | May 7, 2026, 9:15 AM PT |
| **Submissions deadline** | **June 5, 2026, 5:00 PM PT** |
| Judging | Jun 11 → Jun 18 |
| Winners announced | Jun 22, 2026 2:00 PM PT |
| Prize pool | $60K cash + $37.5K Cloud credits + VIP tickets |
| Eligibility freebie | $500 Cloud credits to every eligible startup |
| Submission requirements | Hosted URL · Public OSS repo with visible license · ~3-min demo video · Devpost form · 3 registration questions |
| Judging criteria | Tech 30% · Business case 30% · Innovation 20% · Demo 20% |
| Mandatory tech | Gemini API (intelligence) · ADK or supported OSS framework (orchestration) · Cloud Run / GKE (infra) |

---

## Track decision: **Track 1 — Build (Net-New Agents)**

### Rationale

Track 1 fits because it matches reality:

- The **agent layer does not exist yet.** The only "draft post-drive note" code referenced anywhere in the working tree is `ClaudeAnalysisService` — and a grep proves it's mentioned only in `docs/ML-ARCHITECTURE-ROADMAP.md`, never implemented as PHP. Net-new is the truthful framing.
- Track 1 explicitly calls out **MCP** as the way agents "securely connect to external tools, gather context, and execute tasks autonomously." That is a precise fit for what the Clipboard needs to do (pull a demo drive's events, look up curriculum, draft a note, queue for review).
- Track 1 allows ADK **or** supported OSS frameworks (LangChain, CrewAI). Gives implementation flexibility if ADK has rough edges in early May.

### Why not Track 2 (Optimize)

Requires bringing an existing Gemini-on-ADK agent and using Agent Simulation / Observability / Optimizer to harden it. We have no existing Gemini agent. Disqualifying.

### Why not Track 3 (Refactor for Marketplace & Gemini Enterprise)

Mandates: B2B core function + Cloud-Native runtime + Gemini-or-Agent-Platform LLM + **A2A protocol** for cross-agent enterprise interoperability. The Clipboard is sold to small driving schools (SMB, not enterprise). A2A interoperability with "internal HR Agent" / "internal Marketplace agents" is a forced fit and a distraction. Marketplace listing posture is also premature. Defer Track 3 to a future cycle.

### Track 1 hidden upside

Several Track-3-style architectural choices (Cloud Run, Gemini, structured tool surfaces) are **good ideas regardless of track**. We adopt them in Track 1 because they earn points on Tech Implementation (30%), without committing to Track 3's enterprise mandates. If the build accidentally meets Track 3's bar, that is a happy accident, not a goal.

---

## What we're building

The product spec is the existing brief at `.mdfiles/beacon/OpenDrive_Instructor_Debrief_Assistant_Brief.md`. Translation to Track 1 architecture:

- **Gemini-powered ADK agent** (Python) running on **Cloud Run**.
- Multi-step loop: `classify safety concern → pull session events → match curriculum → draft debrief note → queue for instructor review`. Stops at the human-review gate.
- **Three MCP servers** exposing typed tools the agent calls — this is the centerpiece for Track 1 scoring on "MCP to securely connect to external tools."
- **Instructor review-gate dashboard** where the licensed instructor sees the draft, edits, approves or rejects. Demo data only. The current MVP ships as a dependency-free Python web demo; Laravel/React/Inertia is the production dashboard direction after the judgeable prototype is stable.
- **Hard human-review gate**: nothing reaches a "delivered" state without instructor sign-off. This is the regulatory boundary AND the product differentiator AND the demo's emotional beat.

The product story for judges: "AI organizes the moment. The instructor leads the lesson."

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Browser demo dashboard  (Cloud Run target)              │
│  - Scenario Intake                                        │
│  - Debrief Note Review (HUMAN-REVIEW GATE — hard stop)   │
│  - Language Access Preview                                │
│  - Demo Log                                               │
│  - Boundary page (links to BEACON-IS-AND-IS-NOT.md)      │
└──────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│  Gemini ADK Agent  (Python, Cloud Run, Gemini 2.5 Pro)   │
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
              │          │          │
              ▼          ▼          ▼
       Demo Postgres   Curriculum   Laravel
       (Cloud SQL)     JSON / RAG   review-gate API
```

### MCP tool surfaces

| Server | Tools |
|---|---|
| `beacon-telemetry-tools` | `get_demo_drive(scenario_id)`, `get_intervention_events(session_id)`, `get_context_predictions(session_id)`, `get_can_summary(session_id)` |
| `curriculum-tools` | `lookup_lesson(topic)`, `match_dragon_to_pattern(pattern)`, `get_dol_standard(code)`, `get_reflection_template(level)` |
| `instructor-review-tools` | `draft_debrief_note(payload)`, `submit_for_instructor_review(draft_id)`, `record_instructor_decision(draft_id, decision)` |

All three MCP servers ship in the same Cloud Run deployment for the demo. The agent treats them as separate tool namespaces.

### Stack table

| Layer | Choice | Why |
|---|---|---|
| Intelligence | Gemini 2.5 Pro for reasoning · Gemini 2.5 Flash for cheap classification | Mandatory tech; mixing tiers improves Tech score. Verified `gemini-2.5-flash` round-trips in `us-central1` on the project (2026-05-01); the 1.5 generation is retired. |
| Orchestration | Google **ADK** (Python) | Mandatory tech; ADK is the headline framework Google wants showcased |
| Tool layer | Three MCP servers (Python, FastMCP or official Google MCP) | Hits the explicit Track 1 MCP mandate |
| Demo backend | Python standard-library HTTP service for MVP; Laravel later | Keeps the judge demo runnable without dependency installs |
| Demo frontend | Dependency-free browser UI for MVP; React/Inertia later | Keeps the judge demo fast, portable, and public-safe |
| Demo data | Cloud SQL (Postgres) with seeded fake drives | No real PII; satisfies "fake/demo data only" boundary |
| Infra | Cloud Run (agent + MCP-style tools + demo UI) | Mandatory tech; cheap; one-command redeploy |
| RAG (curriculum) | Vertex AI Search OR a simple JSON+embedding fallback | "Strategically employ Grounding" — Key Considerations bullet |

---

## Public repo

Per brief Section 8 — **new public repository, demo data only, no live student PII, no Beacon production secrets, complete OSS license visible.**

- Repo: `Opendrivecore/opendrive-clipboard` (matches Codex's `GOOGLE_CLOUD_AGENT_SETUP_PLAN.md` Section 7 naming so the two docs align)
- License: Apache 2.0 (matches Beacon ML license posture; Devpost requires a "visible license")
- Excludes: real Beacon hardware, real student data, audio/microphone code (**Hard Rule 6** — no mic anywhere ever), Vault secrets, any private OpenDriveEDU integration

The existing `opendriveedu` mono-repo stays private and untouched by this work.

---

## Disk layout — where the work lives locally (Pattern C)

The user asked whether the hackathon should live inside this OpenDriveEDU mono-repo (under a hackathon-named folder) or in a separate sibling project folder, and noted that everything ships to Cloud Run anyway. **Decision: Pattern C — split planning from code.**

| Where | What goes there | Why |
|---|---|---|
| `~/PhpstormProjects/opendriveedu/.mdfiles/hackathon/` (this mono-repo, private) | Planning docs, briefs, the Codex engineering plan, the DOL-framing checklist, scratch notes | Keeps Mr. Law's planning where his other planning already lives; same Claude Code terminal/session reads it; never risks public exposure |
| `~/PhpstormProjects/opendrive-clipboard/` (sibling folder, NEW git repo, public on GitHub) | All shipping code — agent, MCP-style tools, review-gate dashboard, deploy manifests, README, LICENSE, demo data | Devpost requires a public OSS repo; clean filesystem boundary makes "is this safe to publish?" a one-question check |

### Why not the alternatives

- **Subfolder of the mono-repo + `git subtree split`** — works once, but every subsequent push has to be re-split, and a single accidental commit at the wrong path can leak private files (Beacon production code, Vault secrets, real student data). Too easy to lose to muscle memory; the public/private boundary needs to be a filesystem boundary, not a git-history boundary.
- **Everything in the mono-repo, ignore the public-repo requirement** — Devpost rule explicitly requires a public OSS repo with a visible LICENSE. Non-negotiable.
- **Everything in the sibling folder, including planning** — splits Mr. Law's docs across two locations. Planning docs benefit from being in the same place as the rest of his thinking; only the *code* needs the public boundary.

### "But it all ends up on Cloud Run anyway"

True. Cloud Run is the runtime; the GitHub repo is the submission artifact. The local sibling folder is what `gcloud run deploy` reads from and what `git push origin main` syncs to GitHub. Local placement is about repo hygiene, not about the runtime story.

### Phase A file moves (planning side)

Both Codex's setup plan and the existing brief currently live under `.mdfiles/beacon/`. Beacon is the production sensor stack; the hackathon is a demo of a downstream concept. Move them so the workstream split matches the repo split:

| From | To | Notes |
|---|---|---|
| `.mdfiles/beacon/GOOGLE_CLOUD_AGENT_SETUP_PLAN.md` | `.mdfiles/hackathon/GOOGLE_CLOUD_AGENT_SETUP_PLAN.md` | Codex's 1093-line engineering spec; becomes the in-repo build doc |
| `.mdfiles/beacon/OpenDrive_Instructor_Debrief_Assistant_Brief.md` | `.mdfiles/hackathon/OpenDrive_Instructor_Debrief_Assistant_Brief.md` | Product spec (this plan's anchor) |
| `docs/dol-edu/OpenDrive_Instructor_Debrief_Assistant_Brief.md` | (leave) | Public-facing DOL doc; stays where regulators expect it |
| `docs/dol-edu/BEACON-IS-AND-IS-NOT.md` | (leave) | Same — public regulatory boundary statement, path is shipped |
| `public/docs/beacon-is-and-is-not.md` | (leave) | Web-served copy; URL is public; do not move |

Grep verified zero cross-references to either source path anywhere in the working tree, so the two `.mdfiles/beacon/` → `.mdfiles/hackathon/` moves are safe `git mv` operations.

### Reconciliation with Codex's `GOOGLE_CLOUD_AGENT_SETUP_PLAN.md`

That doc is highly compatible with this plan and complements it. Division of labor:

- **This plan (`curried-mixing-orbit.md`)** — submission strategy: track choice, deadlines, build phases, DOL framing constraints, risk table, verification checklist. Lives in `~/.claude/plans/`.
- **Codex's plan (`GOOGLE_CLOUD_AGENT_SETUP_PLAN.md`)** — engineering spec: 7-agent ADK design (Orchestrator + Scenario Intake + Lesson Retrieval + Debrief Draft + Reflection/Family Summary + Language Access + Review Gate), gcloud bootstrap commands, env-var contracts, 17-task work plan. After the move it lives at `.mdfiles/hackathon/GOOGLE_CLOUD_AGENT_SETUP_PLAN.md` and eventually copies into the public repo as `docs/ENGINEERING_PLAN.md`.

Where the two disagree, the Codex doc wins on agent count and tooling specifics; this plan wins on track choice, repo naming, and the DOL framing gate. Both name the same repo (`opendrive-clipboard`) — that locks it.

---

## DOL framing constraints applied to all Devpost surfaces

Every public artifact (devpost project page, demo video voice-over, README, code comments, in-product copy) must comply with Hard Rules 1, 2, 3, 6 from the DOL scrub:

1. The word "coach" is reserved for the human in the passenger seat.
2. Do not use role labels that imply the system teaches, instructs, evaluates readiness, or talks directly to the student.
3. Do not pair live timing language with coaching language.
6. **No microphone in the vehicle, ever.** Beacon never captures cabin audio.

Tagline guidance for the Devpost project page (drafts to choose from):

- *"AI organizes the moment. The instructor leads the lesson."*
- *"Instructor-reviewed debriefs for teachable driving moments."*
- *"A Gemini-powered workflow that turns demo driving scenarios into respectful next steps."*

Banned tagline shapes: anything that says the agent "coaches," "teaches," "advises," "guides," or "assists" the student. The agent assists the **instructor**, never the student.

---

## Submission deliverables

| Asset | Status | Owner |
|---|---|---|
| Hosted demo URL (Cloud Run) | Not started | TBD |
| Public OSS repo with visible LICENSE | Not started | TBD |
| ~3-min demo video | Not started | TBD |
| Devpost project page (description, theme, screenshots, video link) | Not started | Mr. Law |
| **3 registration questions** (already submitted; need re-review) | Submitted; text not visible to me | Mr. Law to paste |

### About the 3 registration questions

The Devpost page the user pasted shows the submission-form structure but **not** the verbatim text of the 3 registration questions ("Registered! Edit answers" — the questions sit behind the Edit link). To draft DOL-framing-safe revisions before kickoff (May 7), the user needs to paste the 3 questions and their current answers in the next turn. The plan reserves Phase A time for this revision pass.

If the user meant the page-level "Additional Questions" header (which on this page only contains the support email `dani@devpost.com` and the help icon CTA), then there are no real prompts to answer there and this section becomes a no-op.

---

## Build phases (May 1 → June 5)

Five weeks. Phases are timeboxed and front-load the highest-uncertainty work (Gemini ADK + MCP wiring) so failure modes surface early.

| Phase | Window | Deliverable |
|---|---|---|
| **A — Setup** | Now → May 7 (kickoff) | `git mv` planning docs into `.mdfiles/hackathon/`, create sibling `~/PhpstormProjects/opendrive-clipboard/`, push empty public repo with LICENSE + README seeded from brief, devpost project page first draft, 3 registration questions revised, Cloud Run + Cloud SQL projects provisioned |
| **B — Agent skeleton** | May 7 → May 14 | Gemini ADK agent that calls **one** MCP server (`beacon-telemetry-tools`) and emits a draft string. Round-trip works locally. |
| **C — Full agent loop** | May 14 → May 21 | All 3 MCP servers up; agent does `classify → retrieve → draft → queue` end-to-end; Laravel review-gate page approves/rejects locally |
| **D — Cloud deploy** | May 21 → May 28 | Cloud Run deploy of agent + MCP + Laravel; Cloud SQL demo log; full instructor approve/edit/reject working on the hosted URL |
| **E — Polish & ship** | May 28 → June 5 | Demo video recorded, README polished, screenshots, devpost form completed, **submitted by June 4 EOD** (24h buffer before the 5pm PT deadline) |

Each phase ends with a self-test: agent loop runs, screenshot captured, commit pushed, README updated.

---

## Files & directories to create (in the new repo)

```
opendrive-debrief-assistant/
├── README.md                      # public framing, how to run, license
├── LICENSE                        # Apache 2.0
├── BOUNDARY.md                    # mirror of BEACON-IS-AND-IS-NOT.md (no microphone, instructor authority)
├── agent/
│   ├── pyproject.toml
│   ├── debrief_agent/
│   │   ├── __init__.py
│   │   ├── main.py                # ADK entry point
│   │   ├── prompts/               # system prompts, classifier prompt, drafter prompt
│   │   └── workflow.py            # plan → tool → reflect loop
│   └── tests/
├── mcp-servers/
│   ├── beacon_telemetry/          # 4 tools listed above
│   ├── curriculum/                # 4 tools listed above
│   └── instructor_review/         # 3 tools listed above
├── dashboard/                     # Laravel 13 + React/Inertia demo app
│   ├── app/Http/Controllers/      # IntakeController, ReviewController, DemoLogController
│   ├── resources/js/Pages/        # Dashboard, NewDemoEvent, DebriefNoteReview, LanguagePreview, DemoLog, Boundary
│   ├── database/seeders/          # FakeDriveScenarioSeeder
│   └── tests/
├── data/
│   └── demo_scenarios.json        # late-brake-near-crosswalk, residential-speed-creep, yellow-light-indecision, ...
└── deploy/
    ├── cloudrun-agent.yaml
    ├── cloudrun-dashboard.yaml
    └── README.md                  # one-command deploy guide
```

---

## How this plan touches the existing OpenDriveEDU mono-repo

**It doesn't, by design.** The mono-repo at `~/PhpstormProjects/opendriveedu/` stays the home for production OpenDriveEDU + private Beacon code. The hackathon repo is a clean slate.

Two soft links back to the mono-repo:

1. The Devpost demo video may include a 5-second cutaway showing the real Beacon kiosk in the Corolla Cross (live sensor strip), credited as "production system that informs this prototype." Optional and only if it doesn't slow the agent story.
2. The Devpost project page may link `streetlawopendrive.com/docs/beacon-is-and-is-not.md` as the regulatory boundary statement.

Neither requires committing code to the mono-repo for this submission.

---

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Mr. Law has parallel commitments (Move 7 doc scrub, Dan DOL meeting prep, Seattle launch, Beacon hardware bring-up) | Phase A is timeboxed to <1 week; Phases B–E are sequential with hard gates so partial completion is still demo-able |
| Google ADK is brand-new — undocumented gotchas likely | Phase B intentionally ships only ONE working tool through the loop; expand only after that round-trip is solid |
| Cloud Run cold starts blow the 3-min demo budget | Pre-warm Cloud Run with a synthetic request 30 s before recording; consider min-instances=1 on the agent service for the recording window only |
| Public repo accidentally leaks DOL-misread phrases | Run the DOL framing grep gate against the new repo before every push |
| The 3 already-submitted registration questions may have committed Mr. Law to a track or framing that conflicts with this plan | Resolve in Phase A: user pastes current Q+A, plan revises to align |
| Microphone reference accidentally re-enters via Gemini-generated copy | Add `cabin\|microphone\|audio capture\|VAD\|lavalier` to the pre-push grep gate |
| Devpost judges expect a flashier "AI does the thing live" demo than our human-in-the-loop story allows | Lean into it as the differentiator, not a limitation: the regulatory necessity IS the innovation. Frame in the demo voice-over. |
| Submission form deadline buffer is too tight | Internal deadline is **June 4 EOD (24-hour buffer)**, not June 5 5pm PT |

---

## Verification (submission-ready checklist)

| Check | Pass criteria |
|---|---|
| DOL framing grep gate | A grep for disallowed role labels, cabin-audio terms, and old product names returns zero hits |
| LICENSE present and visible | `LICENSE` at repo root, mentioned in README first paragraph |
| README explains the human-review gate as a hard requirement | Phrase "DRAFT — INSTRUCTOR REVIEW REQUIRED" appears at least once in README |
| Hosted URL renders without auth | `curl <hosted-url>` returns 200; sample drive scenario loads in <5 s |
| Demo video segment 1:35–2:10 | Voice-over says "the human instructor reviews and approves before anything is saved" verbatim |
| Devpost project form | Theme set to "Build (Net-New Agents)"; tagline matches one of the approved drafts; 3 registration questions reviewed |
| Mandatory tech checklist | Gemini API used (commit-traceable) · ADK or supported OSS framework used · Cloud Run deploy URL active |
| Internal deadline | All assets shipped and devpost form submitted **by June 4 23:59 PT** (24-hour buffer before official deadline) |
| Boundary page reachable | `/boundary` route in the demo links to BOUNDARY.md (mirror of `BEACON-IS-AND-IS-NOT.md`) |

---

## Out of scope (intentionally deferred)

- Live integration with Beacon hardware in the actual vehicle. Demo uses fake/seeded drive data only.
- Real student records or PII. Demo log is fake-data-only.
- Track 3 architectural mandates (A2A protocol, Agent Identity, Marketplace listing). Designed-in where free; not pursued.
- Microphone or audio capture of any kind. **Hard Rule 6.** The instructor "TAG INTERVENTION" tap event is the only verbal-intervention signal in any timeline shown to judges.
- The Move 7 doc scrub for the OpenDriveEDU mono-repo. Tracked separately under TaskList #38 and #39; this plan does not block on it.
- Internal changes to the older OpenDriveEDU mono-repo. Out of scope; new Beacon and Clipboard UI work targets React/Inertia.
- Voice TTS, dragon voice, kiosk in-car AI audio output. Out of scope and disallowed by the project boundary.

---

## Open questions for the user (to confirm before Phase A starts)

1. **Repo name & GitHub org** — locked to `Opendrivecore/opendrive-clipboard` (matches Codex doc). Override only if the user wants a different name.
2. **The 3 already-submitted Devpost registration questions** — paste the verbatim Q+A so this plan can revise them for DOL-framing safety before the May 7 kickoff.
3. **Track confirmation** — Track 1 is the locked recommendation. Override only if Mr. Law explicitly wants Track 3 (which would force A2A + Marketplace + enterprise pivot).
4. **Demo video voice & camera** — Mr. Law on-camera, or screen-only with voice-over? Affects video shoot scheduling in Phase E.
5. **Time budget per week** — order-of-magnitude check: Phases B–D each assume ~10–20 hours/week of focused build time. If real budget is much lower, Phase B & C may need to merge or Track 1 may need to ship with fewer MCP servers (the architecture survives at 1 MCP server, just less impressive on Tech score).

---

## What this plan supersedes

This plan replaces the DOL framing scrub plan that previously occupied this file. That work is preserved as:

- Shipped code in working tree: `opendrive-beacon/python/intervention_detector.py`, `beacon_main.py`, `ws_broadcaster.py`, tests, public docs.
- Active TaskList items: #38 (Move 7 doc scrub remainder, in_progress), #39 (Move 7 kiosk button, pending).
- Reference in `MEMORY.md` and `BEACON-IS-AND-IS-NOT.md` (already shipped).

No information lost; just reorganized so this file can hold the active task.
