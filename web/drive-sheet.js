const scenarioSelect = document.querySelector('#scenario');
const runButton = document.querySelector('#run-grader');
const reportEl = document.querySelector('#report');
const reportTitleEl = document.querySelector('#report-title');
const sectionOneEl = document.querySelector('#section-one');
const beaconStripEl = document.querySelector('#beacon-strip');
const driverHealthPanelBody = document.querySelector('#driver-health-panel tbody');
const ecoGaugeEl = document.querySelector('#eco-gauge');
const attitudeBarEl = document.querySelector('#attitude-bar');
const skillGridEl = document.querySelector('#skill-grid');
const strengthsEl = document.querySelector('#strengths');
const gapsEl = document.querySelector('#gaps');
const commentsDraftEl = document.querySelector('#comments-draft');
const reactionInputs = document.querySelectorAll('input[name="reaction"]');
const reviewStateEl = document.querySelector('#review-state');
const reviewButtons = document.querySelectorAll('[data-decision]');

let activeReportId = null;

async function loadScenarios() {
    const response = await fetch('/api/scenarios');
    const payload = await response.json();
    scenarioSelect.innerHTML = payload.scenarios
        .map((s) => `<option value="${s.id}">${s.title}</option>`)
        .join('');
}

async function runGrader() {
    runButton.disabled = true;
    runButton.textContent = 'Running grader...';
    try {
        const response = await fetch('/api/drive-reports', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario_id: scenarioSelect.value }),
        });
        const report = await response.json();
        activeReportId = report.id;
        renderReport(report);
        reviewStateEl.textContent = `Awaiting licensed instructor review. Status: ${report.status_label}`;
    } finally {
        runButton.disabled = false;
        runButton.textContent = 'Run DOL drive-sheet grader';
    }
}

async function recordDecision(decision) {
    if (!activeReportId) {
        reviewStateEl.textContent = 'Run the grader before recording a decision.';
        return;
    }
    const response = await fetch(`/api/drive-reports/${activeReportId}/review`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision }),
    });
    const report = await response.json();
    reviewStateEl.textContent = `Preview state: ${report.review_decision}. ${report.status_label || ''} No DOL record was created.`;
}

function renderReport(report) {
    reportEl.classList.remove('hidden');
    reportTitleEl.textContent = `${report.scenario.title} - ${report.status_label}`;

    sectionOneEl.innerHTML = renderSectionOne(report);
    beaconStripEl.innerHTML = renderBeaconStrip(report.beacon_snapshot);
    renderDriverHealthPanel(report.driver_health_panel);
    ecoGaugeEl.innerHTML = renderEcoGauge(report.eco_score);
    attitudeBarEl.innerHTML = renderAttitudeBar(report.attitude_profile);
    renderSkillGrid(report);
    renderFindings(strengthsEl, report.strengths, 'No 4s drafted - instructor confirms.');
    renderFindings(gapsEl, report.needs_improvement, 'No 1-2s drafted.');
    commentsDraftEl.value = report.section_three_draft.comments_draft;
    const suggested = report.section_three_draft.reaction_to_coaching_suggested;
    reactionInputs.forEach((input) => {
        input.checked = input.value === suggested;
    });
}

function renderSectionOne(report) {
    const log = report.form_reference.section_1_drive_log;
    const rows = [
        ['Form', `${report.form_reference.agency} - ${report.form_reference.form_id} (${report.form_reference.revision})`],
        ['Instructor', log.instructor],
        ['Student', log.student],
        ['Date', log.drive_date],
        ['Start / End', `${log.start_time} - ${log.end_time}`],
        ['Total time (min)', log.total_time_min],
        ['Scenario route', report.scenario.route],
        ['Conditions', report.scenario.conditions],
    ];
    return rows
        .map(([label, value]) => `<div class="meta-row"><strong>${label}</strong><span>${value}</span></div>`)
        .join('');
}

function renderBeaconStrip(snapshot) {
    const taps = snapshot.intervention_taps
        .map((tap) => `<li><strong>${tap.t}s</strong> ${tap.label} <em>(${tap.pattern})</em></li>`)
        .join('');
    const labels = snapshot.forward_camera_labels
        .map((row) => `<li><strong>${row.t}s</strong> ${row.frame_label}</li>`)
        .join('');
    return `
        <div class="strip-row"><strong>CAN samples</strong> ${snapshot.can_sample_count}</div>
        <div class="strip-row"><strong>IMU samples</strong> ${snapshot.imu_sample_count}</div>
        <div class="strip-row"><strong>GPS samples</strong> ${snapshot.gps_sample_count}</div>
        <div class="strip-row"><strong>Audio captured</strong> ${snapshot.meta.has_audio ? 'YES (this should never appear)' : 'NO - by design'}</div>
        <h3 class="strip-subtitle">Intervention taps</h3>
        <ul class="strip-list">${taps || '<li>None</li>'}</ul>
        <h3 class="strip-subtitle">Forward-camera frame labels (text only)</h3>
        <ul class="strip-list">${labels || '<li>None</li>'}</ul>
    `;
}

function renderDriverHealthPanel(rows) {
    driverHealthPanelBody.innerHTML = rows
        .map((row) => `
            <tr class="flag-${row.flag}">
                <td>${row.label || row.metric}</td>
                <td>${row.value} <span class="unit">${row.unit}</span></td>
                <td>${row.ref_range}</td>
                <td><span class="flag-badge flag-${row.flag}">${row.flag}</span></td>
            </tr>
        `)
        .join('');
}

function renderEcoGauge(eco) {
    const value = eco.score;
    const pct = Math.max(0, Math.min(100, value));
    const angle = (pct / 100) * 180 - 90;
    return `
        <svg viewBox="0 0 200 120" class="eco-svg" aria-label="Eco score">
            <path d="M 10 110 A 90 90 0 0 1 190 110" fill="none" style="stroke: var(--border-soft);" stroke-width="14"/>
            <path d="M 10 110 A 90 90 0 0 1 190 110" fill="none" style="stroke: var(--brand-fill);" stroke-width="14"
                  stroke-dasharray="${(pct / 100) * 282.7}, 282.7"/>
            <line x1="100" y1="110" x2="${100 + 70 * Math.cos((angle * Math.PI) / 180)}"
                  y2="${110 + 70 * Math.sin((angle * Math.PI) / 180)}"
                  style="stroke: var(--text);" stroke-width="3"/>
            <circle cx="100" cy="110" r="6" style="fill: var(--text);"/>
        </svg>
        <div class="eco-readout">
            <strong>${value}</strong> / 100 - <em>${eco.band}</em>
        </div>
        <p class="microcopy">${eco.note}</p>
    `;
}

function renderAttitudeBar(profile) {
    const segments = [
        { key: 'calm', label: 'Calm', value: profile.calm_pct, color: '#0891b2' },
        { key: 'tentative', label: 'Tentative', value: profile.tentative_pct, color: '#64748b' },
        { key: 'aggressive', label: 'Aggressive', value: profile.aggressive_pct, color: '#dc2626' },
    ];
    const bar = segments
        .map((s) => `<div class="attitude-segment" style="width:${s.value}%;background:${s.color}" title="${s.label} ${s.value}%"></div>`)
        .join('');
    const legend = segments
        .map((s) => `<li><span class="swatch" style="background:${s.color}"></span>${s.label} <strong>${s.value}%</strong></li>`)
        .join('');
    return `
        <div class="attitude-track">${bar}</div>
        <ul class="attitude-legend">${legend}</ul>
        <p class="microcopy">${profile.note}</p>
    `;
}

function renderSkillGrid(report) {
    const groups = {};
    report.skill_ratings.forEach((row) => {
        groups[row.group] = groups[row.group] || [];
        groups[row.group].push(row);
    });

    skillGridEl.innerHTML = report.skill_groups
        .map((group) => {
            const rows = (groups[group] || [])
                .map((row) => renderSkillRow(row, report.rating_scale))
                .join('');
            return `
                <details class="skill-group" open>
                    <summary>${group}</summary>
                    <div class="skill-rows">${rows}</div>
                </details>
            `;
        })
        .join('');
}

function renderSkillRow(row, scale) {
    const suggested = row.suggested_rating === null
        ? '<span class="rating-pill rating-none">No signal</span>'
        : `<span class="rating-pill rating-${row.suggested_rating}">${row.suggested_rating} - ${row.rating_label}</span>`;
    const options = [1, 2, 3, 4]
        .map((value) => `<option value="${value}"${row.suggested_rating === value ? ' selected' : ''}>${value} - ${scale[value].label}</option>`)
        .join('');
    return `
        <div class="skill-row">
            <div class="skill-label">
                <strong>${row.label}</strong>
                <span class="rationale">${row.rationale}</span>
            </div>
            <div class="skill-rating">
                <div>Suggested: ${suggested}</div>
                <label>Instructor override
                    <select data-skill="${row.id}">
                        <option value="">- keep suggestion -</option>
                        ${options}
                    </select>
                </label>
            </div>
        </div>
    `;
}

function renderFindings(target, items, emptyText) {
    if (!items || items.length === 0) {
        target.innerHTML = `<li class="empty">${emptyText}</li>`;
        return;
    }
    target.innerHTML = items
        .map((item) => {
            const lesson = item.curriculum
                ? ` <em>Lesson: ${item.curriculum.lesson}</em>`
                : '';
            return `<li><strong>${item.skill_label}</strong> - ${item.note}${lesson}</li>`;
        })
        .join('');
}

runButton.addEventListener('click', runGrader);
reviewButtons.forEach((button) => {
    button.addEventListener('click', () => recordDecision(button.dataset.decision));
});

loadScenarios();
