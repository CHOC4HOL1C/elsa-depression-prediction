# Speaker Notes — ELSA Depression Prediction (5-minute version)

7 slides, target ~40 seconds per slide. Pad gracefully to 10 minutes by going deeper on slides 4 and 5.

---

## Slide 1 — Title  *(20 s)*

> "Good afternoon. Our project asked a single question: can we predict, today, whether an older adult will become depressed in two to four years' time using only routine survey data? We worked with the English Longitudinal Study of Ageing — and the answer is yes, and even more interestingly, we can do it without using their depression history at all."

---

## Slide 2 — The Problem and the Question  *(45 s)*

> "Depression in older adults is the WHO's silent epidemic. About one in fourteen adults over sixty lives with it; most never get diagnosed. Stigma, somatic presentation, and the time pressure on primary care all conspire to keep it invisible. Routine universal screening is impractical — but a model that flags the highest-risk people for a clinical follow-up could change that economics.
>
> So we set ourselves three questions. RQ1 — can ML do this prediction at all from survey data? RQ2 — does combining waves help? RQ3 — and most importantly, what predicts depression *beyond* depression history itself?"

---

## Slide 3 — Data and Pipeline  *(50 s)*

> "ELSA tracks the same 50-plus English adults every two years since 2002. Akeeb's audit showed Waves 6, 7, and 8 are the strongest consecutive block — over 90% of participants overlap, and the depression scale, CES-D, has 95% completeness in all waves. After inner-joining on participant ID we had 7,211 people in our analytic sample. Prevalence sits at 19%, exactly what the literature predicts.
>
> Our pipeline runs end-to-end in a single Colab notebook. We recode survey missing codes, drop high-missingness columns using only the training set, engineer ten clinically meaningful features — most importantly the *change* in depression score from Wave 6 to Wave 7, which is what makes this a longitudinal model. We compared four algorithms across three time horizons and five feature configurations — sixty experiments in total before we even started tuning."

> *(If asked about the methodological note)*: "We caught a bug early — an exploratory notebook had reconstructed CES-D from raw items on a wrong scale, producing 74% prevalence. Switching to the IFS-validated derived variable fixed it."

---

## Slide 4 — Results  *(50 s)*

> "Our headline finding: the tuned Random Forest combining Wave 6 and Wave 7 achieves an AUC of 0.85 on the held-out test set. F1 for the depressed class is 0.58, recall is 71% — meaning we catch seven out of every ten future depression cases.
>
> Cross-arm comparison answers RQ2: combining waves beats either alone, but only by about 0.025 AUC. The Wave-7-only model is essentially as good as the combined model when used as a 2-year-horizon screen. That's actually a useful clinical finding — it tells us the prediction is robust to having only one recent snapshot."

---

## Slide 5 — Interpretation  *(50 s)*

> "When we look inside the model with SHAP, prior depression scores dominate — that's expected and unsurprising. But the next tier is fascinating: self-rated health, mobility difficulty, change in depression score, and financial difficulty. The model is picking up the biopsychosocial pattern of late-life depression: people whose bodies are failing, whose finances are stressed, whose mobility is declining are at meaningfully higher risk."

---

## Slide 6 — Beyond depression history  *(50 s)*

> "Now the most important slide. We re-trained the model after stripping out *every* depression-related feature. AUC drops from 0.85 to 0.77. That drop confirms prior depression matters. But 0.77 is still a usable screening signal — and crucially, this AUC is achieved using only physical health, mobility, finances, and demographics.
>
> What this means: depression leaves a measurable footprint in non-mental-health data two to four years before symptoms emerge. That is the clinical novelty here. A GP practice that already collects routine over-50 health-check data could deploy a model like this without any depression questionnaire — and still catch the majority of future cases."

---

## Slide 7 — Limitations and future  *(45 s)*

> "We are honest about the limits. CES-D ≥ 3 is a screening cutoff, not a diagnosis. The design is observational, so we identify predictors, not causes. Attrition is real — about 30% of Wave 6 respondents are excluded because they didn't survive to Wave 8, and those people are likely the highest-risk ones. Precision is modest at 49%, which is fine for screening but not for diagnosis.
>
> Future work: external validation on HRS, SHARE, and TILDA cohorts; adding the ELSA nurse-visit biomarkers; subgroup fairness analysis; and a cost-effectiveness model linking model outputs to intervention efficacy.
>
> The bottom line: routine survey data can flag future depression with clinically useful accuracy two to four years in advance. Thank you — happy to take questions."

---

## Q&A preparation — three likely hard questions

**Q1: "Why didn't you use deep learning?"**
> "Tabular ELSA has 7,211 rows. Gradient-boosted trees (LightGBM, XGBoost) consistently outperform deep nets on this scale of structured tabular data, and they give us interpretable feature attributions through SHAP. We did try an ensemble — it tied with the best single model, suggesting all three trees are learning the same patterns."

**Q2: "How do you justify the 0.5 threshold?"**
> "We didn't optimise the threshold to maximise F1 — we kept 0.5 to keep the comparison clean. In a real deployment, the threshold would be tuned to the operational point chosen by the commissioning healthcare body, balancing precision against recall depending on follow-up capacity."

**Q3: "Isn't this just predicting that depressed people stay depressed?"**
> "Almost — and that's exactly why we ran the leakage sensitivity. Without any prior CES-D feature, the model still achieves AUC 0.77. Half of the discriminative power comes from physical health, mobility, and socioeconomic features, not from depression history. That is the real scientific contribution of the project."

**Q4: "What about anxiety, the other outcome the brief mentions?"**
> "ELSA does not contain a validated continuous anxiety scale across waves 6, 7, 8 the way it does CES-D. Adding anxiety would have meant much weaker measurement; we chose to do depression well rather than depression and anxiety badly."

---

## Timing scaffold

| Slide | Target | Cumulative |
|-------|--------|------------|
| 1 Title | 20 s | 0:20 |
| 2 Problem | 45 s | 1:05 |
| 3 Data + Pipeline | 50 s | 1:55 |
| 4 Results | 50 s | 2:45 |
| 5 SHAP | 50 s | 3:35 |
| 6 Leakage | 50 s | 4:25 |
| 7 Limitations | 45 s | 5:10 |

If the slot is 10 minutes, double the time on slides 3-6 and add a deeper walk-through of one specific case. Slides 1 and 2 should stay tight regardless.
