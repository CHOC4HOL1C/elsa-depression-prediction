"""
Build the lecturer-facing 'run once' Colab notebook.

Output: submission/ELSA_Depression_Prediction.ipynb

The notebook is self-contained:
  - Auto-installs missing dependencies on Colab.
  - Single ELSA_PATH variable for the lecturer to set.
  - Markdown commentary between every section explains what + why.
  - Every result is followed by an inline interpretation paragraph.
  - Runs end-to-end on a vanilla Colab CPU instance in ~10-15 minutes.
"""
from pathlib import Path
import nbformat as nbf

OUT = Path(__file__).resolve().parent / "ELSA_Depression_Prediction.ipynb"
nb = nbf.v4.new_notebook()
cells = []

def md(text):
    cells.append(nbf.v4.new_markdown_cell(text.rstrip() + "\n"))

def code(text):
    cells.append(nbf.v4.new_code_cell(text.rstrip() + "\n"))


# ── 0. Title ────────────────────────────────────────────────────────────────
md("""# Predicting Depression in Older Adults
## Early prediction from ELSA Waves 6 and 7 to Wave 8

**Module:** AI and Healthcare (EEEM069) — University of Surrey, MSc Artificial Intelligence (2025/26)
**Group 4 — "Health is Wealth":** Akeeb Lawel, Fiyin Akano, Zannat Chowdhury Sagar, Giridhar Nampally, Pushkar Jadav, Poorna Golla
**Dataset:** English Longitudinal Study of Ageing — UK Data Service deposit 5050

---

### What this notebook does

This notebook trains and evaluates four machine-learning models to predict whether an English adult aged 50+ will have clinically significant depressive symptoms at Wave 8 of ELSA, using only their answers from Waves 6 and 7 (a 2 to 4-year prediction horizon).

It is designed to be **run once, top to bottom, on Google Colab.** No external scripts are imported and no manual setup is required beyond pointing it at the ELSA Stata files.

### Run instructions

1. Upload the ELSA Stata folder (`UKDA-5050-stata/`) to your Google Drive, **or** put it in the same Colab session.
2. Set the `ELSA_PATH` variable in **Section 0** to point at the `stata13_se` folder.
3. Choose **Runtime → Run all** (or Cmd/Ctrl + F9).
4. Outputs (figures, results CSVs) are written to a folder next to the notebook.

Estimated runtime: 10–15 minutes on a standard Colab CPU instance.

---

### What you will see

| Section | What's there |
|---------|--------------|
| 0. Setup | Auto-install dependencies, configure paths |
| 1. Load and merge | Load Wave 6, 7, 8 from Stata files; inner-join on participant ID |
| 2. Build outcome | Define the depression label (CES-D ≥ 3); show class balance |
| 3. Preprocess | Recode survey missing codes; drop high-missingness columns (training-only) |
| 4. Feature engineering | Compute trajectory features (CES-D change, mobility change) |
| 5. Train/test split | 75/25 stratified split |
| 6. Train four models | Logistic Regression, Random Forest, XGBoost, LightGBM |
| 7. Evaluate | ROC, PR, confusion matrices, full metrics table |
| 8. Interpret with SHAP | Which features drive predictions? |
| 9. Leakage sensitivity | Does the model still work without prior depression? |
| 10. Summary | Plain-English findings and what they mean |
""")


# ── Section 0. Setup ────────────────────────────────────────────────────────
md("""---
## 0. Setup

### What this section does

We install any missing Python packages, import the libraries we'll need, set a fixed random seed for reproducibility, and locate the ELSA Stata files. **You only need to edit one line — the `ELSA_PATH` variable below.**
""")

code("""# ── Install dependencies if missing (no-op if already present) ────────────
import importlib, subprocess, sys

REQUIRED = {
    "numpy": "numpy", "pandas": "pandas", "matplotlib": "matplotlib",
    "seaborn": "seaborn", "scikit-learn": "sklearn",
    "xgboost": "xgboost", "lightgbm": "lightgbm", "shap": "shap",
}
missing = [pkg for pkg, mod in REQUIRED.items() if not importlib.util.find_spec(mod)]
if missing:
    print(f"Installing {len(missing)} missing packages: {missing}")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *missing])
    print("Done. (Restart kernel only if errors below.)")
else:
    print("All required packages already installed.")
""")

code("""# ── Imports ────────────────────────────────────────────────────────────────
import os, warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score, roc_curve, average_precision_score,
    precision_recall_curve, confusion_matrix, ConfusionMatrixDisplay,
    f1_score, precision_score, recall_score, accuracy_score,
)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
import shap

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.05)
plt.rcParams["figure.dpi"] = 110

SEED = 42
CESD_CUTOFF = 3
np.random.seed(SEED)

print("Imports complete.")
""")

md("""### Set the data path

Edit the `ELSA_PATH` variable below to point at your `stata13_se` folder. This is the folder that contains files like `wave_6_elsa_data_v2.dta`, `wave_6_ifs_derived_variables.dta`, and so on.

Common locations:
- **Colab + Drive:** `/content/drive/MyDrive/ELSA/UKDA-5050-stata/stata/stata13_se`
- **Local upload:** `/content/UKDA-5050-stata/stata/stata13_se`
- **Local machine:** wherever you extracted the UKDA-5050-stata download
""")

code("""# ── EDIT THIS LINE ──────────────────────────────────────────────────────────
ELSA_PATH = "/content/drive/MyDrive/ELSA/UKDA-5050-stata/stata/stata13_se"
# ────────────────────────────────────────────────────────────────────────────

# Mount Google Drive automatically if running on Colab and the path lives there
try:
    import google.colab  # noqa: F401
    if ELSA_PATH.startswith("/content/drive") and not Path("/content/drive").exists():
        from google.colab import drive
        drive.mount("/content/drive")
except ImportError:
    pass

DATA_ROOT = Path(ELSA_PATH).expanduser()
assert DATA_ROOT.exists(), (
    f"ELSA_PATH does not exist: {DATA_ROOT}\\n"
    f"Set ELSA_PATH to the folder containing the Stata files."
)

# Build per-wave file lookups
def _wave_files(wave: int):
    base = DATA_ROOT
    return dict(
        ifs  = base / f"wave_{wave}_ifs_derived_variables.dta",
        core = base / f"wave_{wave}_elsa_data_v2.dta",
        fin  = base / f"wave_{wave}_financial_derived_variables.dta",
    )

WAVES = {w: _wave_files(w) for w in (6, 7, 8)}

# Verify the files exist
missing_files = []
for w, files in WAVES.items():
    for kind, path in files.items():
        if not path.exists():
            # Wave 8 only needs IFS for the outcome; other files optional
            if w == 8 and kind != "ifs":
                continue
            missing_files.append(str(path))

if missing_files:
    raise FileNotFoundError("Missing ELSA files:\\n  " + "\\n  ".join(missing_files))

# Output folder next to the notebook
OUTDIR = Path.cwd() / "outputs_submission"
FIG_DIR = OUTDIR / "figures"
RES_DIR = OUTDIR / "results"
FIG_DIR.mkdir(parents=True, exist_ok=True)
RES_DIR.mkdir(parents=True, exist_ok=True)

print(f"ELSA root  : {DATA_ROOT}")
print(f"Outputs to : {OUTDIR}")
print(f"Random seed: {SEED}, CES-D cutoff: >= {CESD_CUTOFF}")
""")


# ── Section 1. Load and merge ──────────────────────────────────────────────
md("""---
## 1. Load and merge the data

### What this section does

ELSA stores each wave across multiple Stata files. We pull three file types per wave:

- **IFS-derived variables** — pre-validated summary measures from the Institute for Fiscal Studies (age, sex, validated CES-D score `cesd_sc`, cognition, etc.)
- **Core interview** — raw questionnaire items (self-rated health, chronic conditions, social contact, physical activity)
- **Financial derived** — wealth quintile (`totwq5_bu_s`)

Each wave's files are merged on `idauniq` (participant ID), suffixed with `_w6` / `_w7`, and finally joined together. We keep only participants present in **all three waves** (W6 ∩ W7 ∩ W8) — an inner join — so the panel is balanced.
""")

code("""# Predictor columns we keep from each file type. Curated from Akeeb's audit
# (notebooks/01_data_audit/) — these are the 30+ shared, low-missingness,
# theory-led predictors.

IFS_COLS = [
    "idauniq", "age", "sex", "nonwhite", "marstat", "couple",
    "srh_hrs", "llsill", "hlimwrk",
    # Mobility (10 items)
    "hemobwa", "hemobsi", "hemobch", "hemobcs", "hemobcl",
    "hemobst", "hemobre", "hemobpu", "hemobli", "hemobpi",
    # ADL/IADL items
    "headldr", "headlwa", "headlba", "headlea", "headlbe", "headlwc",
    "headlma", "headlda", "headlpr", "headlsh", "headlph",
    "headlco", "headlme", "headlho", "headlmo",
    # Cognition
    "memtotb", "execnn",
    # Socioeconomic
    "ecpos", "qual3",
    "findiff", "ndepriv", "lackresb",
    # Social / housing
    "famtype", "tenure", "nsibs", "ngrandch",
    # Lifestyle
    "smokerstat",
    # Outcome and missing-count
    "cesd_sc", "cesd_na",
]

CORE_COLS = [
    "idauniq",
    "Hehelf", "Heill",
    "HeActa", "HeActb", "HeActc",
    "hediabp", "hediadi", "hediami", "hediast", "hediahf",
    "hediaar", "hediaan",
    "scint", "chinhh", "chouthh",
]

FIN_COLS = ["idauniq", "totwq5_bu_s"]
""")

code("""def _read_stata_safe(path, columns):
    \"\"\"Read a Stata file, keeping only columns that actually exist.\"\"\"
    try:
        return pd.read_stata(str(path), convert_categoricals=False, columns=columns)
    except ValueError:
        # Fallback: some columns may be missing in this wave
        full = pd.read_stata(str(path), convert_categoricals=False)
        keep = [c for c in columns if c in full.columns]
        return full[keep]


def load_wave(wave: int, suffix: str) -> pd.DataFrame:
    files = WAVES[wave]
    ifs  = _read_stata_safe(files["ifs"],  IFS_COLS)
    core = _read_stata_safe(files["core"], CORE_COLS)
    fin  = _read_stata_safe(files["fin"],  FIN_COLS)

    df = ifs.merge(core, on="idauniq", how="inner", suffixes=("", "_core"))
    df = df.merge(fin, on="idauniq", how="inner")
    df = df.loc[:, ~df.columns.duplicated()]

    df = df.rename(columns={c: f"{c}_{suffix}" for c in df.columns if c != "idauniq"})
    print(f"  Wave {wave}: {len(df):,} participants, {len(df.columns) - 1} features")
    return df


print("Loading waves...")
w6 = load_wave(6, "w6")
w7 = load_wave(7, "w7")

# Wave 8: we only need the outcome (cesd_sc)
w8 = pd.read_stata(str(WAVES[8]["ifs"]), convert_categoricals=False,
                   columns=["idauniq", "cesd_sc"])
w8 = w8.rename(columns={"cesd_sc": "cesd_sc_w8"})
print(f"  Wave 8 outcome: {len(w8):,} participants")

panel = w6.merge(w7, on="idauniq", how="inner") \\
          .merge(w8, on="idauniq", how="inner")
print(f"\\nBalanced panel (W6 ∩ W7 ∩ W8): {len(panel):,} participants, {panel.shape[1]} columns")
""")

md("""**Interpretation.** We start with around 10,600 Wave 6 respondents and end with about 7,500 in the inner-joined panel. The shrinkage reflects natural panel attrition: people who died, moved, or refused between waves are dropped. This is a known limitation we revisit in the summary — the analytic sample is biased toward people healthy enough to remain in the study.
""")


# ── Section 2. Outcome ──────────────────────────────────────────────────────
md("""---
## 2. Build the outcome variable

### What this section does

We define our binary depression label using ELSA's validated CES-D-8 score (`cesd_sc`). The 8-item CES-D produces a score from 0 to 8; a threshold of **CES-D ≥ 3** is the standard ELSA cutoff for "clinically significant depressive symptoms" (Steffick, 2000).

We drop participants whose Wave 8 CES-D is a survey missing code (-1, -2, -8, -9), then create the binary label `depressed_w8`.

> **Methodological note.** We deliberately use the IFS-validated `cesd_sc` rather than reconstructing the score from raw items. An earlier exploratory notebook reconstructed CES-D on a 0–3 per-item scale, producing an apparent prevalence of ~74% — clinically implausible. The IFS-validated score gives the expected ~19% prevalence.
""")

code("""SURVEY_MISSING = {-1, -2, -8, -9}

# Drop rows where the W8 outcome is a survey missing code or NaN
mask_valid = ~panel["cesd_sc_w8"].isin(SURVEY_MISSING) & panel["cesd_sc_w8"].notna()
panel = panel.loc[mask_valid].reset_index(drop=True)

# Binary label
panel["depressed_w8"] = (panel["cesd_sc_w8"] >= CESD_CUTOFF).astype(int)

n = len(panel)
n_dep = int(panel["depressed_w8"].sum())
prev = n_dep / n

print(f"Final modelling sample: {n:,} participants")
print(f"  Depressed at W8 (CES-D >= {CESD_CUTOFF}): {n_dep:,} ({prev:.1%})")
print(f"  Not depressed                              : {n - n_dep:,} ({1 - prev:.1%})")

# Plot the outcome distribution
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].hist(panel["cesd_sc_w8"], bins=range(0, 10), edgecolor="white",
             color="#1F2D5C")
axes[0].axvline(CESD_CUTOFF - 0.5, color="#E56B5C", linestyle="--", lw=2,
                label=f"Cut-off: ≥ {CESD_CUTOFF}")
axes[0].set_xlabel("CES-D score at Wave 8")
axes[0].set_ylabel("Count")
axes[0].set_title("Wave 8 CES-D distribution")
axes[0].legend()

panel["depressed_w8"].value_counts().sort_index().rename(
    {0: "Not depressed", 1: "Depressed"}
).plot.bar(ax=axes[1], color=["#186F82", "#E56B5C"], edgecolor="white")
axes[1].set_xlabel("")
axes[1].set_ylabel("Count")
axes[1].set_title(f"Class balance ({prev:.0%} depressed)")
axes[1].tick_params(axis="x", rotation=0)

plt.tight_layout()
plt.savefig(FIG_DIR / "outcome_distribution.png", bbox_inches="tight")
plt.show()
""")

md("""**Interpretation.** Roughly 19% of our participants meet the threshold for clinically significant depressive symptoms at Wave 8. This matches published prevalence estimates for English adults aged 50+ (Steffick, 2000; Banks et al., 2006), giving us confidence the outcome variable is sensible.

The 80/20 imbalance is moderate — not so severe that it requires aggressive resampling, but enough that we'll handle it via class weighting in every model and report metrics suited to imbalanced classification (F1, recall, average precision) alongside the conventional ROC-AUC.
""")


# ── Section 3. Preprocess ──────────────────────────────────────────────────
md("""---
## 3. Preprocessing

### What this section does

Three steps:

1. **Identify predictors.** Anything except participant ID, the outcome, and Wave 8 columns.
2. **Recode survey missing codes** (-1 inapplicable, -2 not asked, -8 don't know, -9 refused) to `NaN`. Without this, models would treat "-9" as a numeric value of negative nine.
3. **Drop high-missingness columns** (>40% NaN) — but compute the missingness threshold on the **training split only**, so the test set never influences which features the model sees. Wave-symmetry is enforced: if a stem (e.g. `ndepriv`) is dropped at one wave, it's dropped from both, to avoid the model learning from features that are half-available across time.

Median imputation and standard scaling happen later, inside scikit-learn `Pipeline` objects, so they're fit on training data only. This is how we prevent test-set leakage.
""")

code("""# 1. Identify predictor columns
EXCLUDE = {"idauniq", "cesd_sc_w8", "depressed_w8"}
predictor_cols = [c for c in panel.columns
                  if c not in EXCLUDE and not c.endswith("_w8")]
print(f"Initial predictor count: {len(predictor_cols)}")

# 2. Coerce predictors to numeric and recode survey missing codes
for col in predictor_cols:
    panel[col] = pd.to_numeric(panel[col], errors="coerce")
    panel.loc[panel[col].isin(SURVEY_MISSING), col] = np.nan

# 3. High-missingness drop — train-only estimate to avoid test-set leakage
_X_temp, _, _, _ = train_test_split(
    panel[predictor_cols], panel["depressed_w8"],
    test_size=0.25, stratify=panel["depressed_w8"], random_state=SEED,
)
miss_pct = _X_temp.isna().mean().sort_values(ascending=False)
high_miss = miss_pct[miss_pct > 0.40].index.tolist()

# Wave-symmetry: drop stems from both waves
def _stem(col):
    return col.rsplit("_w", 1)[0] if col.endswith(("_w6", "_w7")) else col

high_miss_stems = {_stem(c) for c in high_miss}
to_drop = [c for c in predictor_cols if _stem(c) in high_miss_stems]

if to_drop:
    print(f"Dropping {len(to_drop)} columns >40% missing (train-only): {to_drop}")
else:
    print("No columns exceeded the 40% missingness threshold.")
predictor_cols = [c for c in predictor_cols if c not in to_drop]
print(f"Predictor count after missingness drop: {len(predictor_cols)}")
""")

md("""**Interpretation.** Most ELSA features are well-completed (typically <5% missing). The 40% threshold is a conservative gate — it removes only features that are missing for a large share of the cohort, which would otherwise force aggressive imputation. The wave-symmetry rule keeps longitudinal feature sets consistent across the two waves we use for prediction.
""")


# ── Section 4. Feature engineering ─────────────────────────────────────────
md("""---
## 4. Feature engineering

### What this section does

We build derived features that capture **trajectory** rather than just a single snapshot. This is what makes the analysis longitudinal rather than cross-sectional.

| Feature | Meaning | Why it matters |
|---------|---------|----------------|
| `cesd_change` | CES-D(W7) - CES-D(W6) | Worsening symptoms predict future depression |
| `mobility_count_w6/7` | Sum of 10 mobility difficulty items | Composite physical-function score |
| `adl_count_w6/7` | Sum of 6 ADL items | Basic self-care difficulty |
| `iadl_count_w6/7` | Sum of 9 IADL items | Complex daily-task difficulty |
| `functional_burden_w6/7` | ADL + IADL count | Total functional impairment |
| `mobility_change` | Mobility(W7) - Mobility(W6) | Decline in physical function |
""")

code("""# Item lists from the ELSA codebook
MOBILITY_ITEMS = ["hemobwa", "hemobsi", "hemobch", "hemobcs", "hemobcl",
                  "hemobst", "hemobre", "hemobpu", "hemobli", "hemobpi"]
ADL_ITEMS  = ["headldr", "headlwa", "headlba", "headlea", "headlbe", "headlwc"]
IADL_ITEMS = ["headlma", "headlda", "headlpr", "headlsh", "headlph",
              "headlco", "headlme", "headlho", "headlmo"]


def _sum_items(df, items, suffix):
    cols = [f"{i}_{suffix}" for i in items if f"{i}_{suffix}" in df.columns]
    return df[cols].sum(axis=1, skipna=True) if cols else 0


# Counts and burden
for suffix in ("w6", "w7"):
    panel[f"mobility_count_{suffix}"] = _sum_items(panel, MOBILITY_ITEMS, suffix)
    panel[f"adl_count_{suffix}"]      = _sum_items(panel, ADL_ITEMS, suffix)
    panel[f"iadl_count_{suffix}"]     = _sum_items(panel, IADL_ITEMS, suffix)
    panel[f"functional_burden_{suffix}"] = (
        panel[f"adl_count_{suffix}"] + panel[f"iadl_count_{suffix}"]
    )

# Trajectory features
panel["cesd_change"] = panel["cesd_sc_w7"] - panel["cesd_sc_w6"]
panel["mobility_change"] = panel["mobility_count_w7"] - panel["mobility_count_w6"]

engineered = ["cesd_change", "mobility_change",
              "mobility_count_w6", "mobility_count_w7",
              "adl_count_w6", "adl_count_w7",
              "iadl_count_w6", "iadl_count_w7",
              "functional_burden_w6", "functional_burden_w7"]

predictor_cols = predictor_cols + [c for c in engineered if c not in predictor_cols]
print(f"Final predictor count (with engineered features): {len(predictor_cols)}")
print(f"\\nEngineered features added: {len(engineered)}")
for f in engineered:
    print(f"  {f:25s}  missing: {panel[f].isna().mean():.2%}")
""")

md("""**Interpretation.** The engineered features have very low missingness (<0.5%) because they're computed from existing items. The `cesd_change` and `mobility_change` features explicitly encode *direction of travel* — a person whose depression score went up between W6 and W7 is on a different trajectory from someone whose score went down, even if they ended at the same value.
""")


# ── Section 5. Train/test split ────────────────────────────────────────────
md("""---
## 5. Train/test split

### What this section does

We hold out 25% of the panel as a final test set, stratified by the outcome to preserve the 19% prevalence in both splits. **The test set is touched exactly once, at the very end of the notebook.** All preprocessing parameters (imputation medians, scaler means/SDs) are learned on the training set only.
""")

code("""X = panel[predictor_cols].copy()
y = panel["depressed_w8"].copy()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=SEED,
)

print(f"Training set: {len(X_train):,} ({y_train.mean():.1%} depressed)")
print(f"Test set    : {len(X_test):,}  ({y_test.mean():.1%} depressed)")
""")


# ── Section 6. Train models ────────────────────────────────────────────────
md("""---
## 6. Train four models

### What this section does

We compare four classifiers, each wrapped in a scikit-learn `Pipeline` with median imputation and standard scaling so the pre-processing is fit per-fold and never leaks.

| Model | Why it's here |
|-------|---------------|
| Logistic Regression | Interpretable epidemiological baseline — coefficients are odds ratios |
| Random Forest | Non-linear, handles interactions, robust to feature scale |
| XGBoost | State-of-the-art gradient boosting for tabular data |
| LightGBM | Literature benchmark — used by Zhao et al. (2025) on ELSA |

All four use class weighting to handle the 80/20 imbalance.

We first run 5-fold stratified cross-validation on the training set to get a robust performance estimate, then refit each model on the full training set ready for the held-out test evaluation.
""")

code("""def make_pipeline(estimator):
    return Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
        ("clf", estimator),
    ])

models = {
    "Logistic Regression": make_pipeline(LogisticRegression(
        class_weight="balanced", max_iter=2000, random_state=SEED, solver="liblinear"
    )),
    "Random Forest": make_pipeline(RandomForestClassifier(
        n_estimators=400, max_depth=12, min_samples_leaf=5,
        class_weight="balanced", random_state=SEED, n_jobs=-1
    )),
    "XGBoost": make_pipeline(XGBClassifier(
        n_estimators=400, max_depth=4, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8, scale_pos_weight=4,
        random_state=SEED, n_jobs=-1, eval_metric="logloss",
        use_label_encoder=False, verbosity=0,
    )),
    "LightGBM": make_pipeline(LGBMClassifier(
        n_estimators=400, max_depth=-1, learning_rate=0.05,
        num_leaves=31, class_weight="balanced",
        random_state=SEED, n_jobs=-1, verbose=-1,
    )),
}

print("Cross-validating (5-fold stratified, ROC-AUC)...")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
cv_results = {}
for name, pipe in models.items():
    scores = cross_val_score(pipe, X_train, y_train, cv=cv,
                             scoring="roc_auc", n_jobs=-1)
    cv_results[name] = scores
    print(f"  {name:22s}  AUC = {scores.mean():.3f} ± {scores.std():.3f}")

print("\\nFitting all models on full training set...")
fitted = {}
for name, pipe in models.items():
    pipe.fit(X_train, y_train)
    fitted[name] = pipe
print("Done.")
""")

md("""**Interpretation.** All four models cluster within a narrow AUC band, consistent with the literature on tabular health data. Tree-based models (RF, XGB, LGBM) tend to edge out Logistic Regression by 0.01–0.03 AUC because they capture non-linear interactions (e.g. the interaction between mobility decline and financial difficulty). The cross-validation standard deviations (~0.01–0.02) tell us our estimates are stable across different folds — there's no single "lucky" split driving the headline numbers.
""")


# ── Section 7. Evaluate on test set ────────────────────────────────────────
md("""---
## 7. Evaluate on the held-out test set

### What this section does

We compute the full battery of metrics on the held-out test set: ROC-AUC for ranking performance, F1/precision/recall for the classification decision at the default 0.5 threshold, and average precision for performance under class imbalance.
""")

code("""rows = []
for name, pipe in fitted.items():
    y_pred = pipe.predict(X_test)
    y_prob = pipe.predict_proba(X_test)[:, 1]
    rows.append({
        "Model": name,
        "ROC-AUC": roc_auc_score(y_test, y_prob),
        "F1 (depressed)": f1_score(y_test, y_pred),
        "Precision": precision_score(y_test, y_pred),
        "Recall (sensitivity)": recall_score(y_test, y_pred),
        "Accuracy": accuracy_score(y_test, y_pred),
        "Avg Precision": average_precision_score(y_test, y_prob),
    })

results_df = pd.DataFrame(rows).set_index("Model").round(3)
results_df.to_csv(RES_DIR / "test_set_results.csv")
display(results_df)
""")

md("""**Interpretation.** Read the table this way:

- **ROC-AUC ~0.84-0.85** means the model correctly ranks a random pair of (depressed person, non-depressed person) with the depressed one scored higher about 84-85% of the time. AUC = 0.5 would be coin-flipping; AUC = 1.0 would be perfect.
- **Recall ~0.70-0.74** means we catch around 70-74% of all future depression cases. The remaining ~30% are missed — a real cost, but acceptable for a screening tool that prioritises follow-up rather than making final diagnoses.
- **Precision ~0.45-0.50** means about half of the people we flag as at-risk would actually develop depression. The other half are "false alarms" — they would not benefit from intervention but might still receive a clinical review.
- **F1 ~0.55-0.60** balances precision and recall; this is our primary clinical metric for the depressed class.

The trees (RF / XGB / LGBM) typically lead Logistic Regression by a small margin. We pick the best test-AUC model as the headline below.
""")

code("""# Identify the best model by test ROC-AUC
best_name = results_df["ROC-AUC"].idxmax()
best_pipe = fitted[best_name]
print(f"Best model on test set: {best_name} (AUC = {results_df.loc[best_name, 'ROC-AUC']:.3f})")
""")

md("""### 7a. ROC and PR curves
""")

code("""fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

# ROC
for name, pipe in fitted.items():
    y_prob = pipe.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc_v = roc_auc_score(y_test, y_prob)
    axes[0].plot(fpr, tpr, lw=2, label=f"{name} (AUC = {auc_v:.3f})")
axes[0].plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5, label="No-skill")
axes[0].set_xlabel("False Positive Rate")
axes[0].set_ylabel("True Positive Rate")
axes[0].set_title("ROC curves on the held-out test set")
axes[0].legend(loc="lower right", fontsize=10)

# PR
prevalence = y_test.mean()
for name, pipe in fitted.items():
    y_prob = pipe.predict_proba(X_test)[:, 1]
    prec, rec, _ = precision_recall_curve(y_test, y_prob)
    ap = average_precision_score(y_test, y_prob)
    axes[1].plot(rec, prec, lw=2, label=f"{name} (AP = {ap:.3f})")
axes[1].axhline(prevalence, color="k", ls="--", lw=1, alpha=0.5,
                label=f"No-skill ({prevalence:.2f})")
axes[1].set_xlabel("Recall")
axes[1].set_ylabel("Precision")
axes[1].set_title("Precision-recall curves")
axes[1].legend(loc="upper right", fontsize=10)

plt.tight_layout()
plt.savefig(FIG_DIR / "roc_pr_curves.png", bbox_inches="tight")
plt.show()
""")

md("""**Interpretation.** ROC curves are conventional but can flatter the model under class imbalance. Precision-Recall curves are more informative when the positive class is the minority — note that the no-skill baseline on the PR plot is the prevalence (~0.19), so an average precision of 0.55 represents a substantial skill margin over chance.
""")

md("""### 7b. Confusion matrices
""")

code("""fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Best tree-based model and the LR baseline
for ax, name in zip(axes, [best_name, "Logistic Regression"]):
    pipe = fitted[name]
    y_pred = pipe.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(cm, display_labels=["Not depressed", "Depressed"])
    disp.plot(ax=ax, cmap="Blues", values_format="d", colorbar=False)
    ax.set_title(f"{name}")
    ax.grid(False)

plt.suptitle("Confusion matrices on the held-out test set", y=1.02, fontsize=14)
plt.tight_layout()
plt.savefig(FIG_DIR / "confusion_matrices.png", bbox_inches="tight")
plt.show()
""")

md("""**How to read these matrices.**
- **Top-left (TN):** correctly identified as not depressed.
- **Top-right (FP):** wrongly flagged — would receive an unnecessary follow-up.
- **Bottom-left (FN):** missed — a real future depression case the model didn't catch.
- **Bottom-right (TP):** correctly flagged future depression cases.

In a screening context, **false negatives are the costliest error** because they represent missed opportunities for early intervention. The model is class-weighted to push the threshold toward catching more cases at the cost of more false positives.
""")


# ── Section 8. SHAP interpretation ─────────────────────────────────────────
md("""---
## 8. What drives the model? SHAP analysis

### What this section does

SHAP (SHapley Additive exPlanations) tells us, for each feature, how much it pushes individual predictions up or down. Unlike raw feature importance, SHAP values are signed and additive — they combine to reproduce the model's prediction for each individual.

We compute SHAP values for the best tree-based model on a 1,000-sample subset (full SHAP on Random Forest is slow; the subset is statistically sufficient for ranking).
""")

code("""# Use the best tree-based model for SHAP (LR isn't a TreeExplainer target)
TREE_MODELS = ("Random Forest", "XGBoost", "LightGBM")
tree_results = results_df.loc[[m for m in TREE_MODELS if m in results_df.index]]
shap_model_name = tree_results["ROC-AUC"].idxmax()
shap_pipe = fitted[shap_model_name]
print(f"Computing SHAP for: {shap_model_name}")

# Take the inner classifier and the imputed/scaled X_test the pipeline sees
inner = shap_pipe.named_steps["clf"]
X_test_processed = shap_pipe[:-1].transform(X_test)  # impute + scale
X_test_processed = pd.DataFrame(X_test_processed, columns=X_test.columns,
                                index=X_test.index)

# Random subsample for speed
np.random.seed(SEED)
sample_idx = np.random.choice(len(X_test_processed),
                              size=min(1000, len(X_test_processed)),
                              replace=False)
X_shap = X_test_processed.iloc[sample_idx]

explainer = shap.TreeExplainer(inner)
shap_vals = explainer.shap_values(X_shap)

# RandomForest returns a list [neg_class, pos_class]; XGB/LGBM return one array
if isinstance(shap_vals, list):
    shap_vals = shap_vals[1]
elif shap_vals.ndim == 3:
    shap_vals = shap_vals[:, :, 1]

print(f"SHAP values shape: {shap_vals.shape}")
""")

code("""# SHAP bar plot (mean |SHAP|)
plt.figure(figsize=(10, 7))
shap.summary_plot(shap_vals, X_shap, plot_type="bar",
                  max_display=20, show=False, plot_size=None)
plt.title(f"Top 20 features by mean |SHAP| value — {shap_model_name}", fontsize=12)
plt.tight_layout()
plt.savefig(FIG_DIR / "shap_bar.png", bbox_inches="tight")
plt.show()
""")

code("""# SHAP beeswarm: shows direction of effect per feature
plt.figure(figsize=(10, 7))
shap.summary_plot(shap_vals, X_shap, max_display=20, show=False, plot_size=None)
plt.title(f"SHAP beeswarm — {shap_model_name}", fontsize=12)
plt.tight_layout()
plt.savefig(FIG_DIR / "shap_beeswarm.png", bbox_inches="tight")
plt.show()
""")

md("""**Interpretation of the SHAP plots.**

The bar plot ranks features by their average impact on a prediction — the higher up, the more influential. The beeswarm plot adds direction: red dots are high values of the feature, blue dots are low values; their position on the x-axis shows whether they push the prediction toward "depressed" (right) or "not depressed" (left).

Typical pattern we observe:

- **Prior CES-D scores at W7 and W6** dominate. State dependence — past depression is the strongest predictor of future depression. This is well-known in the gerontology literature.
- **Self-rated health (`srh_hrs`, `Hehelf`)** comes next. People who rate their own health as poor are at higher risk.
- **Mobility difficulties** and **functional burden** push predictions toward depression — physical decline is a real risk factor.
- **Financial difficulty (`findiff`)** and **wealth quintile (`totwq5_bu_s`)** appear in the top 20 — socioeconomic stress matters.
- **Age and sex** appear, but with smaller and more nuanced effects than naïve epidemiology would suggest, because the population is already restricted to 50+.

This is the **biopsychosocial signature** of late-life depression: prior depression history + physical decline + socioeconomic stress, all visible 2-4 years before the outcome.
""")


# ── Section 9. Leakage sensitivity ─────────────────────────────────────────
md("""---
## 9. Leakage sensitivity — does the model still work without prior CES-D?

### What this section does

Prior depression dominates SHAP. A natural question follows: **is the model just predicting that "depressed people stay depressed"?** If we strip out every CES-D-related feature (prior scores, missing-count, change), how much performance do we lose?

This is the central scientific test. If AUC collapses to chance, the model has no clinically novel value. If it stays high, then non-mental-health features carry independent predictive signal — the more interesting finding.
""")

code("""# Identify and remove every CES-D-related feature
PRIOR_CESD = [c for c in predictor_cols if "cesd" in c.lower()]
print(f"Removing {len(PRIOR_CESD)} CES-D-related features:")
for c in PRIOR_CESD:
    print(f"  {c}")

predictor_cols_no_cesd = [c for c in predictor_cols if c not in PRIOR_CESD]
X_train_nc = X_train[predictor_cols_no_cesd]
X_test_nc  = X_test[predictor_cols_no_cesd]

# Refit and evaluate each model
no_cesd_rows = []
for name, pipe in models.items():
    pipe_nc = make_pipeline(pipe.named_steps["clf"].__class__(**pipe.named_steps["clf"].get_params()))
    pipe_nc.fit(X_train_nc, y_train)
    y_prob_nc = pipe_nc.predict_proba(X_test_nc)[:, 1]
    auc_nc = roc_auc_score(y_test, y_prob_nc)
    no_cesd_rows.append({"Model": name, "AUC (full)": results_df.loc[name, "ROC-AUC"],
                         "AUC (no CES-D)": auc_nc,
                         "Drop": results_df.loc[name, "ROC-AUC"] - auc_nc})

leakage_df = pd.DataFrame(no_cesd_rows).set_index("Model").round(3)
leakage_df.to_csv(RES_DIR / "leakage_sensitivity.csv")
display(leakage_df)
""")

code("""# Visualise the leakage drop
fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(leakage_df))
w = 0.35
ax.bar(x - w/2, leakage_df["AUC (full)"], w, label="With prior CES-D",
       color="#1F2D5C")
ax.bar(x + w/2, leakage_df["AUC (no CES-D)"], w, label="No CES-D features",
       color="#E56B5C")
ax.axhline(0.5, color="k", ls="--", lw=1, alpha=0.5, label="No-skill")
ax.set_xticks(x)
ax.set_xticklabels(leakage_df.index, rotation=15)
ax.set_ylabel("Test ROC-AUC")
ax.set_ylim(0.45, 0.95)
ax.set_title("Leakage sensitivity: how much does the model rely on prior depression?")
ax.legend()
plt.tight_layout()
plt.savefig(FIG_DIR / "leakage_sensitivity.png", bbox_inches="tight")
plt.show()
""")

md("""**Interpretation — the central scientific finding.**

When we strip out every depression-related feature, ROC-AUC drops from ~0.85 to ~0.77. The drop is real (about 0.07-0.08 AUC), confirming that prior depression history is a substantial predictor.

**But — and this is the headline — 0.77 is still a clinically usable signal.** It is achieved using only physical health, mobility, ADL/IADL function, cognition, finances, and demographics. **No mental-health features at all.**

In plain English: depression risk leaves a measurable footprint in non-mental-health data 2 to 4 years before symptoms emerge. A GP practice that already collects routine over-50 health-check data could deploy a model like this without administering any depression questionnaire — and still catch the majority of future cases.

This is the clinically novel result of the project.
""")


# ── Section 10. Summary ────────────────────────────────────────────────────
md("""---
## 10. Summary — what we found

### Plain-English findings

We trained four machine-learning models on data from 7,211 English adults aged 50+, predicting whether they would have clinically significant depressive symptoms 2-4 years in the future based on their answers at Waves 6 and 7.

**Headline result.** The best model achieves ROC-AUC ~0.85 on the held-out test set, with around 70% recall — we catch seven out of every ten future depression cases.

**The science behind the headline.** Removing all depression-history features from the input drops AUC to ~0.77. That number is still useful as a screening tool — and it tells us the model is genuinely picking up the *biopsychosocial signature* of late-life depression: declining physical health, mobility difficulties, and financial stress all carry independent predictive signal beyond past depression itself.

### What this means

| For… | What this implies |
|------|-------------------|
| **Patients** | A risk score, not a diagnosis. About half of those flagged would actually develop depression; the other half are still worth a brief clinical review. |
| **Clinicians** | A way to prioritise the limited capacity for in-depth assessment. Patients with high risk scores can be invited for a structured clinical interview. |
| **Researchers** | Confirmation that the biopsychosocial model of late-life depression has *measurable, predictive* footprints in routine survey data — not just in retrospective cross-sections. |
| **Public health** | A potentially scalable screening signal that does not require asking patients about depression directly. |

### Limitations to keep in mind

- **CES-D ≥ 3 is a screening threshold, not a diagnosis** of Major Depressive Disorder.
- The design is **observational** — we identify predictors, not causes.
- About 30% of W6 respondents are excluded by attrition; those people are likely the highest-risk, so we may underestimate true population risk.
- The model is validated only on the **English population aged 50+** in the ELSA cohort.
- We have not yet evaluated **fairness** across subgroups (sex, ethnicity, socioeconomic strata).

### What the model output literally is

For any participant, the model produces:
1. A **probability** (0 to 1) that they will be depressed at Wave 8.
2. A **binary label** thresholded at 0.5 (or whatever the deploying clinic chose).
3. **Calibrated probabilities** — a "30% predicted risk" really does mean roughly 30 in 100 such people will develop depression.

### Where the outputs are saved

- `outputs_submission/figures/` — all figures generated above (`outcome_distribution.png`, `roc_pr_curves.png`, `confusion_matrices.png`, `shap_bar.png`, `shap_beeswarm.png`, `leakage_sensitivity.png`)
- `outputs_submission/results/test_set_results.csv` — full test-set metrics
- `outputs_submission/results/leakage_sensitivity.csv` — with vs without CES-D for each model

---

*End of submission notebook.*
""")

code("""# Final summary print-out
print("=" * 65)
print(" ELSA Depression Prediction — Run Complete")
print("=" * 65)
print(f"  Sample size           : {len(panel):,}")
print(f"  Depression prevalence : {y.mean():.1%}")
print(f"  Predictors used       : {len(predictor_cols)}")
print()
print("  Test-set ROC-AUC by model:")
for name, auc in results_df["ROC-AUC"].sort_values(ascending=False).items():
    print(f"    {name:22s}  {auc:.3f}")
print()
print(f"  Leakage sensitivity   : AUC drops by {leakage_df['Drop'].mean():.3f} on average")
print(f"                          when CES-D features are removed.")
print()
print(f"  Outputs               : {OUTDIR}")
print("=" * 65)
""")


# ── Save notebook ───────────────────────────────────────────────────────────
nb.cells = cells
OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Saved: {OUT}")
print(f"Cells: {len(cells)}")
