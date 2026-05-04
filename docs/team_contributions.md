# Team Contributions

| Member | Role | Notebooks | Notes |
|--------|------|-----------|-------|
| Zannat Chowdhury Sagar |Zannat Chowdhury Sagar
Established the methodological foundation for the project through two core contributions. First, designed and implemented the baseline preprocessing and feature comparison notebook (`03_preprocessing_modelling.ipynb`), which validated the CES-D scoring issue in the data audit pipeline, compared IFS-derived features against core-wave-only features across three models, and established the single-wave (W6 only) performance baseline. Config B (IFS-enriched) consistently outperformed Config A by approximately 0.012 AUC, justifying the feature selection decisions in the main pipeline.
Second, designed and built the enhanced longitudinal pipeline (`depression_pipeline_enhanced_v2.ipynb`) and the final submission notebook (`ELSA_Depression_Prediction_Final_v2.ipynb`). This included: adding XGBoost and LightGBM as additional models; implementing hyperparameter tuning via RandomizedSearchCV across all three prediction arms; designing the six-configuration feature registry for systematic experimentation; implementing wave-symmetry enforcement for the missingness drop; building the two-act SHAP narrative (full model vs no prior CES-D) that directly answers RQ3; adding calibration analysis with isotonic regression; implementing the complete domain ablation; and authoring the ensemble model. Also authored the README, led the PR review process, and identified and documented the CES-D scoring artefact as a methodological finding. |`03_preprocessing_modelling.ipynb`, `depression_pipeline_enhanced_v2.ipynb`, `ELSA_Depression_Prediction_Final.ipynb` | |
| Akeeb Lawel | | | |
| Fiyin Akano | | | |
| Giridhar Nampally | | | |
| Pushkar Jadav | | | |
| Poorna Golla | | | |
