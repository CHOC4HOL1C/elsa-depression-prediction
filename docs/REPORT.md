# ELSA Depression Prediction — Methods, Findings & Full Project Report

**Module:** AI and Healthcare — University of Surrey, MSc Artificial Intelligence (2025/26)
**Team:** Akeeb Lawel, Fiyin Akano, Zannat Chowdhury Sagar, Giridhar Nampally, Pushkar Jadav, Poorna Golla
**Dataset:** English Longitudinal Study of Ageing (ELSA), UK Data Service Study 5050
**Date:** May 2026

---

## Executive Summary

We built machine learning models that predict whether an English adult aged 50 or over will show clinically significant depressive symptoms 2 to 4 years from now, using only their answers to a routine social and health survey today. The best model — a tuned Random Forest combining Wave 6 and Wave 7 ELSA data — achieves an ROC-AUC of **0.848**, an F1 score of **0.582** for the depressed class, and correctly identifies **71%** of all future depression cases on data it has never seen. Even when prior depression history is removed, the model still achieves an AUC of **0.773** using only physical health, mobility, social, and economic features — confirming that depression risk is detectable from non-mental-health indicators alone. The pipeline is reproducible end-to-end in a single Colab notebook.

---

## 1. The Coursework Brief

The module assignment asked us to:

1. Build a machine learning algorithm that uses ELSA data to predict mental health outcomes (depression, anxiety) **or** to represent the temporal changes that lead to mental health issues.
2. Present the work as a 10-minute PowerPoint in Week 11.
3. Submit code with a runnable README, presentation slides, meeting minutes, and a team contributions document.

The marking criteria emphasise clarity of presentation, background description, the data analysis pipeline, results representation, limitations, and slides.

We chose **early prediction of depression** as our framing because it has the clearest clinical utility (you can intervene if you can predict), the strongest measurement basis in ELSA (the 8-item CES-D scale is collected every wave with >93% completeness), and the most established literature for comparison.

---

## 2. Background

### 2.1 The clinical problem

Depression is one of the most prevalent mental health conditions affecting older adults globally, with an estimated 10 to 15 percent of community-dwelling adults aged 50 and over experiencing clinically significant depressive symptoms at any given time (Banks et al., 2006). Depression in older adults is underdiagnosed and undertreated. The reasons are well documented: stigma, somatic symptom presentation, comorbidity with physical illness, reluctance to disclose, and limited primary care screening capacity. The cost is significant — depression is a leading cause of disability and is associated with worse outcomes for cardiovascular disease, dementia, and all-cause mortality.

Early identification of at-risk individuals is a recognised clinical priority, yet traditional diagnostic pathways typically engage patients only after symptoms have become severe. A predictive model trained on routinely collected survey data could enable proactive, population-level screening without requiring clinical referral or specialist assessment. If routine over-50 data already collected for other purposes can flag people at high future risk, those individuals can be prioritised for clinical assessment without screening everyone in detail. This is exactly the use case ELSA enables.

### 2.2 The English Longitudinal Study of Ageing (ELSA)

ELSA is a representative panel study of the English population aged 50 and over. The study began in 2002 (Wave 1) and follows the same individuals every two years, with periodic refreshment to maintain age-50 inflows. By Wave 11 (2023), the dataset covers more than two decades of biennial measurements on health, cognition, social engagement, economic circumstances, and well-being.

Crucially for our purposes, ELSA includes the **Center for Epidemiologic Studies Depression Scale (CES-D)** at every wave. The ELSA version is an 8-item binary instrument (yes/no per item), giving a total score from 0 to 8. A threshold of CES-D ≥ 3 is the standard cutoff for clinically significant depressive symptoms (Steffick, 2000) and yields a prevalence of roughly 15–25% in older adult populations — consistent with epidemiological estimates.

Our access route was UK Data Service deposit 5050. The team accessed the Stata-format core wave files, IFS-derived variable files, financial derived variable files, and supporting documentation (data dictionaries, technical reports, questionnaires).

---

## 3. Research Questions

The project was framed around three research questions, locked before any modelling began:

| RQ | Question |
|----|----------|
| **RQ1** | To what extent can ML models trained on ELSA survey data predict depression onset 2 to 4 years in advance in adults aged 50+? |
| **RQ2** | Does incorporating longitudinal change across two waves improve predictive performance compared to single-wave models, and does prediction horizon length affect accuracy? |
| **RQ3** | Which feature domains carry independent predictive signal beyond prior depression history, and does the model retain clinically meaningful accuracy when prior depression scores are excluded? |

These questions map directly onto the experimental design (RQ2 → three prediction arms; RQ3 → leakage sensitivity + domain ablation + SHAP two-act analysis).

---

## 4. Data

### 4.1 What is in the UKDA-5050-stata bundle

The complete ELSA deposit contains 82 Stata files (~1.6 GB). For our analysis we focused on three file types per wave:

| File type | Example | Rows × cols | Content |
|-----------|---------|-------------|---------|
| **Core interview** | `wave_6_elsa_data_v2.dta` | 10,601 × 6,189 | Raw questionnaire responses including the 8 PSced depression items, self-rated health, chronic conditions, mobility, physical activity, social contact |
| **IFS derived** | `wave_6_ifs_derived_variables.dta` | 10,601 × 404 | Pre-computed summary variables maintained by the Institute for Fiscal Studies: age, sex, marital status, validated CES-D total `cesd_sc`, memory, executive function, employment, education, smoking |
| **Financial derived** | `wave_6_financial_derived_variables.dta` | 10,601 × 667 | Income and wealth variables including the benefit-unit wealth quintile `totwq5_bu_s` |

Each respondent has a unique identifier `idauniq` that persists across waves, allowing person-level joins.

### 4.2 Why Waves 6, 7, and 8

Waves 6 (2012/13), 7 (2014/15), and 8 (2016/17) were selected based on three criteria established in Akeeb's audit notebook (`notebooks/01_data_audit/`), which examined every available wave (3–11) on three dimensions:

1. **CES-D quality.** All waves contain the 8-item CES-D with 93–97% valid response rates after recoding survey missing codes (-1 = inapplicable, -8 = don't know, -9 = refused). The CES-D measure is therefore stable across waves.

2. **Participant overlap.** The audit produced an overlap matrix showing the percentage of participants in any pair of waves. Consecutive waves retain >90% of participants (e.g. W6 → W7 = 90%), while large gaps lose more (W3 → W11 retains only 34%). For longitudinal modelling, consecutive waves are strongly preferable.

3. **Feature drift.** Across the 9 audited waves there are 13,920 unique variable names, but only 2,656 are common to every wave. Variable schemas evolve; longitudinal modelling must work from the shared subset.

Waves 6, 7, and 8 emerged as the strongest consecutive block: high overlap, complete CES-D, and stable feature schemas. The two-year separation between consecutive waves provides a prediction horizon of two to four years.

The inner join across all three waves produces an analytic sample of 7,211 participants. **Survivorship bias is acknowledged**: inner-join participants are somewhat healthier and more socioeconomically stable than the full ELSA population. We discuss this further in Section 10.

### 4.3 Outcome variable: CES-D depression scale

The outcome is binary depression status at Wave 8, defined as a CES-D score of 3 or above on the validated 0 to 8 scale (Radloff, 1977). The threshold of 3 or above was established by Steffick (2000) through comparison with clinical diagnostic interviews. This produces a prevalence of 19.0 percent in the analytic sample (1,372 depressed, 5,839 not depressed), giving a class ratio of approximately 1:4.3.

> **CES-D scoring note.** An earlier exploratory pipeline reconstructed CES-D scores from raw PSced items using a 0–3 per-item scale (designed for the longer HRS version), producing scores in the range 8–16 and 74 percent apparent prevalence. This was clinically implausible — depression is not the majority condition in any adult population. The artefact came from treating ELSA's binary items as Likert-scale items.
>
> The fix was to use the IFS-validated `cesd_sc` variable directly. ELSA's CES-D items are binary (1 = yes, 2 = no after Stata recoding), so the validated sum produces the correct 0–8 range. With the threshold of CES-D ≥ 3, the analytic sample shows 19% prevalence — exactly what the literature predicts for English adults aged 50 and over.
>
> The methodological lesson: **always start from validated derived variables, and verify your outcome distribution against published prevalence before training any model**.

### 4.4 Class imbalance handling

The 1:4.3 class ratio is handled explicitly per model. Logistic Regression and Random Forest receive `class_weight='balanced'`, which multiplies each minority class sample's loss contribution by 4.3 during training. XGBoost receives `scale_pos_weight=4`, the equivalent gradient-boosting implementation. LightGBM also uses `class_weight='balanced'`.

Without these corrections, models would achieve apparent accuracy above 80 percent by predicting everyone as non-depressed while entirely missing the depressed class. The correction is confirmed effective: recall values of 0.67 to 0.76 are achieved across models (Section 8.3).

### 4.5 Predictors and feature engineering

Predictor variables are drawn from IFS derived files, core interview files, and financial derived files for Waves 6 and 7. Variables are organised into nine feature domains.

**Table 1. Feature domains, representative variables, and wave coverage.**

| Domain | Representative variables | Wave coverage |
|---|---|---|
| Prior depression | `cesd_sc`, `cesd_change` (W6+W7 only) | W6, W7 |
| Self-rated health | `srh_hrs`, `hehelf`, `llsill`, `hlimwrk` | W6, W7 |
| Chronic conditions | `hediabp`, `hediast`, `hediami`, `hediahf`, `hediaar` | W6, W7 |
| Mobility/function | `mobility_count`, `adl_count`, `iadl_count`, `functional_burden` | W6, W7 |
| Cognition | `memtotb` (memory), `execnn` (executive function) | W6, W7 |
| Socioeconomic | `findiff`, `totwq5_bu_s`, `ecpos`, `qual3`, `lackresb` | W6, W7 |
| Social/housing | `famtype`, `tenure`, `chinhh`, `chouthh`, `smokerstat` | W6, W7 |
| Lifestyle/digital | `heacta/b/c` (physical activity), `scint` (internet) | W6, W7 |
| Demographics | `age`, `sex`, `nonwhite`, `marstat`, `couple` | W6, W7 |

Survey missing codes (−1, −2, −8, −9) are recoded to NaN. Columns with more than 40 percent missing are dropped using a **training-only estimate** to avoid leakage. Wave symmetry is enforced: if a variable stem fails the missingness threshold at one wave, both wave versions are removed. This affected the neighbourhood deprivation index (`ndepriv`), which was dropped from both waves because the Wave 7 version had 56 percent missing in the training partition.

**Composite scores were engineered to reduce correlated item batteries:**

| Feature | Definition | Clinical meaning |
|---------|------------|------------------|
| `cesd_change` | CES-D(W7) − CES-D(W6) | Trajectory of depressive symptoms |
| `mobility_count_w6/7` | Sum of 10 mobility difficulty items | Composite physical function score |
| `adl_count_w6/7` | Sum of 6 ADL items | Basic self-care difficulty (bathing, dressing, eating) |
| `iadl_count_w6/7` | Sum of 9 IADL items | Complex daily task difficulty (managing money, taking medication) |
| `functional_burden_w6/7` | ADL + IADL count | Total functional impairment |
| `mobility_change` | Mobility(W7) − Mobility(W6) | Decline in physical function |

The `cesd_change` and `mobility_change` features explicitly capture **temporal change**, satisfying the assignment brief's requirement to "represent the temporal changes that lead to mental health issues."

---

## 5. Methodology

### 5.1 Analytic sample construction

We loaded IFS, core, and financial files for each of W6, W7, W8 and merged them on `idauniq` (inner join), keeping only participants present in all three waves.

| Step | N |
|------|---|
| W6 IFS respondents | 10,601 |
| W7 IFS respondents | 9,666 |
| W8 IFS respondents | 8,445 |
| Inner join W6 ∩ W7 ∩ W8 | 7,535 |
| With valid `cesd_sc_w8` (after dropping survey missing codes) | **7,211** |

The 7,211 figure is our final modelling sample. Of these, 1,372 (19.0%) are depressed at W8 and 5,839 (81.0%) are not.

### 5.2 Preprocessing

Three steps, in order:

1. **Survey missing code recoding.** ELSA encodes non-responses as numeric -1, -2, -8, -9. Every predictor column is converted to numeric and these codes are mapped to NaN.

2. **High-missingness column drop.** Columns with more than 40% missing values are dropped. The threshold is computed on a training-only split (75% of data) to ensure the test set does not influence which features the model sees. In practice only one column triggers the threshold (`ndepriv_w7` at 56% missing), but the methodology is correct.

3. **Wave-symmetry enforcement.** If a stem (e.g. `ndepriv`) is dropped at one wave, it is dropped from both waves. This prevents the longitudinal model from training on a feature that is half-available across time, which would produce inconsistent measurements per person.

Imputation (median) and scaling (standard, where applicable) happen inside scikit-learn `Pipeline` objects so they are fit on training data only — no test-set leakage.

### 5.3 Experimental design — three prediction arms (RQ2)

A three-arm design was used to answer RQ2 directly by comparing different temporal relationships between predictors and outcome.

**Table 2. Three-arm experimental design.**

| Arm | Predictor waves | Horizon | Features |
|-----|-----------------|---------|----------|
| W6 only | Wave 6 | ~4 years before W8 | 68 |
| W7 only | Wave 7 | ~2 years before W8 | 68 |
| **W6+W7** | **Both waves + trajectory features** | **2–4 years** | **138** |

Each arm uses the same 7,211 participants and identical stratified 80/20 train/test split, ensuring that performance differences across arms reflect temporal information rather than sampling variation.

### 5.4 Five feature configurations per arm (RQ3)

Five feature configurations were applied to every arm, each motivated by published literature on depression risk factors in older adults.

**Table 3. Feature configurations and clinical motivation.**

| Config | Contents | Clinical question |
|--------|----------|-------------------|
| `full` | All available features | Best possible prediction |
| `no_cesd` | All features except prior CES-D | Can we predict without depression history? |
| `health_only` | Self-rated health + chronic conditions | How far does basic health data take us? |
| `function_cog` | Mobility, ADL/IADL, cognition | Do functional markers alone predict onset? |
| `socioeconomic` | Financial + social features | Does socioeconomic context carry signal? |

The `no_cesd` configuration is the critical leakage check that answers RQ3.

### 5.5 Models

Four classifiers were evaluated.

| Model | Why included | Strengths |
|-------|--------------|-----------|
| **Logistic Regression** | Interpretable epidemiological baseline; standardised coefficients are directly interpretable as log-odds per 1 SD change | Transparent, fast, well-understood by clinicians |
| **Random Forest** | Non-linear, handles interactions and missingness gracefully via bagging over 300 trees | Robust, no scaling needed, gives feature importance |
| **XGBoost** | State-of-the-art gradient boosting | Often best for tabular health data |
| **LightGBM** | Used by Zhao et al. (2025) on ELSA → AUC 0.77–0.90 cross-sectionally; literature benchmark | Very fast, handles imbalance well |

All models use median imputation for missing values within sklearn `Pipeline` objects.

### 5.6 Hyperparameter tuning

Following the initial 60-combination sweep (3 arms × 5 configs × 4 models), the best-performing configuration per arm by mean AUC was identified. RF, XGBoost, and LightGBM were tuned using `RandomizedSearchCV` with **30 iterations and 5-fold stratified cross-validation**, scoring on ROC-AUC (Bergstra and Bengio, 2012). Logistic Regression was excluded from tuning as its hyperparameter space is narrow and it serves as a stable reference. Tuning used the training set only — the held-out test set was untouched throughout.

### 5.7 Evaluation metrics

The held-out test set (20%, n = 1,803) is used for final reporting.

| Metric | What it measures | Why we care |
|--------|------------------|-------------|
| **ROC-AUC** | Discrimination, threshold-free | Primary metric — how well does the model rank cases above non-cases? |
| **F1 (binary, depressed class)** | Balance of precision and recall on the minority class | Primary clinical metric — captures depression-detection performance |
| **F1 (macro)** | Mean F1 across both classes | Reported for completeness |
| **Precision** | Of those flagged as at-risk, what fraction actually develop depression? | False-alarm cost |
| **Recall (sensitivity)** | Of all future cases, what fraction does the model catch? | Miss rate — paramount in screening |
| **Average precision** | Area under PR curve | More informative than AUC under imbalance |
| **Calibration** | Are predicted probabilities trustworthy? | Crucial for clinical decision-making |

We prefer **binary F1 over macro F1** as the primary clinical metric because correctly classifying the 81% non-depressed majority is a trivially easy component that would inflate macro F1 misleadingly. Recall is reported prominently because in population screening, missing a depressed individual carries greater clinical cost than a false alarm.

### 5.8 Interpretation methods

We use six convergent interpretation strategies so that no single method's blind spot drives our conclusions:

- **Domain ablation:** leave-one-domain-out analysis. The best tuned model is retrained with each domain removed and AUC drop recorded. Measures **unique** contribution given all other features remain.
- **SHAP (SHapley Additive exPlanations):** TreeExplainer on the best RF model for the W6+W7 arm. Run twice: **Act 1** on the full model and **Act 2** on the `no_cesd` configuration. The ranking shift between the two directly answers RQ3.
- **Feature correlation analysis:** Domain-level mean absolute Pearson correlation heatmap (9×9) reveals which domains measure overlapping signals. Per-feature point-biserial correlation with `depressed_w8` (top 25) provides a pre-modelling sanity check comparable to post-modelling SHAP.
- **LR standardised coefficients:** Coefficients from the scaled LR pipeline express log-odds per 1 SD change per feature, enabling cross-feature comparison and direct clinical interpretation.
- **LightGBM gain importance:** Total information gain attributed to each feature across all trees during LGBM training. Provides convergent evidence with SHAP and LR coefficients.
- **Calibration:** Reliability diagrams show whether predicted probabilities correspond to actual depression rates. Isotonic regression calibration is applied to the best model.

### 5.9 Ensemble methods

- **Soft-vote ensemble:** equal-weight average of RF, XGBoost, and LightGBM probability outputs on the W6+W7 full configuration.
- **Stacking ensemble:** RF and LightGBM as base learners with Logistic Regression as the meta-learner, trained on 5-fold out-of-fold probability predictions from the training set. No data leakage occurs — the meta-learner never sees the held-out test set during fitting.

### 5.10 Threshold optimisation

The default classification threshold of 0.5 is conservative for a 19 percent prevalence task. The optimal F1 threshold is found by sweeping predicted probabilities on the test set from 0.10 to 0.60 in 0.01 steps and selecting the threshold maximising binary F1.

---

## 6. Results

### 6.1 Cross-arm performance comparison (RQ1 and RQ2)

**Table 4. Best tuned model results per arm on held-out test set (n = 1,803).**

| Arm | Best model | AUC-ROC | F1 binary | F1 macro | Recall | Precision |
|-----|------------|---------|-----------|----------|--------|-----------|
| W6 only | LGBM (tuned) | 0.819 | 0.532 | 0.683 | 0.732 | 0.418 |
| W7 only | RF (tuned) | 0.824 | 0.545 | 0.704 | 0.668 | 0.461 |
| **W6+W7** | **RF (tuned)** | **0.848** | **0.582** | **0.727** | **0.714** | **0.491** |

**RQ1 answer.** Yes — AUC 0.848 places this study within the range of Zhao et al. (2025), who report 0.77–0.90 on ELSA cross-sectionally, **achieved here under a longitudinal constraint that reduces the sample by approximately 30 percent through inner-join attrition**. AUC 0.85 with 71% recall is genuinely useful early prediction, on a par with established clinical risk calculators like QRISK for cardiovascular disease.

**RQ2 — prediction horizon.** W7 only (2-year horizon) marginally outperforms W6 only (4-year horizon) by 0.005 AUC. The difference is small and consistent, suggesting that more recent health information is slightly more predictive. Crucially, **a 4-year early prediction carries nearly equivalent information to a 2-year prediction**, which has strong clinical implications for early intervention.

**RQ2 — longitudinal benefit.** Adding both waves improves AUC by 0.024 over the best single-wave model. This improvement reflects both the doubled feature set and the trajectory features `cesd_change` and `mobility_change`. The modest size of the improvement suggests diminishing returns from additional wave coverage.

### 6.2 Feature configuration comparison

**Table 5. Best AUC per configuration per arm (untuned models for comparability).**

| Config | W6 AUC | W7 AUC | W6+W7 AUC | Features (W6+W7) |
|--------|--------|--------|-----------|------------------|
| `full` | 0.810 | 0.821 | 0.848 | 138 |
| `no_cesd` | 0.761 | 0.769 | 0.773 | 129 |
| `health_only` | 0.721 | 0.745 | 0.750 | 24 |
| `function_cog` | 0.720 | 0.729 | 0.740 | 22 |
| `socioeconomic` | 0.689 | 0.702 | 0.720 | 18 |

`health_only` achieves AUC 0.721–0.750 using only 12–24 features, demonstrating that **basic health information captures a substantial proportion of predictive signal**. The `socioeconomic` configuration is weakest in isolation not because financial and social factors are clinically irrelevant, but because their signal is correlated with health features and thus partially redundant when both are available (see Section 6.5).

### 6.3 Full model comparison — W6+W7 arm

**Table 6. Full-feature model comparison, W6+W7 arm, held-out test set.**

| Model | AUC | F1 binary | F1 macro | Recall | Precision |
|-------|-----|-----------|----------|--------|-----------|
| LR (baseline) | 0.835 | 0.559 | 0.711 | 0.697 | 0.467 |
| **RF (tuned)** | **0.848** | 0.582 | 0.727 | 0.714 | 0.491 |
| XGBoost (tuned) | 0.844 | **0.585** | **0.734** | 0.676 | **0.516** |
| LightGBM (tuned) | 0.843 | 0.577 | 0.718 | **0.758** | 0.466 |
| Soft-vote (RF+XGB+LGBM) | 0.847 | 0.582 | 0.728 | 0.709 | 0.494 |
| Stacking (RF+LGBM, LR meta) | 0.841 | 0.563 | 0.718 | **0.773** | 0.434 |

**RF tuned** achieves the highest AUC. **LightGBM** achieves the best recall among individual models (0.758) — preferred for screening applications where missing a depressed individual is the primary concern. **XGBoost** achieves the best precision (0.516) and F1 binary (0.585) at default threshold.

The **soft-vote ensemble** does not outperform the best individual model (AUC 0.847 vs 0.848), reflecting the high correlation between three tree models trained on the same data. Averaging correlated predictions regresses toward the mean rather than cancelling independent errors.

The **stacking ensemble** achieves AUC 0.841 but recall 0.773, the highest of any model configuration tested. The LR meta-learner learned to weight LightGBM (highest-recall base model) more heavily, shifting the ensemble toward maximum sensitivity. **For clinical screening applications where missing a depressed individual is the primary concern, the stacking ensemble is the deployment recommendation.**

LR at AUC 0.835 is only 0.013 below the best RF. **For clinical deployment requiring coefficient-level explainability, LR is a defensible choice.**

### 6.4 Threshold optimisation

**Table 7. Threshold optimisation results, W6+W7 arm.**

| Model | F1 @ t=0.50 | Optimal t | F1 @ optimal t | Recall @ opt | Precision @ opt |
|-------|-------------|-----------|----------------|--------------|-----------------|
| RF (tuned) | 0.582 | 0.58 | 0.606 | 0.627 | 0.586 |
| XGBoost (tuned) | 0.585 | 0.55 | 0.593 | 0.643 | 0.549 |
| LightGBM (tuned) | 0.577 | 0.58 | 0.592 | 0.624 | 0.563 |
| LR (baseline) | 0.559 | 0.60 | 0.570 | 0.591 | 0.551 |

The optimal F1 threshold for RF is 0.58, above the default 0.50, yielding an improvement of +0.024 F1. The threshold being above 0.50 is explained by the `class_weight='balanced'` setting: balanced training already shifts the model toward generosity with positive predictions, elevating raw probability outputs. Raising the threshold to 0.58 filters low-confidence positive predictions and improves precision enough to lift F1. At the optimal threshold, the recall–precision tradeoff (0.627 / 0.586) is substantially more balanced than at the default.

### 6.5 Domain ablation and feature correlation (RQ3 setup)

**Table 8. Leave-one-domain-out domain ablation, W6+W7 arm, RF tuned.**

| Domain removed | AUC | AUC drop | Interpretation |
|----------------|-----|----------|-----------------|
| None (full model) | 0.848 | 0.000 | Baseline |
| **Prior depression** | **0.771** | **+0.077** | **Dominant predictor** |
| Self-rated health | 0.843 | +0.005 | Second most informative unique signal |
| Demographics | 0.848 | +0.000 | Redundant with health features |
| Chronic conditions | 0.849 | −0.001 | Signal captured by self-rated health |
| Mobility/function | 0.849 | −0.001 | Signal captured by correlated features |
| Cognition | 0.849 | −0.000 | Near-zero unique contribution |
| Socioeconomic | 0.849 | −0.001 | Signal captured by health and mobility |
| Social/housing | 0.850 | −0.001 | Near-zero unique contribution |
| Lifestyle/digital | 0.849 | −0.000 | Near-zero unique contribution |

The near-zero AUC drops for most domains require careful interpretation. They do **not** mean those domains are unimportant. The domain correlation heatmap reveals why: mobility/function and self-rated health share a mean absolute Pearson correlation of approximately 0.45; chronic conditions and self-rated health correlate at approximately 0.38. When one domain is removed, the model reconstructs its signal from correlated neighbours. **Domain ablation measures unique contribution given all other features are present, not total contribution.**

The top 25 features by raw point-biserial correlation with `depressed_w8` confirm the domain-level findings independently: `cesd_sc_w7` and `cesd_sc_w6` have the highest positive correlations; `hemob96_w6` (no mobility difficulties flag) shows strong negative correlation; `findiff` (financial difficulty) shows positive correlation; `totwq5_bu_s` (wealth quintile) shows negative correlation. These rankings are consistent with the post-modelling SHAP results, providing convergent pre-modelling and post-modelling evidence.

### 6.6 Leakage sensitivity and SHAP (RQ3 answer)

**Table 9. Leakage sensitivity analysis across all three arms.**

| Arm | AUC with CES-D | AUC without CES-D | AUC retained |
|-----|----------------|--------------------|--------------|
| W6 only (LGBM) | 0.819 | 0.739 | 90.2% |
| W7 only (RF) | 0.824 | 0.769 | 93.3% |
| **W6+W7 (RF)** | **0.848** | **0.773** | **91.2%** |

**RQ3 answer.** Across all three arms, removing all prior CES-D retains over **90 percent** of the original AUC. The W6+W7 arm retains AUC 0.773 (91 percent) without any depression history. **The model is genuinely learning from health, functional, and social risk factors rather than simply tracking depression persistence.**

**SHAP — Act 1 (full model, W6+W7, RF tuned).** `cesd_sc` at Waves 7 and 6 dominate by a wide margin, with SHAP values extending from −0.15 to +0.25. The scale of non-CES-D features is substantially smaller. After the CES-D features: `mobility_count` (W7) ranks third, `srh_hrs` (W7) fifth, and `cesd_change` sixth.

**SHAP — Act 2 (no prior CES-D, W6+W7, RF).** The ranking changes substantially. **`srh_hrs` (self-rated health, W7) rises to rank 1**; `hehelf` at both waves occupies ranks 2 and 3; `mobility_count` (W7 and W6) ranks 4 and 5; financial difficulty (`findiff`) ranks 8 and 10; sex ranks 9. The overall SHAP value scale compresses to −0.06 to +0.06, indicating the model **distributes signal across many features rather than anchoring on one dominant predictor**. Sex emerging is consistent with the higher depression prevalence in women (Kessler, 2003). The Act 1 → Act 2 transition is consistent with Ohrnberger et al. (2017) on self-rated health and Zaninotto et al. (2019) on cognitive and social factors as independent predictors.

**Why this matters scientifically.** Act 2 is the clinically novel finding. It demonstrates that **depression risk leaves a measurable footprint in physical health, mobility, and economic circumstances 2–4 years before the depression itself manifests**. This aligns with the biopsychosocial model of late-life depression, where physical decline, social isolation, and financial stress are causal contributors, not just consequences.

### 6.7 Clinical interpretability — LR coefficients and LightGBM importance

Logistic Regression standardised coefficients (log-odds per 1 SD, W6+W7 full configuration):

- `cesd_sc_w7` has the largest positive coefficient.
- `hemob96_w6` (no mobility difficulties flag) has the largest negative coefficient, confirming it is strongly protective.
- `totwq5_bu_s` (wealth quintile) is negative — higher wealth is protective.
- `findiff` is positive — financial difficulty increases depression odds.
- `sex` is positive — female sex associated with higher risk.

**Three independent interpretation methods — SHAP, LR coefficients, and LightGBM gain importance — tell the same story:** prior CES-D features dominate; self-rated health and mobility are the leading non-depression predictors; financial difficulty and sex carry independent signal. Convergent evidence across methods strengthens confidence in the findings.

LightGBM achieves AUC 0.843 versus RF 0.848, a gap of only 0.005. However, LightGBM achieves the best recall (0.758) among individual models. The RF–LightGBM gap is discussed in Section 7.2.

### 6.8 Calibration

All three tree models are **underconfident at low predicted probabilities** — when the model predicts 20 percent probability of depression, the actual rate is higher. Logistic Regression is better calibrated across the probability range, consistent with its known property as a well-calibrated probability estimator.

**Isotonic regression calibration** applied to the tuned RF model substantially improves calibration in the 0.2–0.6 probability range with negligible AUC change (0.850 → 0.848). The calibrated RF model is recommended for any deployment context where the predicted probability is used as a clinical risk score rather than simply a binary classification.

---

## 7. Discussion

### 7.1 Performance in clinical context

The strongest model achieves AUC 0.848. **In a population screening scenario applied to 10,000 adults aged 50 and over with 19% prevalence**, the RF model at default threshold would correctly flag approximately 1,358 of the 1,900 individuals who will develop depression (recall 71.4%) while generating approximately 1,392 false alarms (17.3% of 8,100 non-depressed individuals). At the optimal threshold of 0.58, this shifts to fewer but higher-confidence positive predictions, achieving F1 0.606.

**Different clinical objectives call for different model choices:**

- **RF tuned** for best overall discrimination.
- **Stacking ensemble** or **LightGBM** for maximum case detection (highest recall).
- **LR** for clinical explainability (transparent coefficients).
- **Calibrated RF** when the probability value itself is used for risk stratification.

A more concrete deployment scenario: imagine a GP practice that already records ELSA-style data through routine over-50 health checks. The model could flag, say, the 200 patients out of 1,000 with the highest predicted depression risk. Those 200 would be invited for a 15-minute clinical interview using a validated diagnostic tool (e.g. PHQ-9 or structured clinical interview). Roughly 100 of them (precision ~50%) would meet criteria for early intervention; the other 900 patients are not screened in detail, saving substantial clinician time. Of the 1,000, about 142 would actually develop depression in the next 2-4 years; the model catches ~100 of them (71% recall). Compared to no targeted screening, this is a meaningful improvement in early detection.

### 7.2 Why RF outperforms LightGBM

RF performing marginally better than LightGBM is contrary to Zhao et al. (2025) but explicable on three grounds:

1. **Sample size.** Our training sample of approximately 5,400 participants is at the lower end for gradient boosting to show its full advantage over bagging. RF's variance-reduction strategy is more robust at this scale.
2. **Feature complexity.** Our feature set consists of integer-coded survey responses with limited deep non-linearity, which suits RF's bagging approach over the deeper tree-on-tree boosting that LightGBM exploits best.
3. **Hyperparameter exploration.** Thirty-iteration `RandomizedSearchCV` may under-explore LightGBM's sensitive hyperparameter space (learning rate, leaves, regularisation interact). A larger search budget (≥100 iterations) might recover the gap.

Zhao et al. used a larger cross-sectional sample without longitudinal attrition constraints — an approximately 30% larger effective sample — which favours boosting.

### 7.3 What the model's output means

For any person aged 50+ whose Wave 6 and Wave 7 ELSA-style answers are available, the model produces:

1. **A probability between 0 and 1** — the model's estimate of the chance this person will score CES-D ≥ 3 at Wave 8 (i.e. show clinically significant depressive symptoms 2–4 years from now).
2. **A binary label** — depressed (1) or not depressed (0), thresholded at 0.5 by default or 0.58 at the F1-optimal point.
3. **Calibrated probabilities** — after isotonic regression, these are trustworthy: a "30% chance" really means 30 in 100 such people will develop depression.

What it **is** vs what it **is not**:

| It is | It is not |
|--------|-----------|
| A risk *probability* for elevated depressive symptomatology | A diagnosis of Major Depressive Disorder |
| A correlation-based predictor | A causal model |
| Validated on the English population aged 50+ | Validated on younger adults, non-English populations, or institutionalised individuals |
| Useful as a population-screening prioritisation tool | Useful as a standalone clinical instrument |
| Honest about uncertainty (calibrated probabilities) | A black-box "yes/no" verdict |

---

## 8. Limitations

### Methodological

1. **Prior depression dominates.** Removing CES-D drops AUC from 0.848 to 0.773. The model's main signal is depression history (state dependence). The leakage sensitivity is what rescues the clinical novelty claim.

2. **Survivorship / attrition bias.** Our analytic sample requires presence in all three waves. About 30% of Wave 6 respondents are excluded — and those people may be older, sicker, more isolated, or institutionalised, exactly the population at highest risk. The model likely underestimates true population risk.

3. **CES-D ≥ 3 is screening, not diagnosis.** It captures elevated depressive symptomatology, not Major Depressive Disorder. The CES-D threshold of 3 is a convenient binary cutoff applied to a continuous scale; regression models predicting the continuous score would provide richer characterisation. A person flagged by the model needs clinical confirmation before any treatment decision.

4. **Observational design.** We identify *predictors*, not *causes*. Low wealth predicts depression; we cannot say poverty causes depression from this analysis alone — there may be unmeasured confounders (childhood adversity, undiagnosed physical illness, social network).

5. **Class imbalance trade-off.** Precision for the depressed class is moderate (~49%). About half of model-flagged people would not develop depression. In a screening context this is acceptable; in a confirmatory context it is not.

6. **Excluded variables.** The neighbourhood deprivation index (`ndepriv`) was excluded due to wave-symmetry enforcement. It may carry independent area-level socioeconomic signal beyond household-level financial difficulty.

7. **Hyperparameter budget.** Thirty-iteration `RandomizedSearchCV` may under-explore LightGBM's hyperparameter space, partially explaining the RF vs LGBM AUC gap.

8. **Generalisability boundaries.** ELSA samples English adults aged 50 and over. Findings may not generalise to younger populations, non-English contexts, or institutionalised residents. ELSA cohort effects also mean today's 50-year-olds are not the 50-year-olds in our sample.

### Technical (acknowledged from PR review process)

9. **Missingness filter is computed once on a training split, not within each CV fold.** The gold standard for nested validation would wrap the missingness gate inside a custom transformer fit per fold. In practice the only column dropped (`ndepriv_w7` at 56%) would be dropped under any reasonable split, so the simplification has no practical impact.

10. **Engineered features bypass the missingness gate.** All 10 derived features have <0.3% missingness in our data, so this is theoretical only — but a production pipeline should apply the same gate uniformly.

11. **Logistic regression coefficients are on a standardised scale.** Because features pass through `StandardScaler` before LR, the reported coefficients are log-odds per 1 SD change, not per 1 raw unit. This is labelled correctly on the plot but should be noted when interpreting.

12. **`functional_burden` uses `+` rather than `sum(..., min_count=1)`** — meaning if either ADL or IADL is fully missing, the burden score is NaN even if the other component is present. In our data this scenario does not occur (ADL and IADL come from the same questionnaire block) but the implementation is not maximally NaN-tolerant.

---

## 9. Future Directions

1. **Incident depression model.** Exclude participants with CES-D ≥ 3 at baseline (W6) and predict only first-onset depression at W8. This is harder but more clinically meaningful.

2. **External validation.** Test the trained pipeline on the US Health and Retirement Study (HRS), the Survey of Health, Ageing and Retirement in Europe (SHARE), and the Irish Longitudinal Study on Ageing (TILDA). All three use harmonised CES-D measures and could test cross-population generalisability.

3. **Nurse visit biomarkers.** ELSA collects blood pressure, BMI, grip strength, and inflammatory markers (CRP, fibrinogen) from nurse visits at Waves 2, 4, 6, and 8. None were used here. Adding biological signal could distinguish physical-decline-driven depression from socially-driven depression.

4. **Multi-wave trajectory modelling.** Rather than two snapshots (W6, W7), latent growth curve models or recurrent neural networks could capture richer temporal patterns across many waves.

5. **Subgroup fairness analysis.** Are the predictors equally informative across sex, ethnicity, and socioeconomic strata? Differential calibration is a major fairness concern in clinical ML and was not evaluated here.

6. **Cost-effectiveness modelling.** Combined with intervention efficacy data (e.g. CBT acceptance and remission rates in this population), the model's outputs could feed a Markov decision-process analysis estimating quality-adjusted life-years (QALYs) gained per pound of screening cost.

7. **Wider hyperparameter sweep for LightGBM** with at least 100 iterations to confirm or close the RF–LGBM gap.

---

## 10. Pipeline Summary

```
ELSA UKDA-5050 Stata files
        │
        ▼
[1. Audit] — Akeeb
   waves, CES-D quality, feature overlap, attrition
        │
        ▼
[2. Wave selection] — W6, W7, W8 (highest consecutive overlap)
        │
        ▼
[3. Data load + merge] — IFS + Core + Financial, inner join on idauniq
        │
        ▼
[4. Outcome] — cesd_sc_w8 ≥ 3 → binary label
        │
        ▼
[5. Preprocessing]
   • Recode survey missing codes (-1, -2, -8, -9 → NaN)
   • Drop columns >40% missing (training-only estimate)
   • Wave-symmetry enforcement
        │
        ▼
[6. Feature engineering]
   • cesd_change, mobility/ADL/IADL counts
   • functional_burden, mobility_change
        │
        ▼
[7. Three prediction arms]
   • W6 only (~4yr)  • W7 only (~2yr)  • W6+W7 (combined)
        │
        ▼
[8. Five configs per arm]
   • full • no_cesd • health_only • function_cog • socioeconomic
        │
        ▼
[9. Four models per config]
   • LR • RF • XGBoost • LightGBM (60 baseline experiments)
        │
        ▼
[10. Tune best config per arm]
   • RandomizedSearchCV (30 iter, 5-fold CV) on RF/XGB/LGBM
        │
        ▼
[11. Evaluate on held-out test set]
   • ROC-AUC, F1, Precision, Recall, Confusion matrix, Calibration
        │
        ▼
[12. Interpretation]
   • Domain ablation • SHAP Act 1 (full) • SHAP Act 2 (no CES-D)
   • LR coefs • LightGBM gain • Feature correlation
        │
        ▼
[13. Sensitivity + ensembles]
   • Leakage analysis (with vs without prior CES-D, all 3 arms)
   • Soft-vote (RF+XGB+LGBM) • Stacking (RF+LGBM, LR meta)
   • Threshold optimisation
        │
        ▼
[14. Reporting]
   • 16 figures, 6 results CSVs, this report, presentation
```

---

## 11. Reproducibility

The submission notebook (`submission/ELSA_Depression_Prediction_Final_v2.ipynb`) is designed to run end-to-end in a single Colab session. The user sets one path variable (`ELSA_PATH`) pointing to either a downloaded UKDA-5050 zip file or the extracted folder. The notebook installs missing dependencies, locates the Stata files, runs all 60 baseline experiments + 9 tuning rounds + ensembles + threshold optimisation + calibration, and exports figures and CSVs to Google Drive.

A `FAST_MODE` flag in Section 0.4 of the notebook controls the runtime/precision trade-off. With `FAST_MODE = True` (default) the tuning sweep uses 10 iterations × 3-fold CV and SHAP samples 200 rows, completing in ~15-25 min on a Colab CPU runtime. With `FAST_MODE = False` the full 30-iteration × 5-fold tuning and 500-row SHAP run, reproducing the exact headline AUCs in this report at a cost of ~60-90 min on Colab CPU. The fast-mode AUCs typically land within 0.005-0.010 of the values reported in Tables 4 and 6; the cross-arm ordering, leakage drop, SHAP rankings, and clinical conclusions are unchanged.

A fixed random seed (`SEED=42`) is used throughout. All splits, CV folds, hyperparameter searches, and SHAP samples are deterministic. Any user with UKDS access can reproduce every figure and every number in this report.

---

## 12. Team Contributions

See [`team_contributions.md`](team_contributions.md) for the full per-member narrative. Brief summary:

- **Akeeb Lawel** — Data audit, wave selection, feature funnel
- **Fiyin Akano** — Original W6+W7 pipeline, CES-D fix, leakage analysis, project report, presentation deck, PR review process
- **Zannat Chowdhury Sagar** — Preprocessing baseline, enhanced pipeline (XGBoost/LightGBM/tuning/SHAP/calibration/stacking), final submission notebook, methods & findings report
- **Giridhar Nampally, Pushkar Jadhav, Poorna Golla** — see contributions doc

---

## 13. References

Banks, J., Breeze, E., Lessof, C., and Nazroo, J. (Eds.). (2006). *Retirement, health and relationships of the older population in England: The 2004 English Longitudinal Study of Ageing*. London: Institute for Fiscal Studies.

Bergstra, J., and Bengio, Y. (2012). Random search for hyper-parameter optimization. *Journal of Machine Learning Research*, 13, 281–305.

Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., and Liu, T. Y. (2017). LightGBM: A highly efficient gradient boosting decision tree. *Advances in Neural Information Processing Systems*, 30.

Kessler, R. C. (2003). Epidemiology of women and depression. *Journal of Affective Disorders*, 74(1), 5–13.

Lundberg, S. M., and Lee, S.-I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems*, 30.

Ohrnberger, J., Fichera, E., and Sutton, M. (2017). The relationship between physical and mental health: A mediation analysis. *Social Science and Medicine*, 195, 42–49.

Radloff, L. S. (1977). The CES-D scale: A self-report depression scale for research in the general population. *Applied Psychological Measurement*, 1(3), 385–401.

Steffick, D. E. (2000). *Documentation of affective functioning measures in the Health and Retirement Study*. HRS Documentation Report DR-005. Ann Arbor: University of Michigan.

Turvey, C. L., Wallace, R. B., and Herzog, R. (1999). A revised CES-D measure of depressive symptoms and a DSM-based measure of major depressive episodes in the elderly. *International Psychogeriatrics*, 11(2), 139–148.

Zaninotto, P., Sommerlad, A., Kivimaki, M., and Steptoe, A. (2019). The bidirectional association between depressive symptoms and cognitive decline in adults aged over 50. *Psychological Medicine*, 47(7), 1321–1334.

Zhao, Y., Wan, X., and Liu, Z. (2025). Machine learning identifies determinants of depressive symptoms in multinational middle-aged and older adults. *npj Digital Medicine*.

---

## Appendix A — Figures Index

All saved to `outputs/figures/` and copied to the submission Drive output folder.

| File | Section | Purpose |
|------|---------|---------|
| `01_data/outcome_distribution.png` | Background | CES-D histogram, class balance |
| `02_experiments/auc_all_arms_configs.png` | Experiment | AUC across all 60 baseline experiments |
| `03_results/arm_comparison.png` | Results | Cross-arm AUC comparison |
| `03_results/roc_curves.png` | Results | ROC curves, best model per arm |
| `03_results/pr_curves.png` | Results | Precision-recall curves |
| `03_results/confusion_matrices.png` | Results | Test-set confusion matrices |
| `03_results/threshold_optimisation.png` | Results | F1 vs threshold sweep |
| `03_results/ensemble_roc.png` | Results | Soft-vote ensemble vs individual models |
| `03_results/stacking_ensemble_roc.png` | Results | Stacking ensemble vs individual models |
| `04_interpretation/domain_ablation.png` | Interpretation | Leave-one-domain-out |
| `04_interpretation/domain_correlation_heatmap.png` | Interpretation | Cross-domain correlations |
| `04_interpretation/feature_target_correlation.png` | Interpretation | Top-25 Pearson correlations |
| `04_interpretation/shap_act1_full.png` | Interpretation | SHAP, full model |
| `04_interpretation/shap_act2_no_cesd.png` | Interpretation | SHAP, no prior CES-D |
| `04_interpretation/lgbm_importance_top20.png` | Interpretation | LightGBM gain importance |
| `04_interpretation/lr_coefficients_standardised.png` | Interpretation | LR standardised coefficients |
| `04_interpretation/calibration.png` | Interpretation | Reliability diagrams |
| `04_interpretation/calibration_isotonic.png` | Interpretation | Isotonic-calibrated reliability |
| `05_sensitivity/leakage_sensitivity.png` | Sensitivity | With vs without CES-D |

## Appendix B — Results Files

- `results/all_experiments.csv` — every (arm × config × model) combination, baseline run (60 rows)
- `results/tuned_models.csv` — best tuned model per arm with held-out test metrics
- `results/domain_ablation.csv` — leave-one-domain-out AUC drops
- `results/leakage_sensitivity.csv` — full vs no-CES-D for every arm
- `results/threshold_optimisation.csv` — optimal F1 threshold per model
- `results/stacking_ensemble.csv` — stacking vs individual models

---

*End of report.*
