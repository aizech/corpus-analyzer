# Legal & Privacy Gate for Phase 2

> **Disclaimer:** This document is an internal engineering checklist and risk
> map. It is **not legal advice**. Before enabling persistent health-data storage,
> progress tracking, or any feature that could be interpreted as medical
> decision-support, Corpus Analytica should obtain a written legal opinion from
> qualified regulatory counsel.

## Purpose of this gate

Phase 2 of Corpus Analyzer introduces features that touch **special-category
health data** and may change the regulatory classification of the product:

- Persistent storage of photographed body findings (progress tracking).
- Comparison of images over time (longitudinal analysis).
- Doctor-handover exports and second-opinion referrals.

These features must not be enabled in production until the items below are
documented, reviewed, and signed off.

---

## 1. Zweckbestimmung / Intended Purpose

Final wording to be used in all user-facing and regulatory materials:

> Corpus Analyzer is an educational and orientation tool. It helps users
> understand what their medical images, smartphone health photos, and
> photographed health documents show. It does **not** diagnose, triage, or
> recommend treatment. All output should be reviewed by a qualified healthcare
> professional.

### Open questions

- [ ] Is the wording approved by legal/compliance?
- [ ] Is it reflected consistently in README, PRD, About, Security, and in-app
      disclaimers?

---

## 2. MDR / Medical Device Regulation (EU)

### Risk to clarify

If progress tracking or longitudinal comparison is marketed in a way that suggests
melanoma screening, early detection, or treatment decisions, Corpus Analyzer could
be classified as a **medical device** under EU MDR.

### Checklist

- [ ] Legal opinion obtained on whether Phase 2 features trigger MDR.
- [ ] If MDR applies: determine class (I, IIa, IIb, III) and required conformity
      route.
- [ ] If MDR does **not** apply: document why and ensure marketing language
      does not imply medical purpose.
- [ ] Review all user-facing copy for phrases like "screening", "early
      detection", "monitoring", "track your cancer risk", etc. Remove or
      rephrase.

### Engineering guardrails

- No traffic-light / red-yellow-green classification.
- No urgency labels such as "urgent", "soon", "within 24 hours".
- Neutral language only: "consider seeing a doctor if you are unsure".

---

## 3. EU AI Act

### Risk to clarify

AI systems used for health purposes can be classified as **high-risk** under the
EU AI Act.

### Checklist

- [ ] Determine AI Act risk class for the planned feature set.
- [ ] If high-risk: plan conformity assessment, risk management system,
      logging, human oversight, and transparency obligations.
- [ ] Document which AI provider is used (OpenAI API) and under what terms.

---

## 4. GDPR / DSGVO Art. 9 — Special-category health data

Health photos and progress snapshots are **special-category personal data**
under GDPR Art. 9.

### Legal basis

The appropriate basis is **explicit consent** (Art. 9(2)(a)).

### Checklist

- [ ] Consent flow is separate from the analysis consent.
- [ ] Consent is granular: users can agree to analysis **without** agreeing to
      progress tracking.
- [ ] Consent is recorded (timestamp, version, scope).
- [ ] Users can withdraw consent and delete stored snapshots easily.

### Engineering guardrails

- `ENABLE_PROGRESS_TRACKING` defaults to `false`.
- Storage is encrypted at rest.
- No health data is sent to OpenAI for progress-tracking metadata unless the
  user explicitly starts a new analysis.

---

## 5. Processor agreement (AVV) with AI provider

### Open questions

- [ ] Does OpenAI's API terms and EU data processing addendum cover the
      planned use case?
- [ ] Are images sent to OpenAI for analysis retained? For how long? Where?
- [ ] Is model-training opt-out configured correctly?

Current understanding (must be verified against current OpenAI policy):

- OpenAI API inputs/outputs are not used to train models by default.
- Data may be retained for up to 30 days for abuse/safety monitoring.
- Verify at https://platform.openai.com/docs/guides/your-data.

---

## 6. Data retention and deletion

### Policy to define

- How long are snapshots stored?
- Who can delete them?
- What happens when a user deletes their account (if accounts exist)?

### Engineering guardrails

- Each snapshot has a unique id and a deletion API.
- UI offers "delete all my snapshots".
- Encryption key management documented separately.

---

## 7. Cross-border data transfers

### Open questions

- [ ] Which OpenAI region / endpoint is used?
- [ ] If data leaves the EEA, is an adequate transfer mechanism in place
      (e.g., EU-approved standard contractual clauses)?

---

## 8. Security measures

### Checklist

- [ ] Storage encryption at rest.
- [ ] Transport encryption (HTTPS) for the web app.
- [ ] Access controls if multi-user support is added.
- [ ] Logging limited to non-sensitive metadata; no raw health images in logs.

---

## 9. Code-level verification

Engineering should run the automated compliance check before each release:

```bash
python scripts/legal_compliance_check.py
```

This script verifies that:

1. `ENABLE_PROGRESS_TRACKING` defaults to `false`.
2. The progress-tracking consent is separate from the analysis consent.
3. No traffic-light/triage language appears in skills or user-facing text.
4. No definitive diagnosis or treatment claims appear in skill instructions.
5. Encrypted storage requires an encryption key.
6. No raw health images are written to logs.
7. All environment variables used in `config.py` are documented in `.env.example`.
8. No obvious hardcoded secrets exist in project Python files.
9. No `print` statements are used in `views/` (which could leak data to stdout).
10. Progress-tracking UI elements are gated by `ENABLE_PROGRESS_TRACKING`.
11. The analysis prompt instructs the model to include a medical disclaimer.
12. Every health-analysis skill has a safety-rules section.

Status: implemented and passing. Run it as part of CI before enabling
`ENABLE_PROGRESS_TRACKING` in production.

If any check fails, the gate must be re-evaluated before enabling Phase 2.

---

## 10. Organizational measures

Beyond code checks, the following organizational measures should be in place
before Phase 2 is enabled:

### 10.1 Legal review workflow

- **Trigger:** Any PR that changes progress tracking, storage, consent, skill
  instructions, or user-facing medical claims must be reviewed by
  legal/compliance before merge.
- **Artifacts:** Legal review comments are stored in the PR; a final sign-off
  is recorded in this document (Section 11).
- **Fallback:** If no legal counsel is available, the PR must not enable
  `ENABLE_PROGRESS_TRACKING` by default and must keep all new features behind
  the flag.

### 10.2 Data Protection Impact Assessment (DPIA)

- [ ] Document the data flows for health photos, snapshots, and AI provider
      submissions.
- [ ] Identify risks to data subjects and mitigations (encryption, opt-in,
      deletion, minimization).
- [ ] Record the legal basis for each processing activity.
- [ ] If required by local law, submit the DPIA to the supervisory authority.

### 10.3 AI provider governance

- [ ] Keep a copy of the current OpenAI API Terms of Use and Data Processing
      Addendum.
- [ ] Review them quarterly or after any service-change notification.
- [ ] Document the selected model provider and region in the deployment
      runbook.
- [ ] Maintain an opt-out / no-train confirmation log if available from the
      provider.

### 10.4 Incident response

- [ ] Define what constitutes a privacy/security incident for health data.
- [ ] Document who must be notified (DPO, legal, affected users, supervisory
      authority) and within what timeframe.
- [ ] Prepare a containment playbook: disable progress tracking, rotate
      encryption keys, preserve evidence.

### 10.5 User-facing transparency

- [ ] Privacy policy is updated to cover Phase 2 features.
- [ ] Terms of use clearly state that Corpus Analyzer is not a diagnostic or
      triage service.
- [ ] Consent records can be exported or deleted on request.
- [ ] A simple "delete all my snapshots" flow is available and tested.

### 10.6 Training and awareness

- [ ] Anyone with merge rights to `main` has read this gate document.
- [ ] Marketing/copy review includes a check against triage and diagnosis
      claims.
- [ ] Customer support knows how to handle requests for data deletion and
      consent withdrawal.

### 10.7 Release checklist

Before each release that touches health-data features:

1. Run `python scripts/legal_compliance_check.py`.
2. Run the full test suite: `pytest tests/`.
3. Review all new or changed skill instructions for diagnosis/triage language.
4. Verify the default `.env.example` values keep progress tracking disabled.
5. Confirm sign-off table is up to date (Section 11).

---

## 11. Sign-off before enabling Phase 2

| Role | Name | Date | Status |
|---|---|---|---|
| Product Owner | | | |
| Legal / Compliance | | | |
| Data Protection Officer (if applicable) | | | |
| Engineering Lead | | | |

**Do not set `ENABLE_PROGRESS_TRACKING=true` in production until all sign-offs
are complete.**
