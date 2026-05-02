# Q&A Flashcard Pack — ELSA Depression Prediction

**Purpose:** Anyone in the team can pick this up and answer any likely question during the 10-minute presentation Q&A.

**Format:**
- **Q:** the question
- **One-liner:** a 5-second answer for when you've gone blank
- **Deeper:** a 30-second confident answer
- **Anchor:** which slide / figure / number this lives on

Read each card aloud once before the presentation. Anchor numbers help you point back to the deck if asked.

---

## Section A — Background and motivation

### A1. Why depression in older adults? Why not younger people, or anxiety, or another condition?
- **One-liner:** Late-life depression is the WHO's quiet epidemic, ELSA has a validated CES-D scale every wave, and the prediction has clear clinical utility.
- **Deeper:** About 7% of adults over 60 have depression globally; most are never diagnosed. ELSA's CES-D scale is collected at every wave with >93% completeness. Anxiety is not measured as consistently across the waves we use, so we chose to do depression *well* rather than two outcomes badly.
- **Anchor:** Slide 2.

### A2. Why use ELSA specifically?
- **One-liner:** ELSA is the gold-standard longitudinal study of English over-50s, with the same individuals measured every two years since 2002.
- **Deeper:** ELSA gives us 21 years of biennial measurements on the same people, validated CES-D at every wave, and harmonised survey instruments. UK Data Service deposit 5050 is publicly accessible to researchers. The longitudinal design lets us predict *future* depression rather than just describing current depression.
- **Anchor:** Slide 4.

### A3. Why the CES-D ≥ 3 cutoff?
- **One-liner:** Steffick (2000) standard cutoff for clinically significant depressive symptoms in the 8-item CES-D.
- **Deeper:** The 8-item CES-D used in ELSA scores 0 to 8. Steffick's threshold of ≥3 is the standard cutoff used by ELSA, the US Health and Retirement Study, and SHARE for screening. It yields a 19% prevalence in our sample, which matches published estimates for English over-50s. We are honest that this is a *screening* threshold, not a diagnosis.
- **Anchor:** Slide 5.

---

## Section B — Data and waves

### B1. Why Waves 6, 7, and 8 specifically?
- **One-liner:** Strongest consecutive longitudinal block — 90%+ participant overlap, complete CES-D, stable feature schemas.
- **Deeper:** Akeeb's audit examined every available wave (3-11). All have CES-D with 93-97% completeness. Consecutive waves retain >90% of participants; large gaps (e.g. W3 → W11) lose 66%. Of 13,920 unique variables across all waves, only 2,656 are common — schemas drift. W6, W7, W8 emerged as the longest consecutive block with high overlap and stable features.
- **Anchor:** Slide 4.

### B2. How many participants in your final sample?
- **One-liner:** 7,211 — those present in all three waves with valid CES-D at Wave 8.
- **Deeper:** We started with 10,601 W6 respondents, 9,666 at W7, and 8,445 at W8. Inner-joining on participant ID gives 7,535. Filtering to valid CES-D at the outcome wave gives 7,211. That's our analytic sample.
- **Anchor:** Slide 4 funnel.

### B3. What's the class balance?
- **One-liner:** 19% depressed (1,372), 81% not depressed (5,839) — moderate imbalance.
- **Deeper:** Handled in every model via `class_weight='balanced'` for Logistic Regression and Random Forest, and `scale_pos_weight=4` in XGBoost. We report ROC-AUC, F1 for the depressed class, recall, and average precision rather than raw accuracy because accuracy is misleading under imbalance.
- **Anchor:** Slide 5.

---

## Section C — Pipeline and methodology

### C1. Walk me through your pipeline in one minute.
- **One-liner:** Load + merge → preprocess → engineer features → split → train + tune four models → evaluate.
- **Deeper:** We inner-join the IFS, core, and financial files on participant ID. Recode survey missing codes (-1, -8, -9) to NaN. Drop columns with >40% missing — but the threshold is computed on the training split only, so the test set never influences feature selection. Engineer ten longitudinal features including the change in CES-D from W6 to W7. 75/25 stratified split, 5-fold stratified cross-validation on the training set. Train Logistic Regression, Random Forest, XGBoost, and LightGBM with class weighting. Tune the best feature configuration per arm via RandomizedSearchCV. Calibrate via isotonic regression. Evaluate on the held-out test set.
- **Anchor:** Slide 6.

### C2. Why these four algorithms?
- **One-liner:** LR for interpretability, RF for non-linearity, XGB and LGBM as state-of-the-art tree-based benchmarks.
- **Deeper:** Logistic Regression is our interpretable baseline — coefficients are odds ratios that clinicians understand. Random Forest handles non-linear interactions and missingness. XGBoost is the state-of-the-art for tabular health data. LightGBM was used by Zhao et al. (2025) on ELSA achieving AUC 0.90 in the cross-sectional setting, so it's a literature benchmark. We compared all four; tree-based models won, all within 0.005 AUC of each other.
- **Anchor:** Slide 7.

### C3. Did you use deep learning? If not, why?
- **One-liner:** No. Tabular ELSA at 7,000 rows is too small to beat tuned tree models, which are also more interpretable.
- **Deeper:** Tabular data of this scale and structure consistently favours gradient-boosted trees over deep nets. We get state-of-the-art performance, native handling of missing values, fast training, and SHAP interpretability. We also tried a simple averaging ensemble of RF + XGB + LGBM — it tied with the best single model, suggesting the algorithms are converging on the same patterns. There's no diversity bonus from deep learning to be expected here.
- **Anchor:** Slide 7.

### C4. Why three prediction arms?
- **One-liner:** To answer RQ2 — does combining waves help vs. a single snapshot?
- **Deeper:** W6-only is a 4-year prediction horizon, W7-only is 2 years, and W6+W7 combines both with engineered change features. Identical participant rows across all three arms makes the comparison clean. Result: W7-only (0.824 AUC) beats W6-only (0.819) slightly, and the combined model wins at 0.848. The gain from combining waves is real but small — about 0.025 AUC.
- **Anchor:** Slide 7-8.

### C5. How did you tune hyperparameters?
- **One-liner:** RandomizedSearchCV with 50 iterations and 5-fold stratified CV, AUC as the optimisation metric.
- **Deeper:** For each arm, we picked the best feature configuration by mean baseline AUC across all four models, then tuned RF, XGB, and LGBM on that configuration. Logistic Regression kept default parameters as the baseline. Tuning was done entirely on the training set; the test set was untouched throughout. Random search was chosen over grid search because Bergstra and Bengio (2012) showed it explores high-impact hyperparameter directions more efficiently with the same compute budget.
- **Anchor:** Slide 7.

---

## Section D — Results

### D1. What's the headline result?
- **One-liner:** Tuned Random Forest on combined W6+W7 features achieves AUC 0.85 with 71% recall on the held-out test set.
- **Deeper:** AUC 0.848 on the test set. F1 for the depressed class is 0.582. Recall (sensitivity) is 71.4% — we catch seven out of every ten future depression cases. Precision is 49% — about half of the people we flag will actually develop depression. That precision-recall balance is acceptable for a screening tool that prioritises follow-up, not a standalone diagnostic instrument.
- **Anchor:** Slide 8.

### D2. Why Random Forest as the headline rather than XGBoost or LightGBM?
- **One-liner:** All three trees were within 0.005 AUC. RF has the cleanest calibration, smallest hyperparameter footprint, and the most readable SHAP visualisations.
- **Deeper:** All three tree models performed within 0.005 AUC of each other after tuning. We picked Random Forest because it has the most stable calibration after isotonic correction, the simplest hyperparameter footprint to defend in a 10-minute talk, and clear SHAP plots. Reporting one model rather than three keeps the presentation honest — they all tell the same story.
- **Anchor:** Slide 8.

### D3. ROC-AUC vs. PR — which matters more?
- **One-liner:** PR is more informative under our 80/20 imbalance; ROC is the conventional headline metric.
- **Deeper:** ROC-AUC summarises ranking performance across all thresholds and is comparable across studies. But under class imbalance, the no-skill baseline is 0.5 for ROC and 0.19 (the prevalence) for PR. Average precision of 0.55 versus a no-skill baseline of 0.19 is a meaningful skill margin. We report both for transparency.
- **Anchor:** Slide 8.

---

## Section E — Interpretation

### E1. What features matter most?
- **One-liner:** Prior CES-D dominates; self-rated health, mobility, CES-D change, and financial difficulty come next.
- **Deeper:** SHAP analysis ranks W7 CES-D and W6 CES-D as roughly 4× more impactful than any other single feature. The next tier is self-rated health, mobility count, CES-D change (the trajectory feature), functional burden, and financial difficulty. This is the biopsychosocial signature of late-life depression, well-established in the gerontology literature.
- **Anchor:** Slide 9, SHAP figure.

### E2. Isn't this just predicting that depressed people stay depressed?
- **One-liner:** Partially yes — that's why we ran the leakage sensitivity test. Without prior CES-D, AUC is still 0.77.
- **Deeper:** This is exactly why we ran the leakage sensitivity. We re-trained the model after stripping out every CES-D feature — prior scores, missing-count, change. AUC drops from 0.848 to 0.773 — a real 0.075 drop confirming that prior depression matters. But 0.77 is still a clinically usable signal, and it's achieved with no mental health features at all. Half of the discriminative power lives in physical health, mobility, finances, and demographics.
- **Anchor:** Slide 10.

### E3. What is the central scientific finding?
- **One-liner:** Depression risk leaves a measurable footprint in physical, functional, and economic data 2-4 years before symptoms emerge.
- **Deeper:** Even without using any mental health feature at all, the model achieves AUC 0.77 — a clinically useful screening signal. This means a GP practice that already collects routine over-50 health-check data could deploy a model like this without administering any depression questionnaire. It also aligns with the biopsychosocial model of late-life depression, where physical decline, social isolation, and economic stress are causal contributors, not just consequences.
- **Anchor:** Slide 10.

### E4. What does the model output mean for an individual?
- **One-liner:** A calibrated probability between 0 and 1 — their estimated risk of developing depression in 2-4 years.
- **Deeper:** The model produces a probability, not a diagnosis. After isotonic calibration, "30% predicted risk" really means roughly 30 in 100 people like this person will develop depression. Above a 0.5 threshold we label them as predicted-depressed; in real deployment the threshold would be tuned to clinic capacity. The model is honest about uncertainty — it's a risk score, not a verdict.
- **Anchor:** Slide 10.

---

## Section F — Limitations and threats

### F1. What's the biggest weakness?
- **One-liner:** Attrition bias — we only model people who survived to Wave 8, and they're systematically less sick than those who dropped out.
- **Deeper:** Our analytic sample requires presence in all three waves. About 30% of W6 respondents are excluded by attrition — those who died, were institutionalised, or refused. Those people are likely the highest-risk for depression, so the model probably underestimates true population risk. This is a survivor effect inherent to the inner-join design.
- **Anchor:** Slide 11.

### F2. Causality?
- **One-liner:** This is observational and predictive, not causal. We identify predictors, not causes.
- **Deeper:** We can say low wealth predicts depression. We cannot say poverty causes depression from this analysis. There may be unmeasured confounders — childhood adversity, undiagnosed physical illness, social network density. A causal claim would need a designed intervention or instrumental-variable analysis. We're explicit about this limitation.
- **Anchor:** Slide 11.

### F3. Generalisability?
- **One-liner:** Validated only on English adults aged 50+. Excludes institutionalised individuals. Has not been audited for fairness across subgroups.
- **Deeper:** Our sample is community-dwelling English adults aged 50 and over. The model would need to be re-validated on other populations — younger adults, non-English populations, or care-home residents. ELSA also has cohort effects: today's 50-year-olds are not the 50-year-olds in our sample. We have not yet evaluated calibration across sex, ethnicity, or socioeconomic strata; that audit is the first thing to do before any deployment claim.
- **Anchor:** Slide 11.

### F4. Can this be deployed in a hospital tomorrow?
- **One-liner:** No. It's a research prototype, not a clinical instrument. It needs external validation, fairness auditing, and regulatory approval first.
- **Deeper:** Three things must happen first. Validation on independent cohorts (HRS in the US, SHARE in Europe, TILDA in Ireland) to confirm cross-population transfer. A fairness audit across demographic subgroups. Then a prospective validation study with intervention efficacy data feeding a cost-effectiveness analysis. After that, regulatory approval as a clinical decision support tool. Today, this is a research artefact.
- **Anchor:** Slide 12.

---

## Section G — Common methodology challenges

### G1. How did you avoid data leakage?
- **One-liner:** Train-only feature selection, no test-set imputation parameters, fixed split before any preprocessing.
- **Deeper:** Three layers. First, the >40% missingness threshold is computed on the training split only. Second, median imputation and standard scaling happen inside scikit-learn `Pipeline` objects, so they're fit on training data only and never see the test set. Third, hyperparameter tuning uses cross-validation within the training set only; the held-out test set is touched exactly once at the end. We acknowledge a minor refinement: the >40% gate could be applied per CV fold for full nested validation, but in practice only one column meets the threshold under any reasonable split.
- **Anchor:** Slide 6.

### G2. Why class weighting rather than SMOTE or undersampling?
- **One-liner:** Class weighting preserves the data and is consistent with how we'd deploy the model in practice.
- **Deeper:** SMOTE generates synthetic minority examples, which can introduce noise and overfit local boundaries. Undersampling discards data and degrades generalisation. Class weighting modifies the loss function to penalise minority-class errors more heavily, which is the most principled approach when you have enough minority samples (we have 1,372). It also matches how a deployed model would be tuned to clinic capacity at inference time.
- **Anchor:** Slide 5.

### G3. What about temporal validation — split by time, not at random?
- **One-liner:** Our split is at the participant level, not the time level. The temporal direction is built in: we predict W8 from W6 and W7.
- **Deeper:** This is a common confusion. A temporal hold-out applies when you have time-series data and want to test forecasting on later periods. Our design is participant-level: each row is a person, observed across W6, W7, W8. We hold out 25% of *people* for testing. The temporal direction is enforced by feature design — predictors come from W6 and W7, the label is W8. There's no temporal leakage.
- **Anchor:** Slide 7.

### G4. Why didn't you do feature selection first?
- **One-liner:** We did — the audit funnel reduced 12,539 candidates to 30 curated features per wave. Then within-pipeline regularisation handles the rest.
- **Deeper:** Akeeb's audit applied a four-stage filter: drop admin columns, drop high-missingness columns, restrict to theory-led domains based on Lu et al. (2025), and collapse concept-prefix duplicates. From 12,539 raw candidates we reached 30 curated features per wave. Within the modelling pipeline, regularised LR and tree-based feature importance further attenuate noisy features. We deliberately avoided automated feature selection inside CV folds because it can create selection-bias-driven optimism — the funnel was theory-led, not data-driven.
- **Anchor:** Slide 4.

---

## Section H — "Surprise" questions

### H1. What would you do differently if you started over?
- **One-liner:** Start with the leakage sensitivity analysis as the headline, not as a sub-result.
- **Deeper:** Methodologically nothing major would change — the pipeline is sound. Presentation-wise, I'd lead with the leakage sensitivity finding (AUC 0.77 without depression history) earlier, because that's the clinically novel result. The 0.85 AUC headline could mislead a reader into thinking the model is just memorising depression history.

### H2. What was the hardest part?
- **One-liner:** Catching the CES-D scoring bug — the kind of error that quietly survives if you don't validate against published prevalence.
- **Deeper:** An exploratory notebook reconstructed CES-D from raw items on a 0-3 scale, producing 74% prevalence. That's the wrong scale — ELSA's items are binary. The fix was to use IFS-validated `cesd_sc`. The lesson: always validate your outcome against published epidemiological estimates before training any model. A 74% depression prevalence is biologically implausible; if we'd missed it, every result downstream would be invalid.

### H3. How long did this take?
- **One-liner:** About 8 weeks from team formation to submission, with peak modelling activity in mid-April.
- **Deeper:** Team formed in late February. Initial roadmap and data access in early April. Audit, modelling, and PR review cycles through mid-April. Final submission notebook integration in late April through early May. Total developer time across the team was roughly 80-100 hours.

### H4. Why did you split the work the way you did?
- **One-liner:** Audit needed deep familiarity with ELSA documentation; modelling needed scikit-learn fluency. Different team members brought different strengths.
- **Deeper:** Akeeb led the audit because he has the strongest documentation-reading discipline. Fiyin and Zannat led modelling because both have prior scikit-learn experience. The CES-D fix was a collaborative catch — Fiyin spotted the prevalence anomaly during preprocessing, the team agreed on the IFS-validated variable. The split was role-driven, not equality-driven.

---

## Recommended distribution

Each member should know:

| Member | Especially focused on | Plus all "common" cards |
|--------|----------------------|--------------------------|
| Akeeb | Section A, Section B (audit, wave selection) | All cards |
| Zannat | Section C (pipeline, models), Section D (results) | All cards |
| Fiyin | Section E (interpretation, leakage), Section G (methodology challenges) | All cards |
| All speakers | Sections F (limitations) and H (surprises) | All cards |

If a question lands and the assigned section-owner isn't sure, anyone can hand off with: *"That sits closer to [name]'s area — over to you."* Practise the hand-off; it looks coordinated rather than evasive.
