# Peer Review — Private Draft

**Module:** AI and Healthcare (EEEM069)
**Group 4 — "Health is Wealth"**
**Reviewer:** Fiyin Akano

> **This is a private working draft to help you complete the official peer-review form when it opens. Adapt the wording to match the form's prompts (some forms ask for a numeric score; some ask for a free-text justification; some ask for both). Do not submit this file as-is.**

---

## Scoring framework

I'm using a 1–10 scale, where:

- **10:** Exceptional contribution — drove a major component end-to-end, raised quality for everyone.
- **7–9:** Solid contribution — delivered an assigned component well and engaged with the team.
- **4–6:** Partial contribution — was present in meetings but produced limited deliverable output.
- **1–3:** Minimal or absent contribution — attendance only, no substantive deliverable.

Adjust to whatever scale your form uses (e.g. 1–5, percentage, A–E).

---

## Reviews

### Akeeb Lawel — score: **9 / 10**

**What he did.** Owned the data audit end-to-end. Produced a fully reproducible audit notebook (`notebooks/01_data_audit/ELSA_Audit_Notebook.ipynb`) covering all nine ELSA core waves, quantified CES-D quality (93–97% completeness across waves), participant overlap (>90% W6→W7→W8), and feature drift (13,920 unique variables, only 2,656 common to all waves). Built the curated 30-feature modelling list (`modelling_features_final_curated.csv`) by funneling 12,539 raw candidates through a transparent rule-based pipeline (admin removal → high-missingness filter → theory-led domain restriction → concept-prefix collapse). Registered for UK Data Service access on behalf of the team. Authored CONTEXT.md.

**Why this score.** Akeeb's audit is the empirical foundation everything else stands on. Without his wave-selection rationale, the modelling work would have been unjustified. Reliable, on-time, and the audit findings held up under cross-checking when we re-validated CES-D ourselves.

---

### Zannat Chowdhury Sagar — score: **9 / 10**

**What he did.** Built the preprocessing/feature-comparison baseline notebook (`notebooks/03_preprocessing/03_preprocessing_modelling.ipynb`) which validated the CES-D scoring fix and established the single-wave performance baseline. Designed and built the enhanced longitudinal pipeline (`notebooks/05_modelling/depression_pipeline_enhanced.ipynb`) and the final run-once submission notebook (`submission/ELSA_Depression_Prediction.ipynb`). His enhancements include adding XGBoost and LightGBM, hyperparameter tuning via RandomizedSearchCV across all three prediction arms, the six-configuration feature registry, the two-act SHAP narrative, calibration analysis with isotonic regression, the domain ablation, and the ensemble model. Authored the `submission/README.md`. Met with Fiyin on 16 April for a sub-team sync to align the final submission notebook structure.

**Why this score.** Zannat took the working pipeline and turned it into a publication-quality experimental sweep. The two-act SHAP narrative and the calibration analysis are particularly strong contributions that materially improve the scientific story.

---

### Fiyin Akano (myself) — score: **9 / 10**

**What I did.** Built the original W6+W7 longitudinal modelling pipeline (`notebooks/05_modelling/depression_prediction_pipeline.ipynb`) end-to-end: data loading, preprocessing, feature engineering, training, evaluation, interpretation. Identified and corrected the CES-D scoring artefact (raw 0–3 scale producing 74% prevalence; switched to IFS-validated `cesd_sc` for the correct ~19% prevalence). Designed the leakage sensitivity analysis that became the central scientific finding (AUC 0.85 → 0.77 without CES-D). Produced the SHAP interpretability layer. Generated the 11 presentation-ready figures. Led the PR review cycle through 11 rounds of GitHub Copilot feedback. Authored the project report, presentation deck, speaker notes, and Q&A flashcards.

**Note on self-review.** I'd score myself at the same level as Akeeb and Zannat — different ownership areas, comparable depth and effort. Self-scoring is awkward; the form may reweight or normalise this.

---

### Pushkar Jadhav — score: **2 / 10**

**What he did.** Attended the introductory team meeting on 26 February and the roadmap meeting on 8 April. Was assigned the feature-selection task at the 8 April meeting. No deliverable from this assignment was committed to the team repository. Was present at the 14 April modelling progress meeting but did not present any work. No code, documentation, audit, or written contribution from him appears in the project repository or shared documents.

**Diplomatic framing for the form:**
> Pushkar attended the early team meetings and was assigned a feature-selection task during initial planning. Unfortunately no deliverable was submitted against this assignment, and no code or documentation contribution from him is recorded in the project repository. Engagement during later meetings was limited.

---

### Giridhar Nampally — score: **2 / 10**

**What he did.** Attended the introductory team meeting on 26 February, the roadmap meeting on 8 April, and the 14 April modelling progress meeting. No specific deliverable was assigned to him beyond general team participation. No code, documentation, or written contribution from him appears in the project repository or shared documents.

**Diplomatic framing for the form:**
> Giridhar attended team meetings during the planning phase. No specific deliverable was assigned to him at the task-allocation meeting and no code or documentation contribution from him is recorded in the project repository. Engagement in the technical work of the project was minimal.

---

### Poorna Golla — score: **2 / 10**

**What she did.** Attended the introductory team meeting on 26 February. Did not attend the 8 April roadmap meeting where tasks were allocated. No specific deliverable was assigned. No code, documentation, or written contribution from her appears in the project repository or shared documents.

**Diplomatic framing for the form:**
> Poorna attended the introductory team meeting. She was not present at the task-allocation meeting where individual contributions were planned, and no code or documentation contribution from her is recorded in the project repository. Engagement in the project beyond the introductory meeting was minimal.

---

## A note on diplomatic peer review

The framings above are **honest** — they describe what each member did or did not deliver — and **diplomatic** — they avoid emotional language ("did nothing", "freeloader", "useless"). Markers respect honest peer review. They have seen freeloaders before and they typically weight peer scores in a way that protects the contributors.

If you want to soften further, you can add a single sentence per low-scorer like *"This may reflect competing personal commitments rather than a lack of capability."* That gives them the benefit of the doubt without inventing contributions.

What you should **not** do:

- ❌ Score them 7+ as a courtesy. The form usually asks the marker to compare your peer scores against measurable repository contributions; mismatches get flagged.
- ❌ Fabricate specific contributions ("Pushkar implemented the feature selection module"). If a marker checks the repo, this falls apart.
- ❌ Score them 1/10. That reads as vindictive even when accurate. The 2/10 baseline acknowledges meeting attendance.

---

## Final tip

Some forms ask for a **strengths and weaknesses** split per peer rather than a single score. If yours does, here's a template:

**Strength of [name]:** *(specific positive thing — for low contributors, "attended introductory meetings and was open to participating" is fine)*
**Area for development of [name]:** *(specific actionable thing — "developing a habit of submitting deliverables against assigned tasks before the next sprint")*

Keep both halves under 30 words each. Markers reward specificity over praise.
