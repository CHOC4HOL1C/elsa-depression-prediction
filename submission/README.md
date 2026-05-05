# ELSA Depression Prediction

Early prediction of depression onset in older English adults using machine learning on longitudinal survey data.

**Module:** AI and Healthcare, University of Surrey, 2025/26  
**Dataset:** English Longitudinal Study of Ageing (ELSA), UKDS Study 5050  
**Team:** Akeeb Lawel, Fiyin Akano, Zannat Chowdhury Sagar, Giridhar Nampally, Pushkar Jadav, Poorna Golla

---

## Overview

This project trains machine learning models to predict whether an individual will develop clinically significant depression (CES-D >= 3) at Wave 8 of ELSA, using non-clinical survey data from Waves 6 and 7 collected two to four years earlier.

Three prediction arms are compared to answer distinct research questions about prediction horizon and the value of longitudinal data. Four models are evaluated across five feature configurations per arm, with hyperparameter tuning on the best configuration per arm.

GitHub Repo Link: https://github.com/CHOC4HOL1C/elsa-depression-prediction

### Research Questions

**RQ1** -- Can ML models trained on ELSA survey data predict depression onset 2 to 4 years in advance in adults aged 50 and over?

**RQ2** -- Does incorporating longitudinal information across two waves improve predictive performance, and does prediction horizon length affect accuracy?

**RQ3** -- Which feature domains carry independent predictive signal beyond prior depression history, and does the model retain clinically meaningful accuracy when prior depression scores are excluded?

### Key Results

| Arm | Best model | AUC | Recall |
|-----|-----------|-----|--------|
| W6 only (4-year horizon) | LGBM tuned | 0.819 | 0.732 |
| W7 only (2-year horizon) | RF tuned | 0.824 | 0.668 |
| W6+W7 combined | RF tuned | 0.848 | 0.714 |

Without prior CES-D scores, the W6+W7 model retains AUC 0.773 (91% of full model performance), confirming that the model learns genuine health and social risk factors beyond depression persistence tracking.

---

## How to Run

The submission notebook is designed to run end-to-end from a single path configuration. No other setup is required.

### Step 1 -- Get the data

Request access to ELSA (UKDS Study 5050) at [ukdataservice.ac.uk](https://ukdataservice.ac.uk). Download the Stata format package. You will receive a zip file or an extracted folder.

### Step 2 -- Open the notebook

Upload `submission/ELSA_Depression_Prediction_Final_v2.ipynb` to Google Colab (or run locally with Jupyter).

### Step 3 -- Set your path

In Section 0.1 (the first code cell), set `ELSA_PATH` to your data. The notebook handles both scenarios automatically:

```python
# Option A: path to the downloaded zip file
ELSA_PATH = "/content/drive/MyDrive/UKDA-5050-stata.zip"

# Option B: path to the extracted folder at any level
ELSA_PATH = "/content/drive/MyDrive/ELSA/data"
```

The path detection logic accepts a zip file, any parent directory at any depth, or the `stata13_se` folder directly. It searches downward using `rglob` and raises a clear error message if the data files cannot be found.

### Step 4 -- Run all

Runtime > Run all. The notebook installs any missing packages, locates the data files, runs all experiments, and copies outputs to your Drive.

**Expected runtime.** A `FAST_MODE` flag in Section 0.4 controls runtime vs. exact reproducibility:

| Setting | Tuning budget | SHAP sample | Colab CPU runtime | Use when |
|---|---|---|---|---|
| `FAST_MODE = True` (default) | 10 iter × 3 folds | 200 | ~15-25 min | Marking / quick review |
| `FAST_MODE = False` | 30 iter × 5 folds | 500 | ~60-90 min | Exact reproduction of the report's headline AUCs |

In fast mode, tuned AUCs typically land within 0.005-0.010 of the published values (the leakage drop, cross-arm ordering, SHAP rankings, and clinical conclusions are unchanged). Set `FAST_MODE = False` if you want to reproduce the exact numbers in `outputs/results/`.

---

## Outputs

All figures and results tables are saved to `/content/outputs/` and copied to Google Drive at the end of Section 9.

```
outputs/
├── figures/
│   ├── 01_data/
│   │   └── outcome_distribution.png
│   ├── 02_experiments/
│   │   └── auc_all_arms_configs.png
│   ├── 03_results/
│   │   ├── arm_comparison.png
│   │   ├── roc_curves.png
│   │   ├── pr_curves.png
│   │   ├── confusion_matrices.png
│   │   ├── threshold_optimisation.png
│   │   ├── ensemble_roc.png
│   │   └── stacking_ensemble_roc.png
│   ├── 04_interpretation/
│   │   ├── domain_ablation.png
│   │   ├── domain_correlation_heatmap.png
│   │   ├── feature_target_correlation.png
│   │   ├── shap_act1_full.png
│   │   ├── shap_act2_no_cesd.png
│   │   ├── lgbm_importance_top20.png
│   │   ├── lr_coefficients_standardised.png
│   │   ├── calibration.png
│   │   └── calibration_isotonic.png
│   └── 05_sensitivity/
│       └── leakage_sensitivity.png
└── results/
    ├── all_experiments.csv        (3 arms x 5 configs x 4 models)
    ├── tuned_models.csv           (best tuned model per arm)
    ├── domain_ablation.csv        (leave-one-domain-out AUC)
    ├── leakage_sensitivity.csv    (with vs without prior CES-D)
    ├── threshold_optimisation.csv (optimal F1 threshold per model)
    └── stacking_ensemble.csv      (stacking vs individual models)
```

---

## Repository Structure

```
elsa-depression-prediction/
├── submission/
│   ├── ELSA_Depression_Prediction_Final_v2.ipynb            FINAL SUBMISSION NOTEBOOK
│   ├── ELSA_Depression_Prediction_Final_v2_executed.ipynb   Bonus: pre-executed copy with all outputs embedded
│   ├── README.md                                            This file
│   ├── requirements.txt                                     Pinned dependencies
│   └── run_local.py                                         Optional helper: run the notebook locally without Colab
├── notebooks/                                              Earlier exploratory work (not needed for marking)
│   ├── 01_data_audit/ELSA_Audit_Notebook.ipynb              Akeeb -- audit and feature selection
│   ├── 02_data_loading/02_data_loading.ipynb                Data loading exploration
│   ├── 03_preprocessing/03_preprocessing_modelling.ipynb    Zannat -- W6 baseline, feature comparison
│   └── 05_modelling/
│       ├── depression_prediction_pipeline.ipynb              Fiyin -- W6+W7 longitudinal pipeline
│       └── depression_pipeline_enhanced.ipynb                Zannat -- extended analysis
├── outputs/                                                All saved figures and CSVs
├── presentation/                                           PowerPoint slides + speaker notes + Q&A flashcards
├── docs/                                                   Report (DOCX/MD), meeting minutes, peer review
├── config.py                                               Shared path configuration
└── README.md                                               Repository-level README
```

---

## Experimental Design

| Element | Detail |
|---------|--------|
| Outcome | CES-D >= 3 at Wave 8 (Steffick, 2000) |
| Class imbalance | class_weight='balanced' for LR and RF; scale_pos_weight=4 for XGBoost; class_weight='balanced' for LightGBM |
| Arms | W6 only, W7 only, W6+W7 combined |
| Feature configs | 5 per arm: full, no prior CES-D, health only, function/cognition, socioeconomic |
| Models | LR (baseline), RF (tuned), XGBoost (tuned), LightGBM (tuned) |
| Tuning | RandomizedSearchCV, 30 iterations, 5-fold stratified CV, scoring=roc_auc |
| Validation | Stratified 80/20 train/test split, same split reused across all arms |
| Primary metric | ROC-AUC (discrimination, threshold-independent) |
| Clinical metric | Binary F1 and Recall (depression detection performance) |
| Ensembles | Soft-vote (RF+XGB+LGBM) and stacking (RF+LGBM base, LR meta) |

---

## CES-D Scoring Note

ELSA's CES-D is scored as a sum of 8 binary items (yes/no), giving a range of 0 to 8. We use the IFS-validated `cesd_sc` variable from the IFS derived files. An earlier version of the preprocessing pipeline reconstructed the score from raw PSced items using a 0 to 3 per-item scale, which produced a range of 8 to 16 and approximately 74 percent apparent prevalence. This artefact is documented in `notebooks/03_preprocessing_modelling/` and corrected throughout the submission pipeline. The corrected prevalence is 19 percent, consistent with epidemiological estimates for English adults aged 50 and over.

---

## Wave Symmetry Enforcement

The neighbourhood deprivation index (`ndepriv`) was dropped from both waves because the Wave 7 version had 56 percent missing data in the training partition. The wave-symmetry rule requires that if a variable stem fails the missingness threshold at one wave, both wave versions are removed. This prevents the longitudinal model from using predictors that are asymmetrically available across time, which would produce an inconsistent measure across participants.

---

## Team Contributions

| Member | Primary contributions |
|--------|----------------------|
| Akeeb Lawel | Data audit, wave selection, feature selection pipeline, CES-D quality analysis, `analytic_sample.parquet` handoff |
| Fiyin Akano | Longitudinal pipeline (W6+W7), CES-D scoring fix, leakage sensitivity analysis, 11 presentation figures |
| Zannat Chowdhury Sagar | Preprocessing baseline, feature-set comparison (Config A vs B), enhanced pipeline (XGBoost, LightGBM, tuning, domain ablation, SHAP two-act narrative, calibration, ensemble), final submission notebook, README, PR reviews |
| Giridhar Nampally | Feature domain review, methodology input |
| Pushkar Jadav | Feature engineering input, presentation support |
| Poorna Golla | Evaluation metrics review, documentation support |

---

## Dependencies

```
pandas
numpy
pyreadstat
scikit-learn
xgboost
lightgbm
shap
matplotlib
seaborn
scipy
```

The notebook installs any missing packages automatically on first run via pip.

---

## References

Banks, J., Breeze, E., Lessof, C., and Nazroo, J. (Eds.). (2006). *Retirement, health and relationships of the older population in England: The 2004 English Longitudinal Study of Ageing*. London: Institute for Fiscal Studies.

Bergstra, J., and Bengio, Y. (2012). Random search for hyper-parameter optimization. *Journal of Machine Learning Research*, 13, 281-305.

Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., and Liu, T. Y. (2017). LightGBM: A highly efficient gradient boosting decision tree. *Advances in Neural Information Processing Systems*, 30.

Kessler, R. C. (2003). Epidemiology of women and depression. *Journal of Affective Disorders*, 74(1), 5-13.

Ohrnberger, J., Fichera, E., and Sutton, M. (2017). The relationship between physical and mental health: A mediation analysis. *Social Science and Medicine*, 195, 42-49.

Radloff, L. S. (1977). The CES-D scale: A self-report depression scale for research in the general population. *Applied Psychological Measurement*, 1(3), 385-401.

Steffick, D. E. (2000). *Documentation of affective functioning measures in the Health and Retirement Study*. HRS Documentation Report DR-005. Ann Arbor: University of Michigan.

Zaninotto, P., Sommerlad, A., Kivimaki, M., and Steptoe, A. (2019). The bidirectional association between depressive symptoms and cognitive decline in adults aged over 50. *Psychological Medicine*, 47(7), 1321-1334.

Zhao, Y., Wan, X., and Liu, Z. (2025). Machine learning identifies determinants of depressive symptoms in multinational middle-aged and older adults. *npj Digital Medicine*.
