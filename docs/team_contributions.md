# Team Contributions

**Module:** AI and Healthcare (EEEM069), University of Surrey, 2025/26  
**Group:** Group 4 — Health is Wealth  
**Members:** Akeeb Lawel, Fiyin Akano, Zannat Chowdhury Sagar, Giridhar Nampally, Pushkar Jadav, Poorna Golla

---

## Akeeb Lawel

**Primary role:** Data custodian and audit lead

- Registered the group for ELSA access via the UK Data Service and coordinated data distribution to the team
- Built the full data audit notebook (`notebooks/01_data_audit/AI_Health_Group_Project.ipynb`) covering all ELSA waves 3 to 11
- Conducted CES-D quality analysis across waves, analysing valid response rates, score distributions, and missingness patterns
- Assessed participant overlap between consecutive wave pairs to identify the optimal longitudinal window
- Confirmed Waves 6, 7, and 8 as the strongest three-wave consecutive block based on over 90 percent participant overlap and 93 to 97 percent valid CES-D response rates
- Built the feature selection pipeline resulting in a curated list of approximately 30 predictors per wave (`modelling_features_final_curated.csv`)
- Produced `analytic_sample.parquet` as the clean handoff file for downstream modelling
- Opened PR for the audit notebook; addressed reviewer comments and merged to dev
- Documented the CES-D scoring artefact discovery in CONTEXT.md after it was identified during the modelling phase
- Presented the background, ELSA dataset, and wave selection sections of the group presentation

---

## Fiyin Akano

**Primary role:** Longitudinal pipeline lead

- Created a centralised project tracking document to coordinate team objectives and tasks from the outset
- Built the end-to-end W6+W7 to W8 longitudinal modelling pipeline (`notebooks/05_modelling/depression_prediction_pipeline.ipynb`) covering data loading, wave merging on `idauniq`, preprocessing, feature engineering, model training, and evaluation
- Identified and corrected the CES-D scoring artefact: traced the apparent 74 percent prevalence to a scale mismatch in the PSced reconstruction function, confirmed that ELSA items are binary (not 0 to 3 Likert), and switched to the IFS-validated `cesd_sc` variable (0 to 8 scale, 19 percent prevalence)
- Trained Logistic Regression and Random Forest on 139 features across 9 clinical domains with stratified 5-fold cross-validation and a held-out test set
- Implemented full evaluation suite: ROC-AUC, F1, precision, recall, PR curves, and confusion matrices
- Designed and implemented the leakage sensitivity analysis (with versus without prior CES-D), confirming AUC 0.842 with CES-D and AUC 0.776 without — establishing that the model retains meaningful predictive power beyond depression persistence tracking
- Integrated SHAP analysis for Random Forest feature interpretation
- Produced 11 presentation-ready figures and 3 results CSVs saved to structured output directories
- Updated `config.py` with robust repository root detection and auto-search for ELSA data path
- Opened PR to dev (`feat/w678-depression-modelling`), addressed all Copilot and reviewer comments across 4 commits, and resolved methodological issues including missingness leakage and LR coefficient labelling
- Drafted the project report and contributed to the presentation slide content covering pipeline methodology, headline results, and SHAP interpretation sections

---

## Zannat Chowdhury Sagar

**Primary role:** Modelling enhancement lead, pipeline architect, submission notebook author

**Baseline and feature comparison work:**

- Built the preprocessing and feature comparison notebook (`notebooks/03_preprocessing_modelling/03_preprocessing_modelling.ipynb`) establishing the single-wave W6 to W8 baseline
- Designed and implemented a two-configuration comparison: Config A (Akeeb's 30 core-wave features) versus Config B (proposed IFS-enriched set), demonstrating Config B outperforms Config A by approximately 0.012 AUC across all three models
- Implemented CES-D threshold validation cells documenting the scoring artefact empirically before the root cause was identified
- Opened and merged PR (`feat/preprocessing-baseline`) with full description of methodology and findings

**PR review and quality assurance:**

- Reviewed Fiyin's PR (#2) in depth: identified the binary F1 metric framing, confirmed the CES-D fix was correct, flagged XGBoost as missing from the comparison, and approved and merged the PR with substantive written commentary
- Identified the wave symmetry issue with `ndepriv` — that dropping `ndepriv_w7` for missingness while retaining `ndepriv_w6` creates an asymmetric longitudinal model — and implemented the stem-based wave symmetry enforcement fix

**Enhanced pipeline:**

- Added XGBoost and LightGBM to the modelling suite alongside LR and RF
- Designed and implemented the six-configuration feature registry (`full`, `no_cesd`, `health_only`, `function_cog`, `socioeconomic`, `w6_only`) for systematic comparison across arms
- Implemented hyperparameter tuning via `RandomizedSearchCV` (30 iterations, 5-fold stratified CV) for RF, XGB, and LightGBM
- Built the two-act SHAP narrative: Act 1 (full model, CES-D dominates) and Act 2 (no prior CES-D, self-rated health and mobility rise to top), directly answering RQ3
- Added calibration analysis with isotonic regression, confirming RF probability reliability improves substantially with negligible AUC cost
- Implemented complete domain ablation (leave-one-domain-out) and produced the domain correlation heatmap explaining near-zero ablation drops as a feature redundancy effect
- Added LR standardised coefficients plot and LightGBM gain-based importance for convergent interpretability evidence
- Added soft-vote ensemble (RF + XGB + LGBM) and stacking ensemble (RF + LGBM base, LR meta-learner), identifying that stacking achieves highest recall (0.773) of any configuration
- Added threshold optimisation, identifying RF optimal threshold at 0.58 giving F1 improvement of +0.024 over default
- Pushed and merged enhanced pipeline (`feat/enhanced-pipeline`) and final submission notebooks

**Final submission notebook:**

- Authored the complete final submission notebook (`submission/ELSA_Depression_Prediction_Final_v2.ipynb`) from scratch: three prediction arms (W6 only, W7 only, W6+W7), five feature configurations, four models, hyperparameter tuning, domain ablation, two-act SHAP, calibration, leakage sensitivity, ensemble analysis, and threshold optimisation
- Implemented the auto-detecting path loader accepting zip files, extracted directories at any depth, or the `stata13_se` folder directly — enabling one-cell setup for any invigilator
- Structured output into five figure subdirectories and a results directory, all copied to Drive at end of run

**Documentation and communication:**

- Authored the README with setup instructions, output directory reference, wave symmetry explanation, team contributions table, and full references
- Led all Git workflow decisions: branch naming, PR conventions, merge sequencing, final merge to main
- Authored the methods and findings report documenting all design decisions, results, and literature connections
- Drafted all team GC progress updates throughout the project
- Built the HTML presentation (`ELSA_Presentation.html`) with all 13 slides, custom dark theme, interactive navigation, inline data visualisations, and figure placement guides
- Presented the leakage sensitivity, limitations, and conclusions sections of the group presentation

---

## Giridhar Nampally

**Primary role:** Methodology review and Q&A support

- Reviewed classification evaluation metrics for imbalanced classes including ROC-AUC, F1, and precision-recall curves during the methodology framing phase
- Contributed to feature domain review discussions
- Assigned as backup Q&A responder for methodology questions during the live presentation, with QA flashcards prepared

---

## Pushkar Jadav

**Primary role:** Feature selection and presentation support

- Investigated feature selection methods during the methodology design phase
- Contributed to discussions on feature engineering decisions
- Served as timekeeper during the live presentation rehearsal and final delivery

---

## Poorna Golla

**Primary role:** Evaluation metrics review and documentation

- Reviewed classification evaluation metrics for imbalanced datasets alongside Giridhar during the methodology framing phase
- Contributed to documentation tasks
- Assigned as backup Q&A responder for background and dataset questions during the presentation, and responsible for circulating final meeting minutes to the team

---

## Git contribution summary

All code contributions are verifiable via the repository commit history at `github.com/CHOC4HOL1C/elsa-depression-prediction`. Key branches and PRs:

| Branch | Author | Description |
|--------|--------|-------------|
| `feat/data-audit` | Akeeb | Full ELSA audit notebook |
| `feat/preprocessing-baseline` | Zannat | W6 baseline and feature comparison |
| `feat/w678-depression-modelling` | Fiyin | W6+W7 longitudinal pipeline |
| `feat/enhanced-pipeline` | Zannat | XGBoost, tuning, SHAP narrative, calibration, ablation |
| `feat/final-submission-notebook` | Zannat | Complete submission notebook v2 |
