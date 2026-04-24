# ELSA Depression Prediction

Early prediction of depression onset in older English adults using machine learning on longitudinal survey data.

**Module:** AI and Healthcare, University of Surrey, 2025/26  
**Dataset:** English Longitudinal Study of Ageing (ELSA), UKDS Study 5050

---

## Overview

This project trains machine learning models to predict whether an individual will develop clinically significant depression (CES-D >= 3) at Wave 8 of ELSA, using survey data from Waves 6 and 7 collected two to four years earlier. All predictors are non-clinical variables available in large population surveys, meaning the approach could scale to population-level screening.

Three prediction arms are compared:

| Arm | Predictors | Horizon |
|-----|-----------|---------|
| W6 only | Wave 6 features | ~4 years |
| W7 only | Wave 7 features | ~2 years |
| W6+W7 | Both waves + change features | 2-4 years |

Four models are evaluated across five feature configurations per arm: Logistic Regression, Random Forest, XGBoost, and LightGBM. The best configuration per arm is selected by cross-validated AUC and then hyperparameter tuned.

---

## Research Questions

**RQ1** -- Can ML models trained on ELSA survey data predict depression onset 2 to 4 years in advance in adults aged 50 and over?

**RQ2** -- Does incorporating longitudinal information across two waves improve predictive performance, and does prediction horizon length affect accuracy?

**RQ3** -- Which feature domains carry independent predictive signal beyond prior depression history?

---

## How to Run

The submission notebook is designed to run end-to-end with a single path configuration. No other setup is required.

### Step 1 -- Get the data

Request access to ELSA (UKDS Study 5050) at [ukdataservice.ac.uk](https://ukdataservice.ac.uk). Download the Stata format package. You will receive a zip file named something like `UKDA-5050-stata.zip`.

### Step 2 -- Open the notebook

Upload `ELSA_Depression_Prediction_Final.ipynb` to Google Colab (or run locally with Jupyter).

### Step 3 -- Set your path

In the first code cell (Section 0.1), set `ELSA_PATH` to point at your data. The notebook handles both scenarios automatically:

```python
# Option A: path to the downloaded zip file
ELSA_PATH = "/content/drive/MyDrive/UKDA-5050-stata.zip"

# Option B: path to the extracted folder (any level -- notebook finds stata13_se)
ELSA_PATH = "/content/drive/MyDrive/ELSA/data"
```

### Step 4 -- Run all

Runtime > Run all. The notebook will install any missing packages, locate the data files, run all experiments, and copy outputs to your Drive.

**Expected runtime:** 25 to 40 minutes on a standard Colab GPU/CPU instance, depending on hyperparameter tuning iterations.

---

## Outputs

All figures and results tables are saved to `/content/outputs/` and copied to Google Drive at the end.

```
outputs/
├── figures/
│   ├── 01_data/          outcome distribution, CES-D histogram
│   ├── 02_experiments/   AUC comparison charts per arm and config
│   ├── 03_results/       ROC curves, PR curves, confusion matrices, arm comparison
│   ├── 04_interpretation/ domain ablation, SHAP Act 1 and 2, calibration curves
│   └── 05_sensitivity/   leakage sensitivity (with vs without prior CES-D)
└── results/
    ├── all_experiments.csv    all arm x config x model combinations
    ├── tuned_models.csv       best tuned model per arm
    ├── domain_ablation.csv    leave-one-domain-out AUC
    └── leakage_sensitivity.csv with vs without prior CES-D across all arms
```

---

## Repository Structure

```
elsa-depression-prediction/
├── notebooks/
│   ├── 01_data_audit/
│   │   └── AI_Health_Group_Project.ipynb       # Akeeb -- data audit and feature selection
│   ├── 03_preprocessing_modelling/
│   │   └── 03_preprocessing_modelling.ipynb    # Zannat -- W6 baseline, feature comparison
│   └── 05_modelling/
│       ├── depression_prediction_pipeline.ipynb          # Fiyin -- W6+W7 longitudinal pipeline
│       └── depression_pipeline_enhanced_v2.ipynb         # Zannat -- extended analysis
├── submission/
│   └── ELSA_Depression_Prediction_Final.ipynb  # FINAL SUBMISSION NOTEBOOK
├── config.py                                    # shared path configuration
├── docs/
│   └── team_contributions.md
└── README.md
```

---

## Team and Contributions

| Member | Primary contributions |
|--------|----------------------|
| Akeeb Lawel | Data audit, wave selection, feature selection pipeline, CES-D quality analysis |
| Fiyin Akano | Longitudinal pipeline (W6+W7), leakage sensitivity analysis, 11 presentation figures |
| Zannat Chowdhury Sagar | Preprocessing baseline, feature-set comparison, enhanced pipeline (XGBoost, tuning, domain ablation, calibration, SHAP two-act narrative), final submission notebook |
| Giridhar Nampally | Feature domain review, report writing |
| Pushkar Jadav | Feature engineering input, presentation slides |
| Poorna Golla | Evaluation metrics review, report writing |

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

Install via: `pip install pandas numpy pyreadstat scikit-learn xgboost lightgbm shap matplotlib seaborn scipy`

The notebook installs missing packages automatically on first run.

---

## CES-D Scoring Note

ELSA's CES-D is scored as a sum of 8 binary items (yes/no), giving a range of 0 to 8. We use the IFS-validated `cesd_sc` variable from the IFS derived files. An earlier version of the preprocessing notebook reconstructed the score from raw PSced items using a 0-3 per-item scale, which produced a 8-16 range and ~74% apparent prevalence. This artefact is documented in the preprocessing notebook and corrected throughout the submission pipeline.

---

## References

Banks, J., Breeze, E., Lessof, C., and Nazroo, J. (Eds.). (2006). *Retirement, health and relationships of the older population in England: The 2004 English Longitudinal Study of Ageing*. London: Institute for Fiscal Studies.

Bergstra, J., and Bengio, Y. (2012). Random search for hyper-parameter optimization. *Journal of Machine Learning Research*, 13, 281-305.

Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., and Liu, T. Y. (2017). LightGBM: A highly efficient gradient boosting decision tree. *Advances in Neural Information Processing Systems*, 30.

Radloff, L. S. (1977). The CES-D scale: A self-report depression scale for research in the general population. *Applied Psychological Measurement*, 1(3), 385-401.

Steffick, D. E. (2000). *Documentation of affective functioning measures in the Health and Retirement Study*. HRS Documentation Report DR-005. Ann Arbor: University of Michigan.

Zhao, Y., Wan, X., and Liu, Z. (2025). Machine learning identifies determinants of depressive symptoms in multinational middle-aged and older adults. *npj Digital Medicine*.
