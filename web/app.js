const scenarioSelect = document.querySelector('#scenario');
const notesInput = document.querySelector('#notes');
const runButton = document.querySelector('#run-demo');
const traceEl = document.querySelector('#trace');
const draftEl = document.querySelector('#draft');
const reviewStateEl = document.querySelector('#review-state');
const reviewButtons = document.querySelectorAll('[data-decision]');

let activeDraftId = null;

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

loadScenarios();
