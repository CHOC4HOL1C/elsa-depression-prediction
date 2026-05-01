# ELSA Depression Prediction — Full Project Report

**Module:** AI and Healthcare — University of Surrey, MSc Artificial Intelligence (2025/26)
**Team:** Akeeb Lawel, Fiyin Akano, Zannat Chowdhury Sagar, Giridhar Nampally, Pushkar Jadav, Poorna Golla
**Dataset:** English Longitudinal Study of Ageing (ELSA), UK Data Service Study 5050
**Date:** May 2026

---

## Executive Summary

We built machine learning models that predict whether an English adult aged 50 or over will show clinically significant depressive symptoms 2 to 4 years from now, using only their answers to a routine social and health survey today. The best model — a tuned Random Forest combining Wave 6 and Wave 7 ELSA data — achieves an ROC-AUC of **0.85**, an F1 score of **0.58** for the depressed class, and correctly identifies **71%** of all future depression cases on data it has never seen. Even when prior depression history is removed, the model still achieves an AUC of **0.77** using only physical health, mobility, social and economic features — confirming that depression risk is detectable from non-mental-health indicators alone. The pipeline is reproducible end-to-end in a single Colab notebook.

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

Depression in older adults is underdiagnosed and undertreated. The World Health Organization estimates that 7% of adults over 60 globally experience depression, but only a fraction receive a diagnosis or treatment. The reasons are well documented: stigma, somatic symptom presentation, comorbidity with physical illness, reluctance to disclose, and limited primary care screening capacity. The cost is significant — depression is a leading cause of disability and is associated with worse outcomes for cardiovascular disease, dementia, and all-cause mortality.

Machine learning offers a route around the screening bottleneck. If routine survey or health-record data already collected for other purposes can flag people at high future risk, those individuals can be prioritised for clinical assessment without requiring everyone to be screened in detail. This is exactly the use case ELSA enables.

### 2.2 The English Longitudinal Study of Ageing (ELSA)

ELSA is a representative panel study of the English population aged 50 and over. The study began in 2002 (Wave 1) and follows the same individuals every two years, with periodic refreshment to maintain age-50 inflows. By Wave 11 (2023), the dataset covers more than two decades of biennial measurements on health, cognition, social engagement, economic circumstances, and well-being.

Crucially for our purposes, ELSA includes the **Center for Epidemiologic Studies Depression Scale (CES-D)** at every wave. The ELSA version is an 8-item binary instrument (yes/no per item), giving a total score from 0 to 8. A threshold of CES-D ≥ 3 is the standard cutoff for clinically significant depressive symptoms (Steffick, 2000) and yields a prevalence of roughly 15–25% in older adult populations — consistent with epidemiological estimates.

Our access route was UK Data Service deposit 5050. The team accessed the Stata-format core wave files, IFS-derived variable files, financial derived variable files, and supporting documentation (data dictionaries, technical reports, questionnaires).

---

## 3. Research Questions

The project was framed around three research questions, decided in our group meetings and locked before any modelling began:

| RQ | Question |
|----|----------|
| **RQ1** | Can ML models trained on ELSA survey data predict depression onset 2 to 4 years in advance in adults aged 50+? |
| **RQ2** | Does combining two waves of data improve predictive performance over single-wave models, and does the prediction horizon (2 vs 4 years) matter? |
| **RQ3** | Which feature domains carry independent predictive signal beyond prior depression history? |

These questions map directly onto the experimental design (RQ2 → three prediction arms; RQ3 → leakage sensitivity + domain ablation).

---

## 4. The Dataset In Detail

### 4.1 What is in the UKDA-5050-stata bundle

The complete ELSA deposit contains 82 Stata files (~1.6 GB). For our analysis we focused on three file types per wave:

| File type | Example | Rows × cols | Content |
|-----------|---------|-------------|---------|
| **Core interview** | `wave_6_elsa_data_v2.dta` | 10,601 × 6,189 | Raw questionnaire responses including the 8 PSced depression items, self-rated health, chronic conditions, mobility, physical activity, social contact |
| **IFS derived** | `wave_6_ifs_derived_variables.dta` | 10,601 × 404 | Pre-computed summary variables maintained by the Institute for Fiscal Studies: age, sex, marital status, validated CES-D total `cesd_sc`, memory, executive function, employment, education, smoking |
| **Financial derived** | `wave_6_financial_derived_variables.dta` | 10,601 × 667 | Income and wealth variables including the benefit-unit wealth quintile `totwq5_bu_s` |

Each respondent has a unique identifier `idauniq` that persists across waves, allowing person-level joins.

### 4.2 Why Waves 6, 7, and 8

Akeeb's audit notebook examined every available wave (3–11) on three dimensions:

1. **CES-D quality.** All waves contain the 8-item CES-D with 93–97% valid response rates after recoding survey missing codes (-1 = inapplicable, -8 = don't know, -9 = refused). The CES-D measure is therefore stable across waves.

2. **Participant overlap.** The audit produced an overlap matrix showing the percentage of participants in any pair of waves. Consecutive waves retain >90% of participants (e.g. W6 → W7 = 90%), while large gaps lose more (W3 → W11 retains only 34%). For longitudinal modelling, consecutive waves are strongly preferable.

3. **Feature drift.** Across the 9 audited waves there are 13,920 unique variable names, but only 2,656 are common to every wave. Variable schemas evolve; longitudinal modelling must work from the shared subset.

Waves 6 (2012-13), 7 (2014-15), and 8 (2016-17) emerged as the strongest consecutive block: high overlap, complete CES-D, and stable feature schemas. Our analytic sample uses these three waves.

### 4.3 The CES-D scoring fix

Early in the project, an exploratory notebook reconstructed CES-D from raw PSced items but used a 0–3 per-item scale (designed for the longer HRS version), producing scores in the range 8–16 and an apparent prevalence of ~74%. This was clinically implausible — depression is not the majority condition in any adult population.

The fix was to use the IFS-validated `cesd_sc` variable directly. ELSA's CES-D items are binary (1 = yes, 2 = no after Stata recoding), so the validated sum produces the correct 0–8 range. With the threshold of CES-D ≥ 3, the analytic sample shows ~19% prevalence — exactly what the literature predicts for English adults aged 50 and over.

This experience became one of the methodological lessons of the project: **always start from validated derived variables, and verify your outcome distribution against published prevalence before training any model**.

---

## 5. Pipeline and Methodology

### 5.1 Analytic sample construction

We loaded IFS, core, and financial files for each of W6, W7, W8 and merged them on `idauniq` (inner join), keeping only participants present in all three waves.

| Step | N |
|------|---|
| W6 IFS respondents | 10,601 |
| W7 IFS respondents | 9,666 |
| W8 IFS respondents | 8,445 |
| Inner join W6 ∩ W7 ∩ W8 | 7,535 |
| With valid `cesd_sc_w8` (after dropping survey missing codes) | **7,211** |

The 7,211 figure is our final modelling sample.

### 5.2 Outcome variable

The label `depressed_w8 = (cesd_sc_w8 >= 3)` produces:

- **Depressed (1):** 1,372 participants (19.0%)
- **Not depressed (0):** 5,839 participants (81.0%)

This is the imbalance every model must handle. We address it via `class_weight='balanced'` in scikit-learn's logistic regression and random forest, and `scale_pos_weight=4` in XGBoost — both equivalent strategies for upweighting the minority class so it is not ignored.

### 5.3 Preprocessing

Three steps, in order:

1. **Survey missing code recoding.** ELSA encodes non-responses as numeric -1, -2, -8, -9. Every predictor column is converted to numeric and these codes are mapped to NaN.

2. **High-missingness column drop.** Columns with more than 40% missing values are dropped. The threshold is computed on a training-only split (75% of data) to ensure the test set does not influence which features the model sees. In practice only one column triggers the threshold (`ndepriv_w7` at 56% missing), but the methodology is correct.

3. **Wave-symmetry enforcement.** If a stem (e.g. `ndepriv`) is dropped at one wave, it is dropped from both waves. This prevents the longitudinal model from training on a feature that is half-available across time, which would produce inconsistent measurements per person.

Imputation (median) and scaling (standard) happen inside scikit-learn `Pipeline` objects so they are fit on training data only — no test-set leakage.

### 5.4 Feature engineering

We constructed 10 clinically meaningful derived features:

| Feature | Definition | Clinical meaning |
|---------|------------|------------------|
| `cesd_change` | CES-D(W7) − CES-D(W6) | Trajectory of depressive symptoms |
| `mobility_count_w6/7` | Sum of 10 mobility difficulty items | Composite physical function score |
| `adl_count_w6/7` | Sum of 6 ADL items | Basic self-care difficulty (bathing, dressing, eating) |
| `iadl_count_w6/7` | Sum of 9 IADL items | Complex daily task difficulty (managing money, taking medication) |
| `functional_burden_w6/7` | ADL + IADL count | Total functional impairment |
| `mobility_change` | Mobility(W7) − Mobility(W6) | Decline in physical function |

The `cesd_change` and `mobility_change` features explicitly capture **temporal change**, satisfying the assignment brief's requirement to "represent the temporal changes that lead to mental health issues."

### 5.5 The three prediction arms (RQ2 design)

We trained three parallel pipelines using identical participant rows but different predictor sets:

| Arm | Predictors | Time horizon | Question answered |
|-----|-----------|---------------|-------------------|
| **W6 only** | 68 features from Wave 6 | ~4 years | Can we predict from a single distant snapshot? |
| **W7 only** | 68 features from Wave 7 | ~2 years | Can we predict from a single recent snapshot? |
| **W6+W7 combined** | 138 features + change features | 2–4 years | Does longitudinal information help? |

Comparing the three arms directly answers RQ2. Using identical participant partitions across arms ensures the comparison is clean.

### 5.6 Five feature configurations per arm (RQ3 design)

Within each arm, we ran five feature configurations to test which domains matter:

| Config | Features | Purpose |
|--------|----------|---------|
| `full` | All predictors | Headline performance |
| `no_cesd` | Drop prior CES-D scores and change | Test: can we predict without depression history? |
| `health_only` | Self-rated health + chronic conditions | Test: how far does pure health get us? |
| `function_cog` | Mobility, ADL/IADL, cognition | Test: physical and cognitive function alone |
| `socioeconomic` | Employment, education, wealth, social | Test: social determinants alone |

The `no_cesd` configuration is the critical leakage check.

### 5.7 Models

Four classifiers were compared:

| Model | Why included | Strengths |
|-------|--------------|-----------|
| **Logistic Regression** | Interpretable epidemiological baseline; coefficients are odds ratios | Transparent, fast, well-understood by clinicians |
| **Random Forest** | Non-linear, handles interactions and missingness gracefully | Robust, no scaling needed, gives feature importance |
| **XGBoost** | State-of-the-art gradient boosting | Often best for tabular health data |
| **LightGBM** | Used by Zhao et al. (2025) on ELSA → AUC 0.90 in cross-sectional setting; benchmark | Very fast, handles imbalance well |

All four use class-weighting to handle the 80/20 imbalance.

### 5.8 Hyperparameter tuning

For each arm, we selected the best feature configuration by mean AUC across all four models, then ran `RandomizedSearchCV` (50 iterations, 5-fold stratified CV) on RF, XGB, and LGBM. Logistic Regression was kept at its default for a fair interpretable baseline. Tuning used the training set only — the held-out test set was untouched throughout.

### 5.9 Evaluation

The held-out test set (25%, n ≈ 1,803) is used for final reporting. Metrics:

| Metric | What it measures | Why we care |
|--------|------------------|-------------|
| **ROC-AUC** | Discrimination, threshold-free | Primary metric — how well does the model rank cases above non-cases? |
| **F1 (depressed class)** | Balance of precision and recall on the minority class | Primary clinical metric — captures depression-detection performance |
| **Precision** | Of those flagged as at-risk, what fraction actually develop depression? | False-alarm cost |
| **Recall (sensitivity)** | Of all future cases, what fraction does the model catch? | Miss rate — paramount in screening |
| **Average precision** | Area under PR curve | More informative than AUC under imbalance |
| **Calibration (Brier score)** | Are predicted probabilities trustworthy? | Crucial for clinical decision-making |

---

## 6. Results

### 6.1 Headline performance (test set)

Best tuned model per arm:

| Arm | Best Model | AUC | F1 (dep.) | Recall | Precision |
|-----|-----------|-----|-----------|--------|-----------|
| W6 only (~4 yr horizon) | LightGBM | 0.819 | 0.532 | 0.732 | 0.418 |
| W7 only (~2 yr horizon) | Random Forest | 0.824 | 0.545 | 0.668 | 0.461 |
| **W6+W7 combined** | **Random Forest (tuned)** | **0.848** | **0.582** | 0.714 | **0.491** |

**RQ1 answer:** Yes — AUC 0.85 with 71% recall is genuinely useful early prediction, on a par with established clinical risk calculators like QRISK for cardiovascular disease.

**RQ2 answer:** Yes, but the gain is modest. W6+W7 beats either single-wave arm by approximately 0.025-0.030 AUC. The two waves complement each other — the combination knows both the *level* (current CES-D) and the *trajectory* (change from W6 to W7).

### 6.2 Cross-arm comparison

The W7-only arm slightly beats the W6-only arm (0.824 vs 0.819 AUC). This is intuitive: a more recent snapshot is closer in time to the outcome, so its predictors are less stale. But the gain from a 2-year shorter horizon is small (~0.005 AUC), suggesting that depression risk profiles in this population evolve slowly over 2-year windows — a clinically meaningful insight in itself.

### 6.3 Domain ablation — what happens when we remove each domain (W6+W7 arm)

| Removed domain | New AUC | AUC drop |
|----------------|---------|----------|
| Prior depression | 0.771 | **0.077** |
| Self-rated health | 0.843 | 0.005 |
| Chronic conditions | 0.849 | -0.000 |
| Mobility / function | 0.849 | -0.001 |
| Cognition | 0.849 | -0.000 |
| Socioeconomic | 0.849 | -0.001 |
| Social / housing | 0.850 | -0.001 |
| Lifestyle / digital | 0.849 | -0.000 |
| Demographics | 0.848 | 0.001 |

Prior depression is the dominant predictor — removing it costs 0.077 AUC. Every other single domain costs less than 0.005. This does **not** mean other domains are useless; it means they overlap heavily (e.g. mobility ↔ self-rated health ↔ chronic conditions all measure the same underlying physical health), so removing one alone is partially compensated by others. The leakage sensitivity analysis (Section 6.5) tests this overlap directly.

### 6.4 SHAP — the two-act narrative (RQ3)

**Act 1 — full model.** With all features present, SHAP confirms what the coefficients and importance plots already show: `cesd_sc_w7` and `cesd_sc_w6` dominate, contributing roughly 4× more to predictions than any other feature. Self-rated health, mobility count, financial difficulty, and CES-D change appear next. This tells us prior depression history is the single most informative signal.

**Act 2 — without CES-D.** Refit on the `no_cesd` configuration, the SHAP top-20 reorders dramatically. **Self-rated health (`srh_hrs`, `Hehelf`) becomes the top predictor.** Mobility count, functional burden, financial difficulty, and `hlimwrk` (health limits work) take the next slots. Demographics (age, sex) and wealth quintile also rise.

**Why this matters scientifically.** Act 2 is the clinically novel finding. It demonstrates that depression risk leaves a measurable footprint in physical health, mobility, and economic circumstances 2-4 years before the depression itself manifests. This aligns with the biopsychosocial model of late-life depression, where physical decline, social isolation, and financial stress are causal contributors, not just consequences.

### 6.5 Calibration

Tree-based models (RF, XGB, LGBM) are well-known to produce overconfident probabilities — they tend to push predictions toward 0 or 1. Isotonic regression calibration on a held-out fold corrects this without changing AUC. The result: a person assigned a 30% predicted risk by the calibrated model genuinely has roughly a 30% chance of developing depression. This is the property required for any clinical screening application.

### 6.6 Leakage sensitivity (with vs without prior CES-D)

| Arm | Full AUC | No-CES-D AUC | Drop |
|-----|----------|--------------|------|
| W6 only | 0.819 | 0.739 | 0.080 |
| W7 only | 0.824 | 0.769 | 0.055 |
| **W6+W7** | **0.848** | **0.773** | **0.075** |

Even after stripping out every CES-D-related feature (prior scores, na count, change), the W6+W7 model still achieves AUC = 0.77. **This is the central scientific claim of the project.** Depression risk is identifiable from non-mental-health features at a level that would still be clinically useful as a first-stage screen. Health, mobility, and socioeconomic features contain genuine, independent predictive signal — not just an echo of past depression.

### 6.7 Ensemble

A simple averaging ensemble of the three tuned tree models (RF + XGB + LGBM) on the W6+W7 full configuration produced AUC = 0.847 — essentially tied with the best single model. This means the algorithms are learning the same underlying patterns, and there is no diversity bonus to exploit. We report the tuned Random Forest as the headline model for simplicity.

---

## 7. What The Model's Output Means

### 7.1 What it produces

For any person aged 50+ whose Wave 6 and Wave 7 ELSA-style answers are available, the model produces three things:

1. **A probability between 0 and 1** — the model's estimate of the chance this person will score CES-D ≥ 3 at Wave 8 (i.e. show clinically significant depressive symptoms 2-4 years from now).
2. **A binary label** — depressed (1) or not depressed (0), thresholded at 0.5 by default.
3. **Calibrated probabilities** — after isotonic regression, these are trustworthy: a "30% chance" really means 30 in 100 such people will develop depression.

### 7.2 What it tells you

If you rank everyone by predicted risk and screen the top 30%, you would catch about **71% of all future depression cases** in that population. The remaining 29% are missed — false negatives. About half of those flagged are false positives (would not actually develop depression). For a screening tool intended to prioritise people for clinical follow-up, that recall/precision balance is acceptable; for a standalone diagnostic instrument, it is not.

### 7.3 What it is not

| It is | It is not |
|--------|-----------|
| A risk *probability* for elevated depressive symptomatology | A diagnosis of Major Depressive Disorder |
| A correlation-based predictor | A causal model |
| Validated on the English population aged 50+ | Validated on younger adults, non-English populations, or institutionalised individuals |
| Useful as a population-screening prioritisation tool | Useful as a standalone clinical instrument |
| Honest about uncertainty (calibrated probabilities) | A black-box "yes/no" verdict |

### 7.4 The clinical scenario

Imagine a GP practice that already records ELSA-style data through routine over-50 health checks. The model could flag, say, the 200 patients out of 1,000 with the highest predicted depression risk. Those 200 would be invited for a 15-minute clinical interview using a validated diagnostic tool (e.g. PHQ-9 or structured clinical interview). Roughly 100 of them (precision ~50%) would meet criteria for early intervention; the other 900 patients are not screened in detail, saving substantial clinician time. Of the 1,000, about 142 would actually develop depression in the next 2-4 years; the model catches ~100 of them (71% recall). Compared to no targeted screening, this is a meaningful improvement in early detection.

---

## 8. Limitations

### Methodological

1. **Prior depression dominates.** Removing CES-D drops AUC from 0.85 to 0.77. The model's main signal is depression history (state dependence). The leakage sensitivity is what rescues the clinical novelty claim.

2. **Attrition bias.** Our analytic sample requires presence in all three waves. About 30% of Wave 6 respondents are excluded — and those people may be sicker, more isolated, or institutionalised, exactly the population at highest risk. The model likely underestimates true population risk.

3. **CES-D ≥ 3 is screening, not diagnosis.** It captures elevated depressive symptomatology, not Major Depressive Disorder. A person flagged by the model needs clinical confirmation before any treatment decision.

4. **Observational design.** We identify *predictors*, not *causes*. Low wealth predicts depression; we cannot say poverty causes depression from this analysis alone — there may be unmeasured confounders (childhood adversity, undiagnosed physical illness, social network).

5. **Class imbalance.** Precision for the depressed class is moderate (~49%). About half of model-flagged people would not develop depression. In a screening context this is acceptable; in a confirmatory context it is not.

6. **Wave selection introduces survivor effects.** Anyone who died, was institutionalised, or refused between W6 and W8 is excluded by the inner join.

### Technical (acknowledged from PR review process)

7. **Missingness filter is computed once on a training split, not within each CV fold.** The gold standard for nested validation would wrap the missingness gate inside a custom transformer fit per fold. In practice the only column dropped (`ndepriv_w7` at 56%) would be dropped under any reasonable split, so the simplification has no practical impact.

8. **Engineered features bypass the missingness gate.** All 10 derived features have <0.3% missingness in our data, so this is theoretical only — but a production pipeline should apply the same gate uniformly.

9. **Logistic regression coefficients are on a standardised scale.** Because features pass through StandardScaler before LR, the reported coefficients are log-odds per 1 SD change, not per 1 raw unit. This is labelled correctly on the plot but should be noted when interpreting.

10. **`functional_burden` uses `+` rather than `sum(..., min_count=1)`** — meaning if either ADL or IADL is fully missing, the burden score is NaN even if the other component is present. In our data this scenario does not occur (ADL and IADL come from the same questionnaire block) but the implementation is not maximally NaN-tolerant.

---

## 9. Future Directions

1. **Incident depression model.** Exclude participants with CES-D ≥ 3 at baseline (W6) and predict only first-onset depression at W8. This is harder but more clinically meaningful.

2. **External validation.** Test the trained pipeline on the US Health and Retirement Study (HRS), the Survey of Health, Ageing and Retirement in Europe (SHARE), and the Irish Longitudinal Study on Ageing (TILDA). All three use harmonised CES-D measures and could test cross-population generalisability.

3. **Nurse visit biomarkers.** ELSA collects blood pressure, BMI, grip strength, and inflammatory markers (CRP, fibrinogen) from nurse visits at Waves 2, 4, 6, and 8. None were used here. Adding biological signal could distinguish physical-decline-driven depression from socially-driven depression.

4. **Multi-wave trajectory modelling.** Rather than two snapshots (W6, W7), latent growth curve models or recurrent neural networks could capture richer temporal patterns across many waves.

5. **Subgroup analysis.** Are the predictors equally informative across sex, ethnicity, and socioeconomic strata? Differential calibration is a major fairness concern in clinical ML and was not evaluated here.

6. **Cost-effectiveness modelling.** Combined with intervention efficacy data (e.g. CBT acceptance and remission rates in this population), the model's outputs could feed a Markov decision-process analysis estimating quality-adjusted life-years (QALYs) gained per pound of screening cost.

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
   • RandomizedSearchCV on RF/XGB/LGBM (9 tuned models)
        │
        ▼
[11. Evaluate on held-out test set]
   • ROC-AUC, F1, Precision, Recall, Confusion matrix, Calibration
        │
        ▼
[12. Interpretation]
   • Domain ablation • SHAP Act 1 (full) • SHAP Act 2 (no CES-D)
        │
        ▼
[13. Sensitivity]
   • Leakage analysis (with vs without prior CES-D, all 3 arms)
        │
        ▼
[14. Reporting]
   • 16 figures, 4 results CSVs, this report, presentation
```

---

## 11. Reproducibility

The submission notebook (`submission/ELSA_Depression_Prediction_Final_v2.ipynb`) is designed to run end-to-end in a single Colab session. The user sets one path variable (`ELSA_PATH`) pointing to either a downloaded UKDA-5050 zip file or the extracted folder. The notebook installs missing dependencies, locates the Stata files, runs all 60 baseline experiments + 9 tuning rounds + ensemble, and exports 16 figures and 4 CSVs to Google Drive. Expected runtime is 25 to 40 minutes on a standard Colab CPU instance.

A fixed random seed (`SEED=42`) is used throughout. All splits, CV folds, hyperparameter searches, and SHAP samples are deterministic. Any user with UKDS access can reproduce every figure and every number in this report.

---

## 12. Team Contributions

See [`team_contributions.md`](team_contributions.md) for the full list. Brief summary:

- **Akeeb Lawel** — Data audit, wave selection, feature funnel
- **Fiyin Akano** — Original W6+W7 pipeline, CES-D fix, leakage analysis, PR review process
- **Zannat Chowdhury Sagar** — Preprocessing baseline, enhanced pipeline, final submission notebook
- **Giridhar, Pushkar, Poorna** — see contributions doc

---

## 13. References

Banks, J., Breeze, E., Lessof, C., and Nazroo, J. (Eds.). (2006). *Retirement, health and relationships of the older population in England: The 2004 English Longitudinal Study of Ageing*. London: Institute for Fiscal Studies.

Bergstra, J., and Bengio, Y. (2012). Random search for hyper-parameter optimization. *Journal of Machine Learning Research*, 13, 281–305.

Ke, G., Meng, Q., Finley, T., et al. (2017). LightGBM: A highly efficient gradient boosting decision tree. *Advances in Neural Information Processing Systems*, 30.

Lundberg, S. M., and Lee, S.-I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems*, 30.

Radloff, L. S. (1977). The CES-D scale: A self-report depression scale for research in the general population. *Applied Psychological Measurement*, 1(3), 385–401.

Steffick, D. E. (2000). *Documentation of affective functioning measures in the Health and Retirement Study*. HRS Documentation Report DR-005. Ann Arbor: University of Michigan.

Turvey, C. L., Wallace, R. B., and Herzog, R. (1999). A revised CES-D measure of depressive symptoms and a DSM-based measure of major depressive episodes in the elderly. *International Psychogeriatrics*, 11(2), 139–148.

Zhao, Y., Wan, X., and Liu, Z. (2025). Machine learning identifies determinants of depressive symptoms in multinational middle-aged and older adults. *npj Digital Medicine*.

---

## Appendix A — Figures Index

All saved to `outputs/figures/` and `submission` Drive output folder.

| File | Section | Purpose |
|------|---------|---------|
| `01_data/outcome_distribution.png` | Background | CES-D histogram, class balance |
| `02_experiments/auc_all_arms_configs.png` | Experiment | AUC across all 60 baseline experiments |
| `03_results/arm_comparison.png` | Results | Cross-arm AUC comparison |
| `03_results/roc_curves.png` | Results | ROC curves, best model per arm |
| `03_results/pr_curves.png` | Results | Precision-recall curves |
| `03_results/confusion_matrices.png` | Results | Test-set confusion matrices |
| `03_results/ensemble_roc.png` | Results | Ensemble vs individual models |
| `04_interpretation/domain_ablation.png` | Interpretation | Leave-one-domain-out |
| `04_interpretation/shap_act1_full.png` | Interpretation | SHAP, full model |
| `04_interpretation/shap_act2_no_cesd.png` | Interpretation | SHAP, no prior CES-D |
| `04_interpretation/calibration.png` | Interpretation | Reliability diagrams |
| `04_interpretation/lr_coefficients_standardised.png` | Interpretation | LR coefficients |
| `04_interpretation/lgbm_importance_top20.png` | Interpretation | LightGBM importance |
| `04_interpretation/feature_target_correlation.png` | Interpretation | Pearson correlations |
| `04_interpretation/domain_correlation_heatmap.png` | Interpretation | Cross-feature correlations |
| `05_sensitivity/leakage_sensitivity.png` | Sensitivity | With vs without CES-D |

## Appendix B — Results Files

- `results/all_experiments.csv` — every (arm × config × model) combination, baseline run
- `results/tuned_models.csv` — best tuned model per arm with CV best AUC
- `results/domain_ablation.csv` — leave-one-domain-out AUC drops
- `results/leakage_sensitivity.csv` — full vs no-CES-D for every arm

---

*End of report.*
