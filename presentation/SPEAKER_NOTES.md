# Speaker Notes — ELSA Depression Prediction (10-minute version)

12 slides, target ~50 seconds per slide. Coursework brief allows 10 min + 5 min Q&A.

---

## Slide 1 — Title  *(20 s)*

> "Good afternoon. Our project asked one question: can we predict, today, whether an older adult will become depressed in two to four years' time using only routine survey data? We worked with the English Longitudinal Study of Ageing — and the answer is yes, with the surprising twist that we can do it even without using their depression history at all."

---

## Slide 2 — The Problem  *(50 s)*

> "Late-life depression is the WHO's quiet epidemic. Around 7% of adults over sixty have it; most are never diagnosed. Stigma, somatic presentation, and the time pressure on primary care all conspire to keep it invisible — and the consequences ripple into worse cardiovascular, dementia, and mortality outcomes.
>
> Universal screening of every over-50 is impractical. But ML offers a way out: routine over-50 data is *already* collected, and a model that flags the highest-risk people for clinician follow-up could change the screening economics. The key word is *early* — we need to predict before symptoms manifest, not after.
>
> So our project goal: predict depression onset 2 to 4 years ahead from data already in routine collection."

---

## Slide 3 — Research Questions  *(45 s)*

> "We locked three research questions before any modelling. RQ1 — can ML do this prediction at all from survey data? RQ2 — does combining waves help? RQ3 — and most importantly, what predicts depression *beyond* depression history itself?
>
> These map directly onto our experimental design. RQ2 is answered by running three prediction arms: Wave 6 alone, Wave 7 alone, and the two combined. RQ3 is answered by SHAP analysis and the leakage sensitivity test, which I'll get to."

---

## Slide 4 — The ELSA Dataset  *(60 s)*

> "ELSA is a representative panel of English adults aged 50 and over. The same individuals are tracked every two years, with the dataset spanning 2002 through 2023. Crucially, the 8-item CES-D depression scale is collected every wave.
>
> Akeeb's audit examined every available wave and answered three things: CES-D quality is excellent across all waves, between 93 and 97% valid responses; participant overlap exceeds 90% between consecutive waves; but feature drift is real — only 2,656 of 13,920 unique variables exist in every wave. Waves 6, 7, and 8 emerged as the strongest consecutive longitudinal block.
>
> The funnel at the bottom: we started with 10,601 Wave 6 respondents, intersected through Wave 7 and Wave 8, kept only those with a valid CES-D at the outcome wave, and ended with 7,211 participants. That's our analytic sample."

---

## Slide 5 — The Outcome Variable  *(50 s)*

> "Our binary label is CES-D ≥ 3 at Wave 8 — Steffick's standard cutoff for clinically significant depressive symptoms. Observed prevalence is 19%, exactly what the literature predicts for English adults over 50.
>
> Brief methodology note — and this is one of the lessons of the project. An earlier exploratory notebook reconstructed CES-D from raw items on a 0-3 scale, producing a 74% prevalence — clinically implausible. We caught it by checking against published prevalence and switched to the IFS-validated `cesd_sc` variable. Range corrected to 0-8, prevalence dropped to 19%, and the binary task became scientifically meaningful.
>
> The 80/20 imbalance is handled by class weighting in every model — no model is allowed to ignore the minority class."

---

## Slide 6 — The Pipeline  *(60 s)*

> "Six stages, all reproducible in a single Colab notebook. Load and merge the IFS, core, and financial files on the participant ID. Recode the survey missing codes — minus one, minus eight, minus nine — to NaN, then drop columns with more than 40% missing on a *training-only* estimate to avoid test-set leakage.
>
> Engineer ten longitudinal features. The most important is `cesd_change`, the change in depression score from Wave 6 to Wave 7 — that's what makes this a true longitudinal model rather than a static snapshot. We also build mobility, ADL, and IADL counts plus a combined functional burden score.
>
> Then a 75/25 stratified split, 5-fold stratified cross-validation on the training set, train four algorithms with class-weighted loss, tune the best feature configuration per arm with Randomized Search, and evaluate with the full battery: AUC, F1, recall, calibration, SHAP."

---

## Slide 7 — Experimental Design  *(50 s)*

> "Three prediction arms answer RQ2: Wave 6 alone is a roughly 4-year horizon, Wave 7 alone is roughly 2 years, and the combined model uses both plus our change features. Identical participant rows across all three arms — the comparison is clean.
>
> Within each arm, five feature configurations answer RQ3: full, no-prior-CES-D, health only, function and cognition only, and socioeconomic only. Three arms times five configs times four models gives sixty baseline experiments. The best feature configuration per arm is then handed to RandomizedSearchCV — fifty iterations, five-fold cross-validation on the training set — to tune Random Forest, XGBoost, and LightGBM. Logistic Regression is kept at its defaults as a fair interpretable baseline."

---

## Slide 8 — Headline Results  *(60 s)*

> "Our headline: the tuned Random Forest combining Wave 6 and Wave 7 achieves AUC 0.85 on the held-out test set. F1 for the depressed class is 0.58, recall is 71% — meaning we catch seven out of ten future depression cases.
>
> Cross-arm comparison answers RQ2. The Wave-7-only arm slightly beats Wave 6 alone — 0.824 versus 0.819 AUC — confirming the recent-snapshot intuition. But the combined model edges both at 0.848. The gain from combining waves is real, about 0.025 AUC, though smaller than we initially expected.
>
> The PR curve on the right is, frankly, more honest under 80/20 imbalance than the ROC. Average precision is around 0.55 — substantially better than the no-skill baseline of 0.19."

---

## Slide 9 — What Drives the Predictions  *(50 s)*

> "SHAP analysis on the full model shows what the algorithm is actually using. Prior CES-D scores at Wave 7 and Wave 6 dominate — that's expected, depression history is a strong predictor of future depression. But the next tier is informative: self-rated health, mobility count, the change in depression score, and financial difficulty.
>
> What this tells us is that late-life depression has a measurable biopsychosocial signature. Physical decline, mental health trajectory, and economic stress all show up as distinct predictive signals two to four years before symptoms emerge. This is consistent with the established gerontological literature on the biopsychosocial model of depression."

---

## Slide 10 — Beyond Depression History  *(60 s)*

> "Now the most important slide of the presentation, because it answers RQ3 and contains our central scientific finding.
>
> We re-trained the model after stripping out *every* depression-related feature — prior scores, missing-count, change feature. AUC drops from 0.848 to 0.773. That drop confirms that prior depression matters; we're not pretending otherwise.
>
> But 0.77 is still a clinically usable screening signal — and it's achieved using *no mental health features at all*. Just physical health, mobility, function, finances, and demographics.
>
> What this means in plain English: depression risk leaves a measurable footprint in physical, functional, and economic data two to four years before symptoms emerge. A GP practice that already collects routine over-50 health-check data could deploy a model like this without any depression questionnaire — and still catch the majority of future cases."

---

## Slide 11 — Limitations  *(45 s)*

> "We are honest about the limits. CES-D ≥ 3 is a screening cutoff, not a diagnosis of Major Depressive Disorder. The design is observational, so we identify predictors, not causes. Attrition is real — about 30% of Wave 6 respondents are excluded because they didn't survive to Wave 8, and those people are likely the highest-risk ones. Precision sits around 49%, which is fine for screening but not for diagnosis.
>
> Generalisability has hard boundaries. Our model is validated only on the English population aged 50 and over. It excludes institutionalised residents. ELSA's cohort effects mean today's 50-year-olds are not the 50-year-olds in our sample. And we have not yet evaluated fairness across sex, ethnicity, or socioeconomic strata — that would be the first thing to do before any deployment claim."

---

## Slide 12 — Future and Conclusion  *(50 s)*

> "Future directions: an incident-only model that excludes already-depressed people at baseline; external validation on the US Health and Retirement Study, the European SHARE cohort, and the Irish Longitudinal Study; adding ELSA's nurse-visit blood biomarkers; building proper trajectory models across multiple waves; a fairness audit; and a cost-effectiveness analysis with intervention efficacy data.
>
> But the take-home messages, summarising our three research questions: AUC 0.85 is clinically useful early prediction; combining waves beats one alone but a recent snapshot is nearly as good; and non-mental-health features carry independent predictive signal.
>
> In one sentence: routine survey data can flag future depression with clinically useful accuracy two to four years in advance — even without using depression history at all. Thank you. Happy to take questions."

---

## Q&A preparation — five likely questions

**Q1: "Why didn't you use deep learning?"**
> "Tabular ELSA has 7,211 rows. Gradient-boosted trees consistently outperform deep nets at this scale on structured tabular data, and they give us interpretable SHAP attributions. We did try an averaging ensemble of RF, XGB, and LGBM — it tied with the best single model, suggesting the algorithms are converging on the same patterns. There's no diversity bonus to exploit."

**Q2: "How do you justify the 0.5 threshold?"**
> "We deliberately kept the default 0.5 to make the cross-arm comparison clean. In real deployment the threshold would be tuned to the operational point chosen by the commissioning healthcare body, balancing precision against recall depending on follow-up clinic capacity. We provide calibrated probabilities specifically so the threshold is a deployment decision, not a modelling lock-in."

**Q3: "Isn't this just predicting that depressed people stay depressed?"**
> "Almost — and that's exactly why we ran the leakage sensitivity. Without any prior CES-D feature, the model still achieves AUC 0.77 versus 0.85 with it. Roughly half of the discriminative power comes from physical health, mobility, and socioeconomic features, not from depression history. That separation is the real scientific contribution of the project."

**Q4: "What about anxiety, the other outcome the brief mentions?"**
> "ELSA does not contain a validated continuous anxiety scale across all three waves we used the way it does CES-D. We could have built an anxiety model on weaker measurement, but we judged it better to do depression *well* than depression and anxiety badly. Anxiety would be a clear extension."

**Q5: "Why Random Forest as the headline rather than XGBoost or LightGBM?"**
> "All three trees performed within 0.005 AUC of each other after tuning. We picked Random Forest as the headline because it has the most stable calibration after isotonic correction, the simplest hyperparameter footprint, and the cleanest SHAP visualisations. Reporting one model rather than three keeps the presentation honest — they all tell the same story."

---

## Timing scaffold (10-minute slot)

| Slide | Target | Cumulative |
|-------|--------|------------|
| 1 Title | 20 s | 0:20 |
| 2 Problem | 50 s | 1:10 |
| 3 RQs | 45 s | 1:55 |
| 4 ELSA dataset | 60 s | 2:55 |
| 5 Outcome | 50 s | 3:45 |
| 6 Pipeline | 60 s | 4:45 |
| 7 Experimental design | 50 s | 5:35 |
| 8 Results | 60 s | 6:35 |
| 9 SHAP | 50 s | 7:25 |
| 10 Leakage | 60 s | 8:25 |
| 11 Limitations | 45 s | 9:10 |
| 12 Future + conclusion | 50 s | 10:00 |

If you find yourself going over, the most cuttable content is slide 5's CES-D fix anecdote (cut to one sentence) and slide 11's generalisability list (compress to one bullet).
