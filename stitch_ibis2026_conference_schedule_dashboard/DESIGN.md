---
name: Induction Academic Precision
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#464555'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#777587'
  outline-variant: '#c7c4d8'
  surface-tint: '#4d44e3'
  primary: '#3525cd'
  on-primary: '#ffffff'
  primary-container: '#4f46e5'
  on-primary-container: '#dad7ff'
  inverse-primary: '#c3c0ff'
  secondary: '#904d00'
  on-secondary: '#ffffff'
  secondary-container: '#fe932c'
  on-secondary-container: '#663500'
  tertiary: '#00524b'
  on-tertiary: '#ffffff'
  tertiary-container: '#006c63'
  on-tertiary-container: '#81eddf'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e2dfff'
  primary-fixed-dim: '#c3c0ff'
  on-primary-fixed: '#0f0069'
  on-primary-fixed-variant: '#3323cc'
  secondary-fixed: '#ffdcc3'
  secondary-fixed-dim: '#ffb77d'
  on-secondary-fixed: '#2f1500'
  on-secondary-fixed-variant: '#6e3900'
  tertiary-fixed: '#89f5e7'
  tertiary-fixed-dim: '#6bd8cb'
  on-tertiary-fixed: '#00201d'
  on-tertiary-fixed-variant: '#005049'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-xl-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-lg:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  headline-md:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 22px
  body-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-lg:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 10px
    fontWeight: '600'
    lineHeight: 12px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-mobile: 0.75rem
  margin: 1.5rem
  margin-mobile: 0.75rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1.25rem
  space-xl: 2rem
---

## Brand & Style

This design system serves academic researchers, theoretical computer scientists, and mathematical statisticians attending the IBIS2026 workshop. The visual tone must project cerebral rigor, absolute clarity, and institutional prestige without slipping into dry bureaucracy.

The interface pairs a high-density, analytical aesthetic with structural precision. Visual cues draw from modern scientific workbenches and editorial conference schedules:
- **Tone:** Authoritative, focused, high-density, analytical.
- **Style Blend:** Minimalist data density layered with crisp micro-borders, deep contrast headers, and functional semantic tagging.
- **Emotion:** Total situational clarity under packed multi-track symposium schedules, eliminating cognitive friction through clear chronological mapping and metadata hierarchies.

## Colors

The palette balances a dense, high-contrast structural shell with vibrant, semantic functional roles:

- **Deep Navy / Slate (`#0F172A`):** Used for top mastheads, dense global navigation bars, high-contrast modal backdrops, and primary terminal typography.
- **Indigo (`#4F46E5`):** The primary interaction anchor for interactive triggers, current navigation highlights, active filters, and interactive paper links.
- **Keynote Amber (`#D97706`):** Dedicated semantic identifier for invited lectures, plenary addresses, and keynote panels.
- **Live Emerald (`#059669`):** Reserved strictly for active sessions, live streams, and verified real-time room occupancy states.
- **Poster Teal (`#0D9488`):** Distinct categorization for interactive poster presentations, lightning talks, and author demo booths.
- **Time Pulse Rose (`#E11D48`):** High-alert accent dedicated to the horizontal timeline schedule scrubber, session overrun indicators, and "Happening Right Now" pulses.
- **Workspace Canvas & Neutral Tiers:** A calibrated off-white/slate scale (`#F8FAFC` base background, `#FFFFFF` card surfaces, `#E2E8F0` structural boundaries, and `#64748B` supporting metadata text).

## Typography

The typography pairs the structural precision of **Inter** for core UI text, paper titles, and abstracts with the monospaced rigor of **JetBrains Mono** for numerical values, timestamps, room allocations, session track codes (e.g., `TRACK-A`, `POSTER-104`), and paper DOIs.

- Headings use tight letter-spacing (`-0.02em`) to maintain editorial density across titles.
- Monospaced labels use explicit letter-spacing (`+0.02em`) and uppercase transformation for badges and timestamps.
- Abstract and metadata body copy prioritizes line-height discipline to ensure legibility during rapid scanning across multi-column agenda layouts.

## Layout & Spacing

This design system uses a 12-column fluid grid within a constrained max-width workspace (`1600px`), optimized for high-density information architecture.

- **Desktop (1024px+):** Fixed deep-navy header with secondary track navigation strip. Left-hand contextual sidebar (280px) for tracks/date selectors, central timeline matrix (8 columns), and an auxiliary collapsable panel (4 columns) for live session notes, speaker bios, and real-time Q&A.
- **Tablet (768px - 1023px):** Collapses auxiliary panels into off-canvas drawers; the main schedule shifts to a 6-column presentation with sticky time axis.
- **Mobile (<768px):** Single-column stacked stream. Timeline tracks turn into swipeable horizontal tabs, and timeline intervals become unified linear cards.
- **Rhythm:** Spacing follows a compact 4px baseline unit. Gaps between concurrent timeline tracks are locked to `space-md`, while intra-card element spacing preserves a high data-per-pixel ratio via `space-xs` and `space-sm`.

## Elevation & Depth

Visual hierarchy relies on crisp borders and tonal layering rather than heavy drop shadows, preserving an analytical, paper-like feel.

- **Tiers of Ground:**
  - `Base Canvas`: `#F8FAFC` provides the foundational workspace.
  - `Surface Tier 1`: `#FFFFFF` for timeline cards, abstract containers, and panels.
  - `Inverse Surface`: `#0F172A` for persistent global navigation, active filters, and deep-context header blocks.
- **Borders & Micro-Dividers:** All cards, panels, and table cells utilize subtle 1px borders in `#E2E8F0`. Hovering an interactive schedule card shifts the border to `#CBD5E1` with an indigo left accent border.
- **Ambient Focus:** Shadow is reserved exclusively for floating interactive overlays (e.g., active timeline tooltips, author popovers, modal dialogues). Shadows are extra-diffused with zero tinting: `box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.08)`.
- **Current Time Marker:** The temporal indicator uses a 2px horizontal rule in Rose (`#E11D48`) featuring an ambient glow effect (`box-shadow: 0 0 8px rgba(225, 29, 72, 0.4)`), anchoring live attention without obscuring text.

## Shapes

The interface embraces a structured, architectural shape profile (Level 1 / Soft).

- **Containers & Panels:** Cards, paper abstracts, dialog boxes, and schedule cells use a concise `0.25rem` (4px) corner radius, reinforcing an organized tabular data grid.
- **Interactive Badges & Status Chips:** Pill-shaped exceptions are rejected in favor of clipped, technical tags (`0.25rem` corners) to reflect algorithmic precision.
- **Input Fields & Action Controls:** Standardized to `0.25rem`, maintaining cohesive visual cadence alongside data cells.

## Components

### Buttons
- **Primary:** Solid `#4F46E5` background, white Inter medium text, subtle inset highlight, crisp 4px corners. Hover: `#4338CA`.
- **Secondary / Technical:** Transparent background, 1px `#E2E8F0` border, `#0F172A` text. Hover: `#F1F5F9`.
- **Keynote / Featured Action:** Solid `#D97706` background with white text, used sparingly for plenary access or live symposium access.

### Badges & Track Chips
- Designed with `JetBrains Mono` at `label-sm` or `label-md`.
- **Keynote Badge:** `#FEF3C7` background, `#B45309` text, `#FDE68A` 1px border.
- **Live Status Badge:** `#ECFDF5` background, `#047857` text, with a pulsating 6px green indicator circle.
- **Poster Badge:** `#F0FDFA` background, `#0F766E` text, `#CCFBF1` 1px border.
- **Track Identification:** Slate tinted tags (`#F1F5F9` background, `#334155` text) indicating room and session numbers.

### Timeline Cards
- **Base Style:** `#FFFFFF` background, 1px `#E2E8F0` border, `space-md` internal padding.
- **Accent Strip:** 3px solid left-border colored conditionally by type (Amber for Keynote, Teal for Poster, Indigo for Regular Paper).
- **Header Row:** Monospaced session start/end times (`label-md`), room badge, and live indicator aligned using flex-space-between.
- **Content Row:** Paper/talk title set in `headline-md`, followed by speaker names, affiliations, and collapsible abstract toggles.

### Inputs & Search
- Low-profile inputs (34px height) with light gray slate borders (`#CBD5E1`), white background, and monospaced placeholder hints (e.g., `filter by author, doi, keyword...`). Focus state features an indigo border (`#4F46E5`) with a 1px matching ring.

### Checkboxes & Segmented Controls
- Segmented multi-track filters use a connected slate container (`#F1F5F9`) with 4px internal radius. Selected tabs transition to pure `#FFFFFF` with an `#CBD5E1` border and dark slate text.
- Checkboxes use square, sharp-cornered boxes with crisp indigo fills on selection.