# ELSA Depression Prediction — Submission Code

**Module:** AI and Healthcare (EEEM069)
**Group 4 — "Health is Wealth"**
**University of Surrey, MSc Artificial Intelligence (2025/26)**

---

## What's in this folder

| File | What it is | Recommended audience |
|------|------------|----------------------|
| `ELSA_Depression_Prediction.ipynb` | **Run-once submission notebook.** Self-contained, well-commented, ~10–15 min on Colab. Generates all headline results. | The marker — run this one. |
| `ELSA_Depression_Prediction_Full.ipynb` | **Full enhanced pipeline (appendix).** Three prediction arms × five feature configurations × four models = 60 baseline experiments, plus hyperparameter tuning, calibration, ensemble. ~30–45 min runtime. | Anyone wanting to see the full experimental sweep. |
| `requirements.txt` | Python dependencies. Auto-installed by the notebook on Colab. | Reference. |
| `build_submission_notebook.py` | The script used to generate the run-once notebook from a single source. Re-run this if the source ever needs editing. | Maintainers. |

---

## How to run the submission notebook

### Option A — Google Colab (recommended)

The notebook **finds your data automatically** if you put it in any of the standard places. Pick whichever is fastest for you.

#### Fastest — upload a zip directly to the Colab session (~5 minutes)

1. On your machine, zip the `UKDA-5050-stata` folder (right-click → Compress).
2. Open the notebook (`ELSA_Depression_Prediction.ipynb`) in Colab.
3. **Runtime → Run all.** When the notebook tells you it could not find data, run the **"Plan B — zip upload"** cell. It opens a file picker; choose your zip and the notebook unzips and continues automatically.

The data lives in the Colab session only and disappears when the session ends — fine for a single evaluation run.

#### Persistent — place data in Google Drive (~30 minutes upload, then permanent)

1. In `drive.google.com`, create a folder called `ELSA`.
2. Upload the entire `UKDA-5050-stata` folder into it. Final path should be `MyDrive/ELSA/UKDA-5050-stata/stata/stata13_se/`.
3. Open the notebook in Colab and click **Runtime → Run all.** It auto-mounts Drive and finds the data.

#### Manual override

If your data lives somewhere unusual, edit the single line in **Section 0**:

```python
ELSA_PATH = "/your/path/to/stata13_se"
```

### Option B — Local Jupyter

1. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Open the notebook in Jupyter / VS Code.
3. Either set `ELSA_PATH` explicitly in Section 0, or just leave it empty and the auto-locator will scan `~/Documents` for any `stata13_se` folder.
4. Run all cells.

---

## What the notebook produces

### Figures (in `outputs_submission/figures/`)

- `outcome_distribution.png` — Wave 8 CES-D histogram and class balance
- `roc_pr_curves.png` — ROC and Precision-Recall curves for all four models
- `confusion_matrices.png` — Confusion matrices for the best tree model and Logistic Regression baseline
- `shap_bar.png` — Top 20 features by mean |SHAP| value
- `shap_beeswarm.png` — SHAP beeswarm showing direction of effect
- `leakage_sensitivity.png` — AUC with vs. without prior CES-D features

### Results (in `outputs_submission/results/`)

- `test_set_results.csv` — Full metrics table (AUC, F1, precision, recall, accuracy, average precision) for all four models
- `leakage_sensitivity.csv` — AUC drop when CES-D features are removed, per model

### Console output

A final summary block prints sample size, prevalence, predictor count, all model AUCs, and the average leakage drop.

---

## Requirements

The notebook auto-installs anything missing on Colab. For reference:

```
numpy
pandas
matplotlib
seaborn
scikit-learn
xgboost
lightgbm
shap
```

All packages are pinned to the latest stable versions.

---

## Project documentation

The accompanying documentation is in the parent submission package:

- `documents/ELSA_Depression_Prediction_Report.docx` — full project report
- `documents/team_contributions.md` — per-member contribution summary
- `documents/Meeting_Minutes.docx` — group meeting minutes
- `presentation/ELSA_Depression_Prediction.pptx` — 10-minute presentation deck
- `presentation/SPEAKER_NOTES.md` — timed presenter scripts
- `presentation/QA_FLASHCARDS.md` — Q&A preparation flashcards

---

## Troubleshooting

**"ELSA_PATH does not exist"** — The `stata13_se` folder isn't where the notebook expects. Verify the path by listing the folder contents (`ls /content/drive/MyDrive/ELSA/UKDA-5050-stata/stata/stata13_se` in a code cell) and update `ELSA_PATH` accordingly.

**"Missing ELSA files"** — The path is correct but the expected `.dta` files aren't there. Check that you have the *Stata* version (not SPSS or tab) of UKDA-5050. The folder should contain files like `wave_6_elsa_data_v2.dta`.

**SHAP runs slowly** — Normal on Colab CPU. The notebook subsamples 1,000 rows for SHAP, which takes 1–2 minutes for Random Forest and ~30 seconds for XGBoost/LightGBM.

**Memory error on Colab** — Restart the runtime (Runtime → Restart) and run all cells again. ELSA core files are large (>1 GB combined) but the notebook only keeps the merged panel in memory.
