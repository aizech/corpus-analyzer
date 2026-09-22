# Body Map Integration Design

This document describes how a body-map feature can be integrated into Corpus
Analyzer so users can mark where a photo or finding is located. The feature is
**planned for Phase 2** and is intentionally not implemented in the current
release.

## Goal

Allow users to mark the location of a skin, nail, wound, or other finding so that
later comparisons (Phase 2 progress tracking) can compare the same body site over
time.

## Data Model

The storage layer already includes a `body_site` field on `PhotoSnapshot`.
`body_site` should be a structured string or enum such as:

- `front:shoulder:right`
- `back:lower_back:center`
- `leg:thigh:left`
- `arm:forearm:right`
- `nail:finger:index:left`

A hierarchical format keeps filtering and grouping simple.

## UI Options

### Option A: Babylon.js 3D model (PainTracker reuse)

Reuse the 3D body model from the existing PainTracker WordPress plugin.

**Pros**
- Consistent with existing Corpus Analytica ecosystem.
- Visually impressive and precise.
- Users can rotate and zoom.

**Cons**
- Heavier frontend dependency.
- Embedding a Babylon.js scene inside Streamlit requires `components.html` or an
  iframe and careful state sync.
- Overkill for simple location tagging.

**Recommended for:** Phase 3/4, when the product moves beyond simple marking and
wants a premium 3D experience.

### Option B: Simplified 2D silhouette with hotspots

Provide front/back SVG silhouettes with clickable regions. Store the clicked
region as the `body_site` value.

**Pros**
- Lightweight and fast.
- Easy to embed as SVG/Canvas inside Streamlit.
- Good enough for skin-spot and wound location tracking.

**Cons**
- Less precise than a 3D model for complex anatomy.
- Users need to pick from predefined regions.

**Recommended for:** Phase 2, because it satisfies the immediate need for
progress tracking without adding heavy dependencies.

## Proposed Phase 2 Implementation

1. Add a `body_site` selector to the Analyze page when progress tracking is
   enabled (`ENABLE_PROGRESS_TRACKING=true`).
2. Provide a default 2D SVG body map with front/back views.
3. Store the selected `body_site` with each snapshot via the storage interface.
4. When listing snapshots, group by `body_site` so users can see the history of a
   specific spot.

## Open Questions

- Should the body map support custom user-defined sites (e.g., "birthmark on
  left shoulder")?
- Should the map support zoom/pan for large areas like the back?
- How should we handle sensitive body regions in the UI?
