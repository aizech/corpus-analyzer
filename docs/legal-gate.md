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

If any check fails, the gate must be re-evaluated before enabling Phase 2.

---

## 10. Sign-off before enabling Phase 2

| Role | Name | Date | Status |
|---|---|---|---|
| Product Owner | | | |
| Legal / Compliance | | | |
| Data Protection Officer (if applicable) | | | |
| Engineering Lead | | | |

**Do not set `ENABLE_PROGRESS_TRACKING=true` in production until all sign-offs
are complete.**
