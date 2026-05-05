# Speaker Notes — ELSA Depression Prediction (10-minute version)

14 slides, target ~43 seconds per slide. Coursework brief allows 10 min + 5 min Q&A.

---

## Slide 1 — Title  *(20 s)*

> "Good afternoon. Our project asked one question: can we predict, today, whether an older adult will become depressed in two to four years' time using only routine survey data? We worked with the English Longitudinal Study of Ageing — and the answer is yes, with the surprising twist that we can do it even without using their depression history at all."

---

## Slide 2 — The Problem  *(45 s)*

> "Late-life depression is the WHO's quiet epidemic. Around 7% of adults over sixty have it; most are never diagnosed. Stigma, somatic presentation, and the time pressure on primary care all conspire to keep it invisible — and the consequences ripple into worse cardiovascular, dementia, and mortality outcomes.
>
> Universal screening is impractical. But ML offers a way out: routine over-50 data is *already* collected, and a model that flags the highest-risk people for clinician follow-up could change the screening economics. The key word is *early*.
>
> Project goal: predict depression onset 2 to 4 years ahead from data already in routine collection."

---

## Slide 3 — Research Questions  *(40 s)*

> "We locked three research questions before any modelling. RQ1 — can ML predict depression at all from survey data? RQ2 — does combining waves help? RQ3 — what predicts depression *beyond* depression history itself?
>
> RQ2 is answered by running three prediction arms: Wave 6 alone, Wave 7 alone, and the two combined. RQ3 is answered by SHAP, a leakage sensitivity test, and a domain ablation."

---

## Slide 4 — The ELSA Dataset  *(50 s)*

> "ELSA is a representative panel of English adults aged 50 and over, tracked every two years from 2002 through 2023. The 8-item CES-D depression scale is collected every wave.
>
> Akeeb's audit established three things: CES-D quality is excellent across all waves, between 93 and 97% valid; participant overlap exceeds 90% between consecutive waves; but only 2,656 of 13,920 unique variables exist in every wave. Waves 6, 7, and 8 emerged as the strongest consecutive longitudinal block.
>
> The funnel: 10,601 Wave 6 respondents, intersected through Wave 7 and Wave 8, valid CES-D filter, ends with 7,211 participants. That's our analytic sample."

---

## Slide 5 — The Outcome Variable  *(40 s)*

> "Our binary label is CES-D ≥ 3 at Wave 8 — Steffick's standard cutoff. Observed prevalence is 19%, exactly what the literature predicts.
>
> Quick lesson: an earlier exploratory notebook reconstructed CES-D from raw items on a 0-3 scale, producing a 74% prevalence — clinically implausible. We caught it by checking against published prevalence and switched to the IFS-validated `cesd_sc` variable. Always validate against published prevalence.
>
> Class imbalance handled by class weighting in every model."

---

## Slide 6 — The Pipeline  *(50 s)*

> "Six stages, all reproducible in a single Colab notebook. Load and merge IFS, core, and financial files on the participant ID. Recode survey missing codes to NaN, then drop columns above 40% missing on a *training-only* estimate.
>
> Engineer ten longitudinal features. The most important is `cesd_change`, the change in depression score from Wave 6 to Wave 7 — that's what makes this a true longitudinal model. We also build mobility, ADL, IADL, and combined functional burden scores.
>
> Then a 75/25 stratified split, 5-fold CV on the training set, four algorithms with class-weighted loss, tune the best feature configuration per arm, evaluate with AUC, F1, recall, calibration, SHAP."

---

## Slide 7 — Experimental Design  *(40 s)*

> "Three arms answer RQ2: Wave 6 alone is roughly a 4-year horizon, Wave 7 alone is roughly 2 years, and the combined model uses both plus our change features. Identical participants across all three arms — clean comparison.
>
> Within each arm, five feature configurations answer RQ3. Three arms times five configs times four models gives sixty baseline experiments. The best configuration per arm is tuned with RandomizedSearchCV, thirty iterations, five-fold CV. Logistic Regression stays at defaults as a fair interpretable baseline."

---

## Slide 8 — Headline Results  *(50 s)*

> "Headline: tuned Random Forest combining Wave 6 and Wave 7 reaches AUC 0.85 on the held-out test set. F1 for the depressed class is 0.58, recall is 71% — we catch seven out of ten future cases.
>
> Cross-arm comparison: Wave 7 alone slightly beats Wave 6 alone, 0.824 versus 0.819 — confirms the recent-snapshot intuition. Combined model edges both at 0.848. The longitudinal gain is real but small.
>
> Note the band at the bottom: a stacking ensemble — Random Forest plus LightGBM with a logistic regression meta-learner — produces recall 0.773, the highest of any model we tested. That's our pick if maximum case detection matters."

---

## Slide 9 — Clinical Deployment Readiness  *(40 s)*  *(NEW)*

> "Three readiness analyses for real deployment. Threshold optimisation: the default 0.5 cutoff is naive. Sweeping the threshold shows F1 peaks around 0.58, lifting binary F1 from 0.58 to 0.61 — a 5% gain just from picking the right cutoff. Lower thresholds raise recall, useful when missing a case costs more than false alarms.
>
> Calibration: tree models are under-confident at low probabilities. Isotonic regression on the Random Forest preserves AUC 0.848 while making the probabilities reliable across the 0.2 to 0.6 range. Logistic regression is naturally well-calibrated.
>
> Stacking ensemble: Random Forest plus LightGBM with an LR meta-learner reaches recall 0.77 — highest of any model. Soft-vote didn't help because RF, XGB, and LGBM share correlated errors.
>
> Three deployment recommendations match three clinical needs: best discrimination, calibrated RF for risk scoring, and stacking for screening."

---

## Slide 10 — What Drives the Predictions  *(40 s)*

> "SHAP analysis on the full model. Prior CES-D scores at Wave 7 and Wave 6 dominate, as expected. The next tier is informative: self-rated health, mobility count, depression-score change, and financial difficulty.
>
> Late-life depression has a measurable biopsychosocial signature. Physical decline, mental health trajectory, and economic stress all show up as distinct predictive signals two to four years before symptoms emerge. Consistent with the established gerontological literature."

---

## Slide 11 — Robustness: Three Methods Agree  *(40 s)*  *(NEW)*

> "Now is this just a SHAP artefact? No. We ran three independent interpretation methods — SHAP values, logistic regression standardised coefficients, and LightGBM gain importance — and they converge on the same ranking. Prior CES-D dominates all three. Self-rated health, mobility count, and financial difficulty land in the top tier of all three. Wealth and sex appear in the mid-tier across all three.
>
> The right side: a leave-one-domain-out ablation. Removing prior depression drops AUC by 0.077 — that's the only domain that matters in isolation. Removing any other single domain: drop near zero. The reason is correlation: health, mobility, and finance share moderate correlations of 0.4 to 0.5, so when one is removed the model reconstructs the signal from neighbours. The signal is robust, not redundant.
>
> Bottom line: RQ3 holds firm under all three methods plus ablation."

---

## Slide 12 — Beyond Depression History  *(50 s)*

> "The most important slide of the presentation, because it nails RQ3 with the cleanest test.
>
> We re-trained the model after stripping out *every* depression-related feature — prior scores, missing-count, change feature. AUC drops from 0.848 to 0.773. The drop confirms that prior depression matters; we're not pretending otherwise.
>
> But 0.77 is still a clinically usable screening signal — and it's achieved using *no mental health features at all*. Just physical health, mobility, function, finances, demographics.
>
> What this means: depression risk leaves a measurable footprint in physical, functional, and economic data two to four years before symptoms emerge. A GP practice that already collects routine over-50 health-check data could deploy a model like this without any depression questionnaire — and still catch the majority of future cases."

---

## Slide 13 — Limitations  *(40 s)*

> "We are honest about the limits. CES-D ≥ 3 is a screening cutoff, not a diagnosis of MDD. The design is observational — we identify predictors, not causes. Attrition is real — about 30% of Wave 6 respondents are excluded because they didn't survive to Wave 8, and those people are likely the highest-risk. Precision sits around 49%, fine for screening, not for diagnosis.
>
> Generalisability has hard boundaries: validated only on the English population aged 50 and over, excludes institutionalised residents, and ELSA cohort effects are real. We have not yet evaluated fairness across sex, ethnicity, or SES — that would be the first thing to do before any deployment claim."

---

## Slide 14 — Future and Conclusion  *(45 s)*

> "Future directions: an incident-only model excluding already-depressed at baseline; external validation on US HRS, European SHARE, Irish TILDA; adding ELSA's nurse-visit blood biomarkers; trajectory models across multiple waves; a fairness audit; and a cost-effectiveness analysis with intervention data.
>
> Take-home messages: AUC 0.85 is clinically useful early prediction; combining waves beats one alone but a recent snapshot is nearly as good; non-mental-health features carry independent predictive signal.
>
> In one sentence: routine survey data can flag future depression with clinically useful accuracy two to four years in advance — even without using depression history at all. Thank you. Happy to take questions."

---

## Q&A preparation — five likely questions

**Q1: "Why didn't you use deep learning?"**
> "Tabular ELSA has 7,211 rows. Gradient-boosted trees consistently outperform deep nets at this scale on structured tabular data, and they give us interpretable SHAP attributions. Our soft-vote ensemble of RF, XGB, and LGBM tied with the best single model — the algorithms converge on the same patterns, no diversity bonus to exploit. The stacking ensemble with a logistic-regression meta-learner does shift the recall higher because the meta weights LightGBM more heavily."

**Q2: "How do you justify the 0.5 threshold?"**
> "We kept 0.5 for the cross-arm comparison so it stayed clean, then ran a separate threshold optimisation showing F1 peaks at about 0.58 — that's slide 9. In real deployment the threshold would be tuned to the operational point chosen by the commissioning healthcare body, balancing precision against recall against follow-up clinic capacity. We provide isotonic-calibrated probabilities specifically so the threshold is a deployment decision, not a modelling lock-in."

**Q3: "Isn't this just predicting that depressed people stay depressed?"**
> "Almost — and that's exactly why we ran the leakage sensitivity. Without any prior CES-D feature, the model still achieves AUC 0.77 versus 0.85 with it. Roughly half of the discriminative power comes from physical health, mobility, and socioeconomic features, not from depression history. The convergent evidence on slide 11 strengthens this — three independent interpretation methods plus a domain ablation all agree the non-mental-health signal is real."

**Q4: "What about anxiety, the other outcome the brief mentions?"**
> "ELSA does not contain a validated continuous anxiety scale across all three waves the way it does CES-D. We could have built an anxiety model on weaker measurement, but we judged it better to do depression well than depression and anxiety badly. Anxiety would be a clear extension."

**Q5: "Why Random Forest as the headline rather than XGBoost or LightGBM?"**
> "All three trees finished within 0.005 AUC of each other after tuning. We picked Random Forest as the headline because it has the most stable calibration after isotonic correction, the simplest hyperparameter footprint, and the cleanest SHAP visualisations. LightGBM did beat it on recall though, which is why our screening-deployment recommendation goes to the stacking ensemble that weights LightGBM heavily."

**Q6: "If domain ablation shows near-zero drops for everything except prior depression, isn't most of the model just CES-D?"**
> "No, and this is the key subtlety. Ablation measures *unique* contribution. Health, mobility, finance, and demographics share correlations of 0.4 to 0.5, so when one domain is removed the model reconstructs the signal from neighbours. The cleanest test is the leakage analysis — strip *all* of CES-D and the model still reaches 0.77, which is 91% of the full performance. Convergent SHAP, LR coefficients, and LGBM gain rankings confirm the non-CES-D predictors are doing real work."

---

## Timing scaffold (10-minute slot)

| Slide | Target | Cumulative |
|-------|--------|------------|
| 1 Title | 20 s | 0:20 |
| 2 Problem | 45 s | 1:05 |
| 3 RQs | 40 s | 1:45 |
| 4 ELSA dataset | 50 s | 2:35 |
| 5 Outcome | 40 s | 3:15 |
| 6 Pipeline | 50 s | 4:05 |
| 7 Experimental design | 40 s | 4:45 |
| 8 Results | 50 s | 5:35 |
| 9 Clinical deployment | 40 s | 6:15 |
| 10 SHAP | 40 s | 6:55 |
| 11 Robustness | 40 s | 7:35 |
| 12 Leakage | 50 s | 8:25 |
| 13 Limitations | 40 s | 9:05 |
| 14 Future + conclusion | 45 s | 9:50 |

If you go over, cut: slide 5's CES-D fix anecdote (one sentence), slide 13's generalisability list (one bullet), or pick **either** slide 9 calibration **or** stacking — both don't have to be said in detail; the slide carries the rest.
