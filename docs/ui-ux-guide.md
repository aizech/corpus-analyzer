# Corpus Analyzer UI/UX Guide

This document describes the design system and user-interface conventions used in Corpus Analyzer.

## Design System

### Location

- `assets/custom.css` — CSS variables and component styles.
- `ui.py` — Shared Streamlit helpers (`card`, `section_header`, `empty_state`, `role_badge`, `workflow_steps`).

Every page should call `inject_custom_css()` (via `render_page_header`) so the custom styles are loaded.

### Key Components

| Function | Purpose |
|----------|---------|
| `render_page_header(title, subtitle)` | Standard page header with logo, title, and subtitle. |
| `render_sidebar_info()` | Collapsible Safety & Privacy panel in the sidebar. |
| `card(title, content, icon)` | Styled bordered card for distinct content blocks. |
| `section_header(title, subtitle)` | Section title with optional muted subtitle. |
| `empty_state(icon, title, description)` | Centered placeholder when no content is available. |
| `role_badge(role)` | Badge showing the selected Clinician / Patient / Researcher view. |
| `workflow_steps()` | 3-step visual workflow (Upload → Confirm privacy → Get analysis). |

## User Roles

The Analyze page offers three roles that change how results are presented:

- **Clinician** — Shows technical assessment, professional analysis, and clinical interpretation expanded by default.
- **Patient** — Highlights the plain-language patient-education section and key takeaways.
- **Researcher** — Shows all sections plus a raw-response toggle.

The role selector lives in the sidebar and is persisted in `st.session_state.user_role`.

## Privacy and Consent

- A privacy confirmation panel is shown before analysis.
- The **Analyze Image** button is disabled until the checkbox is checked.
- The panel lists exactly what is sent to the AI provider and what is anonymized locally.

## Reports

- Analysis responses are parsed by `analysis_format.parse_analysis_sections()` into labeled sections.
- If parsing fails, the raw response is rendered as a fallback.
- Each role renders the sections in an order appropriate for that audience.
- Reports can be downloaded as Markdown or PDF (if PDF export is enabled).

## Responsive Behavior

- Avoid wide multi-column layouts on narrow screens; use `st.columns` sparingly.
- The custom CSS includes mobile stacking rules under `@media (max-width: 768px)`.
