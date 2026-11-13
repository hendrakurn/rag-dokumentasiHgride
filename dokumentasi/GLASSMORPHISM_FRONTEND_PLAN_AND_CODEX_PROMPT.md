# Glassmorphism Frontend Implementation Plan and Codex Prompt

## Design Read

Reading this as: redesign of the existing Streamlit RAG assistant for technical users, with a soft glassmorphism AI interface language, leaning toward a frosted command surface inspired by the provided Omago AI reference.

The target is not a new marketing website. The target is the existing web frontend in `app_streamlit.py`.

## Reference Image Interpretation

The reference image shows these useful traits:

- A large rounded application shell with a pale lavender surface.
- A soft radial glow behind the main assistant area.
- A compact top navigation instead of a heavy sidebar-first layout.
- A centered assistant identity moment.
- A wide frosted input composer with thin white borders and subtle inner highlights.
- Small glass chips for modes and quick actions.
- One saturated violet action button, used sparingly.
- Low visual density, large empty space, and soft blur depth.

The implementation should keep these traits, but adapt them to HGrid247 RAG. It must not become a generic chatbot clone.

## Product Goal

Turn the current HGrid247 Streamlit web interface into a polished glassmorphism RAG workbench:

- Users ask HGrid247 documentation questions.
- The app shows model, collection, retrieval status, and source evidence.
- The UI feels light, modern, and tactile.
- Source URLs and chunk preview remain auditable.
- Existing RAG behavior remains unchanged.

## Scope

Primary file:

- `app_streamlit.py`

Supporting files only if needed:

- `dokumentasi/DESIGN.md`
- `dokumentasi/FASE1_WEB.md`
- `dokumentasi/RUNNING.md`

Do not change:

- `core/rag.py`
- `core/config.py`
- `core/prompts.py`
- `ingest.py`
- Qdrant collection behavior
- Gemini or embedding configuration

## Target Visual System

### Aesthetic

Soft glass AI command surface.

Use a pale lavender and off-white canvas, translucent glass panels, violet accent, cool muted text, and subtle cyan or blue secondary signal only for source evidence.

### Palette

Use semantic CSS variables, not scattered hard-coded colors:

- `--canvas`: pale lavender-white, page background.
- `--canvas-deep`: slightly richer lavender for radial depth.
- `--glass`: translucent white surface.
- `--glass-strong`: stronger frosted panel surface.
- `--glass-border`: thin white border.
- `--text-main`: near-black violet-gray.
- `--text-muted`: muted slate-lavender.
- `--accent`: controlled violet for primary action.
- `--accent-strong`: saturated violet for send button and active nav.
- `--source`: blue-cyan for source anchors.
- `--warning`: warm muted amber for warnings only.

Avoid:

- Default purple-to-blue gradient as the main palette.
- Pure white and pure black.
- Neon edge glow everywhere.
- Random floating blobs.

### Typography

Use the existing local font assets if available, but shift the styling from industrial condensed into a softer AI workbench rhythm:

- Display: existing `HGrid Condensed` only for title or brand lockup.
- Body: system UI is acceptable in Streamlit, but keep size, line-height, and weight controlled.
- Labels: small, readable, not overused. Maximum one visual eyebrow in the first viewport.

### Glass Material Recipe

Create reusable CSS classes:

- `.glass-shell`
- `.glass-nav`
- `.glass-panel`
- `.glass-composer`
- `.glass-chip`
- `.glass-action`

Glass panels should use:

- `background: linear-gradient(...), rgba(...)`
- `backdrop-filter: blur(22px) saturate(160%)`
- `-webkit-backdrop-filter`
- `border: 1px solid rgba(255,255,255,0.42)`
- inner highlight via `box-shadow: inset 0 1px 0 rgba(255,255,255,0.55)`
- tinted outer shadow, not black shadow

Add fallback:

```css
@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
  .glass-panel,
  .glass-composer,
  .glass-nav {
    background: rgba(250, 247, 255, 0.96);
  }
}

@media (prefers-reduced-transparency: reduce) {
  .glass-panel,
  .glass-composer,
  .glass-nav {
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
    background: rgba(250, 247, 255, 0.96);
  }
}
```

## Layout Plan

### First Viewport

Use a full-page custom app shell:

1. Outer rounded container with soft border and shadow.
2. Top nav row:
   - HGrid247 AI logo at left.
   - Navigation labels: `Chat`, `Sources`, `Config`, `Run`.
   - Search/status cluster at right.
3. Center assistant moment:
   - Small glass icon mark.
   - `Hi, I'm HGrid247 AI`
   - Short subcopy in Indonesian.
4. Large glass composer:
   - Text area.
   - Attached control chip.
   - Search/deep-research mode chip.
   - Primary send button as violet circular/pill action.
5. Quick prompt chips below composer.
6. Compact status rail beneath or beside composer, not a heavy dashboard strip.

### Chat History

Render conversation below the first viewport with frosted message panels:

- User message: right-aligned or neutral glass bubble.
- Assistant message: larger readable glass panel.
- Sources: visible source strip under assistant answer.
- Chunk preview: still inside expander, but styled to match glass surface.

### Error State

If Qdrant or Gemini is not ready:

- Show a glass warning panel.
- Keep recovery copy specific:
  - Check Qdrant service.
  - Check collection ingest.
  - Check `GOOGLE_API_KEY`.

### Mobile

At widths below `760px`:

- App shell radius becomes smaller.
- Top nav collapses into logo, status, and compact menu text.
- Composer remains full width.
- Quick chips wrap cleanly.
- Status cells become 2-column or single-column.
- No horizontal scroll.
- Hit targets minimum 44px.

## Interaction Plan

Use only CSS and Streamlit-safe behavior:

- Buttons lift by `translateY(-1px)` on hover.
- Active press uses `translateY(1px)` or `scale(0.99)`.
- Focus-visible rings use violet outline with enough contrast.
- No animation on `all`.
- No layout property animation.
- Add reduced-motion fallback:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
  }
}
```

Use subtle background motion only if it does not affect readability.

## Accessibility Requirements

- Keep the real text area label accessible even if visually hidden.
- Use visible focus states for links, buttons, text area, and sidebar controls.
- Source links must be underlined or visibly link-like, not only blue.
- Composer submit button text must not wrap.
- Body contrast target: WCAG AA.
- Do not use color alone for retrieval state. Keep stage text like `matching docs`, `composed`, `source pages`.

## Implementation Steps

1. Read `app_streamlit.py` fully.
2. Identify all CSS variables and UI sections.
3. Preserve Python flow and all function names unless a rename clearly improves local structure.
4. Replace current visual language with glassmorphism tokens and reusable classes.
5. Redesign `render_header()` to match the reference image structure.
6. Update `render_status()`, `resolution_markup()`, `render_sources()`, and composer styling to use glass components.
7. Keep Streamlit sidebar usable, but visually soften it or make it secondary. Do not rely on it as the main visual anchor.
8. Ensure mobile media query covers header, composer, chips, status cells, chat panels, and sources.
9. Run checks:
   - `venv/bin/python -m py_compile app_streamlit.py`
   - `node /home/hendra/.agents/skills/impeccable/scripts/detect.mjs --json app_streamlit.py`
   - `curl -i http://localhost:8501/_stcore/health` if the server is running
   - Playwright screenshots at desktop and mobile if available
10. Update documentation with the new design direction if the implementation changes materially.

## One-Shot Codex Prompt

Copy the prompt below into Codex.

```text
You are working in /home/hendra/projects/solusi247/dokProjekLangchain-1.

Task:
Redesign the existing Streamlit frontend in app_streamlit.py into a polished glassmorphism AI assistant interface inspired by the provided Omago AI screenshot. Keep this as the HGrid247 RAG assistant, not a new product and not a marketing landing page.

Design read:
This is an operating chat surface for technical HGrid247 users. The visual language should be soft glassmorphism: pale lavender canvas, frosted glass panels, subtle radial depth, compact top navigation, large centered assistant moment, wide translucent composer, small glass quick-action chips, and one controlled violet primary action. It should feel like a premium AI workbench, not a generic chatbot template.

Hard constraints:
- Primary target file is app_streamlit.py.
- Do not change core/rag.py, core/config.py, core/prompts.py, ingest.py, Qdrant collection behavior, Gemini config, or embedding config.
- Preserve existing RAG behavior: question input, quick prompts, chat history, source URLs, chunk preview, error handling, and session state.
- Do not introduce new external dependencies.
- Do not use emojis.
- Do not use pure #000 or #fff as major surface colors.
- Do not use generic purple-to-blue AI gradients.
- Do not hide source evidence behind only an expander. Source anchors must remain visible near the answer.
- Do not create a landing page. The first screen must remain a usable chat/workbench interface.

Implementation requirements:
1. Read app_streamlit.py fully before editing.
2. Replace the current industrial "Tensegrity Retrieval Bench" visual style with a glassmorphism system.
3. Keep the Python functions and data flow clear. You may refactor render helpers if it improves readability, but do not change the RAG API contract.
4. Add semantic CSS tokens:
   --canvas, --canvas-deep, --glass, --glass-strong, --glass-border, --text-main, --text-muted, --accent, --accent-strong, --source, --warning, --shadow-soft.
5. Add reusable classes:
   .glass-shell, .glass-nav, .glass-panel, .glass-composer, .glass-chip, .glass-action, .source-glass, .status-glass.
6. Implement the page as a rounded glass app shell:
   - top navigation with HGrid247 AI brand at left
   - nav items: Chat, Sources, Config, Run
   - right status/search cluster
   - centered assistant mark and title: "Hi, I'm HGrid247 AI"
   - Indonesian subcopy under it
   - large frosted composer area
   - quick prompt chips below composer
   - compact status/retrieval rail
7. Style Streamlit chat messages as frosted readable panels.
8. Style source URLs as glass source anchors with clear underline/link affordance.
9. Style resource errors as a glass warning panel with specific recovery copy.
10. Keep all text readable. Body text must meet WCAG AA contrast.
11. Add glass fallback:
   - @supports not backdrop-filter fallback to opaque pale lavender-white
   - @media (prefers-reduced-transparency: reduce) disable blur and use solid surface
12. Add reduced-motion handling. Do not animate layout properties. Do not use transition: all.
13. Mobile:
   - below 760px, the shell becomes compact
   - nav does not wrap awkwardly
   - composer fills width
   - quick chips wrap
   - hit targets are at least 44px
   - no horizontal scroll
14. Use the existing local font files if useful, but avoid making the design feel industrial. Keep the UI soft, airy, and precise.
15. Do not use hand-rolled decorative SVG illustrations. Simple geometric logo marks are acceptable if needed.

Visual details to match from the reference image:
- Pale lavender-white full app background.
- Large rounded app container.
- Soft violet ambient glow behind the assistant title and composer.
- Wide translucent input composer with thin white border and inner highlight.
- Small frosted chips for modes and quick prompts.
- One violet send/action button.
- Lots of quiet negative space.
- Minimal top nav, not a heavy sidebar-first composition.

Validation:
Run these after editing:
- venv/bin/python -m py_compile app_streamlit.py
- node /home/hendra/.agents/skills/impeccable/scripts/detect.mjs --json app_streamlit.py
- If Streamlit is running, curl -i http://localhost:8501/_stcore/health
- If Playwright tools are available, capture desktop 1440x1000 and mobile 390x844 screenshots and inspect for blank areas, overlap, unreadable text, horizontal scroll, and broken composer layout.

Deliver:
- Update app_streamlit.py.
- If the design changed materially, update or create a short documentation note in dokumentasi/ explaining the glassmorphism direction and how to run it.
- Final response must summarize changed files, verification results, and the run command:
  cd /home/hendra/projects/solusi247/dokProjekLangchain-1
  source venv/bin/activate
  streamlit run app_streamlit.py
```

## Image Reference Prompt

Use this only if Codex has access to image generation and needs a visual design reference before coding.

```text
Generate one horizontal 16:9 frontend reference image for a Streamlit RAG assistant interface called HGrid247 AI. The design is soft glassmorphism inspired by a premium AI chat app: pale lavender-white app shell, rounded 28px container, frosted top navigation, centered assistant mark, title "Hi, I'm HGrid247 AI", wide translucent composer, quick prompt chips, violet primary send button, subtle source/status chips, large quiet negative space, soft violet ambient glow, no purple-to-blue gradient, no decorative blobs, no fake dashboard, no landing page hero. The page must look like a usable chat workbench with visible RAG status and source evidence. Make the layout implementation-friendly, with clear spacing, readable text, mobile-implied hit targets, and premium glass material details.
```

## Done Criteria

The implementation is done only when:

- The app still runs from `streamlit run app_streamlit.py`.
- A user can ask a question and see an answer.
- Source URLs remain visible.
- The UI visibly matches the glassmorphism reference direction.
- Mobile and desktop do not overlap or horizontally scroll.
- Detector returns no mechanical slop findings, or findings are explicitly fixed.
- Python compile passes.

