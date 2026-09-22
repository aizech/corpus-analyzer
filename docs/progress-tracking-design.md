# Progress Tracking Design

This document describes the planned progress-tracking feature for Corpus
Analyzer. The feature is **deactivated in the current release**
(`ENABLE_PROGRESS_TRACKING=false`) and requires legal and privacy review before
it can be enabled.

## Goal

Allow users to photograph the same skin spot, nail, wound, or other finding over
time and compare changes between visits. Provide a conservative reminder to
re-photograph when appropriate.

## Legal Gate

Progress tracking stores health-related images, which are special-category data
under **DSGVO Art. 9**. Before enabling this feature:

1. The product's **Zweckbestimmung** must be finalized in writing.
2. It must be determined whether the feature (especially with any triage or
   urgency language) classifies Corpus Analyzer as a **Medizinprodukt** under
   the EU MDR.
3. The **EU AI Act** classification must be clarified.
4. A clear **legal basis** (explicit consent) and processor agreements (AVV)
   with any AI provider must be in place.
5. Encryption, retention, and deletion policies must be documented.

Until this gate is cleared, `ENABLE_PROGRESS_TRACKING` must remain `false` and
no production storage backend should be wired.

## Data Model

Use the `PhotoSnapshot` model from `storage/models.py`:

- `user_id`: opaque identifier
- `created_at`: UTC timestamp
- `image_hash`: SHA-256 hash of the image (deduplication, integrity)
- `image_path`: path or reference to the encrypted stored image
- `body_site`: location from body map
- `anamnesis`: free-text notes from the user
- `analysis_summary`: short AI-generated summary (optional)
- `tags`: e.g., `SnapshotTag.SKIN`, `SnapshotTag.NAIL`

## Comparison: ABCDE Criteria for Skin Lesions

For skin spot comparisons, the agent can be asked to comment on the ABCDE
criteria:

- **A**symmetry: Is the spot symmetrical or not?
- **B**order: Are the edges smooth, irregular, or blurred?
- **C**olor: Has the color changed? Multiple colors?
- **D**iameter: Approximate size (requires scale in photo).
- **E**volution: What has changed since the previous photo?

The comparison output should be educational and must not diagnose melanoma or
any other condition.

## Reminder Logic

When a skin or nail snapshot is saved, offer an optional reminder:

> "Would you like a reminder to take a new photo in 4 weeks?"

Implementation options:

- Local browser notification via PWA/service worker (privacy-friendly, no
  server-side scheduling).
- Email reminder (requires email collection and consent; more complex).

Recommended: PWA/local notification for privacy reasons.

## User Flow

1. User uploads/captures a skin or nail photo.
2. Optionally marks the body site.
3. System asks whether to save the snapshot for progress tracking (opt-in).
4. If yes, the snapshot is encrypted and stored.
5. Later, the user can return to the same body site, take a new photo, and
   request a comparison.
6. The agent outputs an educational comparison using ABCDE-style observations.
7. The system reminds the user to see a doctor if any concerning change is
   reported or if the user is worried.

## Storage Backends to Evaluate

| Backend | Pros | Cons |
|---|---|---|
| Encrypted SQLite on server | Simple, self-hosted | Data stays on server; portability |
| BYOK S3-compatible bucket | User controls data | Complex setup |
| Browser localStorage/IndexedDB | User owns data; no server storage | Limited space, per-device |
| Supabase with row-level security | Managed, auth, easy sharing | Third-party dependency |

Decision deferred until the legal gate is cleared.

## UI/UX Notes

- Progress tracking must be **strictly opt-in**.
- Make deletion easy and obvious.
- Show clear "no medical diagnosis" disclaimers on comparison views.
- Avoid green/orange/red "traffic light" labels that could be interpreted as
  medical triage.
