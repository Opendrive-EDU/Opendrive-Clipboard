const scenarioSelect = document.querySelector('#scenario');
const notesInput = document.querySelector('#notes');
const runButton = document.querySelector('#run-demo');
const traceEl = document.querySelector('#trace');
const draftEl = document.querySelector('#draft');
const reviewStateEl = document.querySelector('#review-state');
const reviewButtons = document.querySelectorAll('[data-decision]');
const audioControlsEl = document.querySelector('#audio-controls');
const listenBtn = document.querySelector('#listen-btn');
const youthModeEl = document.querySelector('#youth-mode');
const debriefAudioEl = document.querySelector('#debrief-audio');
const audioNoteEl = document.querySelector('#audio-note');

let activeDraftId = null;

function b64ToBlob(b64, mime) {
    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i += 1) bytes[i] = bin.charCodeAt(i);
    return new Blob([bytes], { type: mime || 'audio/mpeg' });
}

async function loadScenarios() {
    const response = await fetch('/api/scenarios');
    const payload = await response.json();

    scenarioSelect.innerHTML = payload.scenarios
        .map((scenario) => `<option value="${scenario.id}">${scenario.title}</option>`)
        .join('');
}

async function runDemo() {
    runButton.disabled = true;
    runButton.textContent = 'Running...';

    try {
        const response = await fetch('/api/demo-runs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                scenario_id: scenarioSelect.value,
                instructor_notes: notesInput.value,
            }),
        });
        const run = await response.json();

        activeDraftId = run.draft.id;
        renderTrace(run.trace);
        renderDraft(run.draft);
        audioControlsEl.classList.add('hidden');
        reviewStateEl.textContent = 'Awaiting licensed instructor review.';
    } finally {
        runButton.disabled = false;
        runButton.textContent = 'Run OpenDrive Clipboard Agent';
    }
}

async function recordDecision(decision) {
    if (!activeDraftId) {
        reviewStateEl.textContent = 'Run a scenario before recording a review decision.';
        return;
    }

    const response = await fetch(`/api/drafts/${activeDraftId}/review`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ decision }),
    });
    const draft = await response.json();

    reviewStateEl.textContent = `Preview state: ${draft.review_decision}. No official record was created.`;
    audioControlsEl.classList.toggle('hidden', draft.review_decision !== 'approve');
}

async function speakDraft() {
    listenBtn.disabled = true;
    listenBtn.textContent = 'Synthesizing...';
    try {
        const response = await fetch('/api/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                draft_id: activeDraftId,
                mode: youthModeEl.checked ? 'youth' : 'professional',
            }),
        });
        const payload = await response.json();
        if (!response.ok) {
            audioNoteEl.textContent = payload.error || 'Could not generate audio.';
            return;
        }
        if (!payload.enabled) {
            audioNoteEl.textContent = 'Audio not configured (Speechify TTS is disabled for this demo).';
            return;
        }
        if (debriefAudioEl.dataset.url) URL.revokeObjectURL(debriefAudioEl.dataset.url);
        const url = URL.createObjectURL(b64ToBlob(payload.audio_b64, payload.mime));
        debriefAudioEl.dataset.url = url;
        debriefAudioEl.src = url;
        debriefAudioEl.controls = true;
        debriefAudioEl.hidden = false;
        const voiceMsg = payload.voice_fell_back
            ? `Youth voice unavailable on this plan - used the professional voice (${payload.voice}).`
            : `Voice: ${payload.voice} (${payload.mode}).`;
        try {
            await debriefAudioEl.play();
            audioNoteEl.textContent = `${voiceMsg} Reads back only the instructor-approved draft.`;
        } catch (err) {
            audioNoteEl.textContent = `${voiceMsg} Press the ▶ on the player below to listen.`;
        }
    } finally {
        listenBtn.disabled = false;
        listenBtn.textContent = '▶ Listen to approved draft';
    }
}

function renderTrace(trace) {
    traceEl.classList.remove('empty');
    traceEl.innerHTML = trace
        .map((entry) => `
            <div class="trace-row">
                <strong>${entry.agent} -> ${entry.tool}</strong>
                <span>${entry.action}: ${entry.detail}</span>
            </div>
        `)
        .join('');
}

function renderDraft(draft) {
    draftEl.classList.remove('empty');
    draftEl.innerHTML = [
        ['Status', draft.status_label],
        ['Safety summary', draft.safety_summary],
        ['Observed concern', draft.observed_concern],
        ['Lesson focus', draft.lesson_focus],
        ['Reflection prompt', draft.reflection_prompt],
        ['Practice assignment', draft.practice_assignment],
        ['Family summary', draft.family_summary],
        ['Language-access preview', draft.language_access_preview],
    ]
        .map(([heading, body]) => `
            <section class="draft-section">
                <h3>${heading}</h3>
                <p>${body}</p>
            </section>
        `)
        .join('');
}

runButton.addEventListener('click', runDemo);
reviewButtons.forEach((button) => {
    button.addEventListener('click', () => recordDecision(button.dataset.decision));
});
listenBtn.addEventListener('click', speakDraft);

loadScenarios();
