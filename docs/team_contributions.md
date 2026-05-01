# Team Contributions

University of Surrey — MSc AI & Healthcare, 2025/26  
ELSA Depression Prediction Group Project

---

## Akeeb Lawel — Data audit and feature selection

Established the empirical foundation of the project by auditing all available ELSA core waves (3-11) in a fully reproducible notebook (`notebooks/01_data_audit/ELSA_Audit_Notebook.ipynb`). The audit answered four scientific questions before any modelling work began: (1) which waves contain a usable CES-D measure, (2) participant overlap and attrition between waves, (3) feature drift across the panel, and (4) data governance for team sharing.

Quantified that all 9 core waves contain the 8 CES-D items with 93–97% valid response rates after recoding survey missing codes (-1, -8, -9), and that Waves 6, 7, and 8 form the strongest consecutive longitudinal block with >90% participant retention between adjacent waves. Showed that the union of variables across all waves is 13,920, of which only 2,656 are common to every wave — making the shared subset the only defensible feature pool for fully longitudinal modelling.

Produced the curated modelling feature list (`modelling_features_final_curated.csv`) by funneling 12,539 raw W6/W7 predictor candidates through a transparent rule-based pipeline (admin column removal → high-missingness filter → theory-led domain restriction → concept-prefix collapse), down to 30 final features grouped into Lu et al. (2025)-style domains. This list was used directly by the modelling notebooks downstream.

**Notebooks:** `notebooks/01_data_audit/ELSA_Audit_Notebook.ipynb`, `notebooks/01_data_audit/AI_Health_Group_Project.ipynb`

---

## Fiyin Akano — Longitudinal modelling pipeline and methodological QA

Built the original W6+W7 longitudinal modelling pipeline (`notebooks/05_modelling/depression_prediction_pipeline.ipynb`) end-to-end: data loading and merging across IFS-derived, core wave, and financial files; survey missing code recoding; engineering of 10 derived features (CES-D change, mobility/ADL/IADL counts, functional burden, mobility change); 9-domain feature grouping; Logistic Regression and Random Forest training with stratified 5-fold CV plus a 25% held-out test set; and full evaluation reporting (ROC-AUC, F1, precision, recall, accuracy, average precision, ROC curves, PR curves, confusion matrices).

Identified and corrected the CES-D scoring artefact in the original preprocessing logic. The earlier reconstruction of CES-D from raw PSced items used a 0–3 per-item scale, producing scores in the range 8–16 and an apparent prevalence of ~74% — clinically implausible. Switching to the IFS-validated `cesd_sc` (range 0–8) restored the expected ~19% prevalence and made the binary classification task scientifically meaningful.

Designed and implemented the leakage sensitivity analysis: re-running each model with and without prior CES-D features to test whether predictive power comes solely from depression history (state dependence) or whether non-mental-health features carry independent signal. The 0.07 AUC drop without CES-D became the central result for RQ3.

Produced the SHAP interpretability layer (`shap_summary_rf.png`, `shap_bar_rf.png`) using `TreeExplainer` on the Random Forest, surfacing which features drive individual predictions. Generated 11 presentation-ready figures saved to `outputs/figures/`.

Led the PR review cycle through 11 rounds of GitHub Copilot feedback (PR #2 → #6). Methodological improvements adopted include: removing personal paths from `config.py`, robust `REPO_ROOT` discovery via upward search for `config.py`, training-only computation of the 40% missingness drop threshold (eliminating test-set leakage in feature selection), and corrected axis labelling on the standardised LR coefficient plot. Acknowledged additional Copilot suggestions (lazy data path scanning, partial-sum imputation for `functional_burden`, CV-fold-internal missingness filtering) as documented limitations rather than fixing them, where the practical impact on results was negligible.

**Notebooks:** `notebooks/05_modelling/depression_prediction_pipeline.ipynb`

---

## Zannat Chowdhury Sagar — Submission notebook and extended analysis

Established the methodological foundation for the project through two core contributions.

First, designed and implemented the baseline preprocessing and feature comparison notebook (`notebooks/03_preprocessing/03_preprocessing_modelling.ipynb`), which validated the CES-D scoring fix in the data audit pipeline, compared IFS-derived features against core-wave-only features across three models, and established the single-wave (W6 only) performance baseline. Config B (IFS-enriched) consistently outperformed Config A by approximately 0.012 AUC, justifying the feature selection decisions in the main pipeline.

Second, designed and built the enhanced longitudinal pipeline (`notebooks/05_modelling/depression_pipeline_enhanced.ipynb`) and the final submission notebook (`submission/ELSA_Depression_Prediction_Final_v2.ipynb`). This included: adding XGBoost and LightGBM as additional models; implementing hyperparameter tuning via RandomizedSearchCV across all three prediction arms; designing the six-configuration feature registry for systematic experimentation; implementing wave-symmetry enforcement for the missingness drop; building the two-act SHAP narrative (full model vs no prior CES-D) that directly answers RQ3; adding calibration analysis with isotonic regression; implementing the complete domain ablation; and authoring the ensemble model.

Also authored the `submission/README.md`, led the PR review process for the final notebook, and contributed to the documentation of the CES-D scoring artefact as a methodological finding.

**Notebooks:** `notebooks/03_preprocessing/03_preprocessing_modelling.ipynb`, `notebooks/05_modelling/depression_pipeline_enhanced.ipynb`, `submission/ELSA_Depression_Prediction_Final_v2.ipynb`

---

## Giridhar Nampally — *(to be filled in)*

## Pushkar Jadav — *(to be filled in)*

## Poorna Golla — *(to be filled in)*
