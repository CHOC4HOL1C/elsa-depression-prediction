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

### Option A — Google Colab (recommended; this is what we tested on)

1. Upload the notebook (`ELSA_Depression_Prediction.ipynb`) to Colab.
2. Make the **ELSA UKDA-5050 Stata folder** accessible to the Colab session. Two routes:
   - **From Google Drive:** copy the `UKDA-5050-stata` folder into your Drive, then mount Drive when prompted in the notebook (`/content/drive/MyDrive/ELSA/UKDA-5050-stata/stata/stata13_se`).
   - **Direct upload:** unzip the UKDA-5050 deposit into the Colab session's filesystem (`/content/UKDA-5050-stata/stata/stata13_se`).
3. Open the **Section 0 → "Set the data path"** cell and edit the `ELSA_PATH` variable to match where the `stata13_se` folder lives. This is the **only** edit required.
4. Choose **Runtime → Run all** (or `Cmd + F9` / `Ctrl + F9`).
5. Sit back. The notebook auto-installs missing packages, runs the full pipeline, and writes outputs to `outputs_submission/` next to the notebook.

### Option B — Local Jupyter

1. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Open the notebook in Jupyter / VS Code.
3. Edit `ELSA_PATH` in Section 0 to point at your local `stata13_se` folder.
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
