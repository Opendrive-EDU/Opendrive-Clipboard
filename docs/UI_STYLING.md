# OpenDrive Clipboard — UI Styling Guide

The Clipboard demo is intentionally dependency-free: no Tailwind, no PostCSS, no build step. All styling lives in a single hand-written `web/styles.css` using CSS custom properties for the palette. Dark and light mode auto-detect via `prefers-color-scheme` — there is **no toggle**.

This guide is the source of truth for the palette, the component patterns, and the constraints. The CSS file is authoritative for the actual values; this doc is authoritative for the *why* behind them.

---

## Palette

Brand colors are stable across both modes. Only neutrals flip. This preserves the product identity (indigo + rubix pink) regardless of the viewer's OS theme.

### Stable across light + dark

| Token | Value | Used for |
|---|---|---|
| `--brand-fill` | `#4f46e5` (indigo-600) | Primary buttons, accent strip on cards, focus rings, trace-row left border, eco-gauge fill, links |
| `--brand-fill-hover` | `#4338ca` (indigo-700) | Hover state for primary button + link |
| `--brand-tint` | `rgb(79 70 229 / 0.08)` light / `rgb(129 140 248 / 0.12)` dark | Hover background on outline buttons, focus ring |
| `--pink` | `#ec4899` (rubix pink) | DRAFT pill fill, Approve button fill |
| `--pink-hover` | `#db2777` (pink-600) | Hover state on Approve |

### Light mode (default)

| Token | Value | Notes |
|---|---|---|
| `--bg` | `#f5f7ff` | Page background — subtly indigo-tinted off-white |
| `--surface` | `#ffffff` | Card bodies (`.hero`, `.panel`) |
| `--surface-soft` | `#f8fafc` | Inner regions (trace rows, draft sections, form inputs) |
| `--surface-sunken` | `#f1f5f9` | Deeper sunken regions (table headers, `.rating-none`) |
| `--surface-tint` | `#eef2ff` | `.review-state`, `.boundary` — informational, indigo-tinted |
| `--text` | `#0f172a` (slate-900) | Body text |
| `--text-strong` | `#334155` | Labels, meta |
| `--text-mid` | `#475569` | Lede, descriptions |
| `--text-mute` | `#64748b` | Microcopy, empty states |
| `--text-faint` | `#94a3b8` | Units, captions |
| `--brand-text` | `#4f46e5` | H1, eyebrow, link color, `.skill-group summary` |

### Dark mode (`prefers-color-scheme: dark`)

| Token | Value | Notes |
|---|---|---|
| `--bg` | `#0b1020` | Deep indigo-slate — not pure black, which reads cheap |
| `--surface` | `#172033` | Cards lift off the background |
| `--surface-soft` | `#1f2b46` | Inner regions |
| `--surface-sunken` | `#0f172a` | Deeper regions |
| `--surface-tint` | `rgb(79 70 229 / 0.15)` | Informational cards |
| `--text` | `#e2e8f0` | Body text |
| `--brand-text` | `#a5b4fc` (indigo-300) | H1 in dark — brighter than `--brand-fill` for AAA contrast against `#172033` |

### Semantic flag colors

Semantic colors stay distinct from the brand colors — flags must read as "ok / watch / concern" not as "brand color."

| Token | Light | Dark |
|---|---|---|
| `--ok-bg` / `--ok-text` | `#ecfeff` / `#155e75` | `rgb(8 145 178 / 0.18)` / `#67e8f9` |
| `--watch-bg` / `--watch-text` | `#fef3c7` / `#854d0e` | `rgb(217 119 6 / 0.22)` / `#fcd34d` |
| `--concern-bg` / `--concern-text` | `#fee2e2` / `#991b1b` | `rgb(220 38 38 / 0.22)` / `#fca5a5` |
| `--good-bg` / `--good-text` | `#dcfce7` / `#166534` | `rgb(22 163 74 / 0.22)` / `#86efac` |
| `--info-bg` / `--info-text` | `#cffafe` / `#155e75` | `rgb(8 145 178 / 0.22)` / `#67e8f9` |

---

## Component patterns

### `.hero` and `.panel` — the card system

Both share: 1 px subtle border, rounded 10 px corners, drop shadow, **and a 4 px solid indigo strip across the top via `box-shadow: inset 0 4px 0 var(--brand-fill)`**. The strip uses `inset` (not `border-top`) so it doesn't shift the layout by 4 px.

`.panel` adds a hover lift: `transform: translateY(-2px)` + indigo-tinted shadow. `.hero` does not lift — it's a header, not interactive.

### `.status-card` — the DRAFT pill

This is the product's load-bearing safety signal: every agent output is `DRAFT - INSTRUCTOR REVIEW REQUIRED` until a licensed instructor approves it. The pill is the visual rendering of that promise, so it must dominate the hero:

- Solid `--pink` fill, white text, subtle pink glow shadow.
- Lives in the hero's right column (grid-template-columns: `1fr minmax(260px, 360px)`).
- Brand color stable across light and dark — identity preservation.
- Targets WCAG AA for bold text. Don't reduce the font weight below 700 here.

### Review-gate button hierarchy

The review gate (Approve / Edit / Reject / Regenerate) is the workflow's load-bearing UI. Visual hierarchy follows the action's stakes:

| Action | Style | Rationale |
|---|---|---|
| **Approve** | Pink fill, white text | The "moment of trust" — the instructor signing off. Should be the most visually prominent. |
| Edit, Reject, Regenerate | Transparent fill, indigo border + text | Secondary actions. Indigo outline anchors them to the brand but keeps them subordinate. |

The default page button (the "Run OpenDrive Clipboard Agent" CTA) is indigo fill. So the hierarchy is: **indigo = action**, **pink = moment of safety approval**.

### `.trace-row` — agent trace entries

3 px indigo left border. This is a visual repetition of the brand color that gives the trace a rhythm and reinforces "this is an agent, not a chatbot."

---

## Type

- System font stack at `:root`: `Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`. No webfont fetch — keeps page load fast and avoids FOUT.
- `h1`: `clamp(34px, 5vw, 56px)`, weight 800, `letter-spacing: -0.02em`, brand color. Confident.
- `h2`: 18 px, weight default, slight negative letter-spacing.
- Eyebrow: 12 px, weight 800, uppercase, brand color, `letter-spacing: 0.02em`.
- Body / lede: 17 px, line-height 1.7.

---

## Accessibility

- WCAG AA (4.5:1) for body text in both modes.
- WCAG AAA where practical for the DRAFT pill (it's the safety claim) — currently AA-bold via `#ec4899` background and `#ffffff` text on the pink fill at weight 800.
- Visible focus states on form inputs and buttons — `box-shadow: 0 0 0 3px var(--brand-tint)` (a soft indigo halo) plus `outline: 3px solid var(--brand-tint); outline-offset: 2px` on `:focus-visible`. Never remove the focus ring.
- `color-scheme: light dark` on `:root` so native form widgets (selects, textareas) also follow the OS theme.

---

## How to extend

### Add a new card type

```css
.my-card {
    border: 1px solid var(--border-strong);
    border-radius: 10px;
    background: var(--surface);
    box-shadow: inset 0 4px 0 var(--brand-fill), var(--shadow-card);
    padding: 22px;
}
```

Reuse `--shadow-card` and the accent strip pattern for consistency. Don't introduce new shadow tokens unless the use case is genuinely different.

### Add a new semantic flag color

1. Add light + dark values to `:root` and the `@media (prefers-color-scheme: dark)` block.
2. Add a `.flag-<name>` rule using `var(--<name>-bg)` and `var(--<name>-text)`.
3. Verify contrast: dark-mode flag chips need at least 4.5:1 between bg and text. Check on the actual `--surface` color, not just on white.

### Change the brand color

Edit `--brand-fill`, `--brand-fill-hover`, and `--brand-text` (light + dark). Keep the relationship: `--brand-text` in dark should be a lighter tint of the brand hue (e.g., `indigo-300` for an indigo-600 brand) so AAA contrast holds against the dark card surface.

---

## What NOT to do

- **Don't add a light/dark toggle.** `prefers-color-scheme` is the modern standard. A toggle adds UI surface area, JS state, and persistence concerns for zero functional gain. Judges expect auto-detect.
- **Don't introduce a third theme** (high-contrast, "pop art," etc.). Two modes that share brand colors is the strongest visual identity.
- **Don't make the DRAFT pill a different color across modes.** Pink stays pink. The pill is the brand's safety promise; it should look identical regardless of OS theme so it's instantly recognizable.
- **Don't add Tailwind, PostCSS, or a build step.** The repo's "dependency-free" pitch is load-bearing for judge testability (Dockerfile is `COPY . /app` + run server; no `npm install`).
- **Don't hardcode hex values in new rules.** Use the custom properties. New hex literals are a smell that you're adding a one-off color instead of extending the palette.
- **Don't remove the inset accent strip on cards.** It's the visual signature that ties the design together. If you don't want it on a specific card, use a different selector — don't override globally.
- **Don't let the H1 default to slate-900.** The brand-color H1 (indigo on light, indigo-300 on dark) is what makes the page read as a deliberately designed AI product instead of a Bootstrap admin theme.

---

## File locations

- Stylesheet: `web/styles.css` (single file, ~14 KB, 542 → ~470 lines)
- Markup: `web/index.html`, `web/drive-sheet.html`
- Inline-SVG colors that need to flip across modes: `web/drive-sheet.js` (eco-gauge — uses `style="stroke: var(--text);"` etc. so it follows the active palette)
- Source brand logos: `docs/opendriveedulogos/` (originals — don't reference directly from the demo; the web-optimized versions in `web/` are what get served)
- Web-optimized assets: `web/favicon.ico`, `web/favicon-32.png`, `web/apple-touch-icon.png`, `web/icon.png`, `web/icon@2x.png`
