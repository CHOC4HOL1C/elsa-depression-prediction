# Project Context for Claude Code

## Project
MSc AI & Healthcare — ELSA Depression Prediction  
University of Surrey, 2025-2026  
Group: Zannat, Akeeb, Fiyin, Giridhar, Pushkar, Poorna

## Goal
Predict depression (CES-D ≥ 3) at Wave 8 using Wave 6 and 7 features from ELSA.
Secondary: lightweight trajectory clustering (k-means on CES-D sequences) as background.

## Waves
6, 7, 8 — core interview data + IFS derived variables

## Target variable
CES-D binary label: cesd_sc ≥ 3 = depressed (from IFS derived files)
Individual items PScedA–PScedH from core wave files for label construction and missingness checks.

## Key feature groups (confirmed from data dictionaries)
### From IFS derived files (wave_X_ifs_derived_variables.dta):
- Demographics: age, sex, nonwhite, marstat, couple, died_p
- Self-rated health: srh_hrs, llsill, hlimwrk
- Mobility (sum to mobility_count): hemobwa/si/ch/cs/cl/st/re/pu/li/pi
- ADL (sum to adl_count): headldr/wa/ba/ea/be/wc
- IADL (sum to iadl_count): headlma/da/pr/sh/ph/co/me/ho/mo
- Cognitive: memtotb, execnn, numtype4
- Employment: ecpos, worktime
- Education: qual3
- Financial subjective: findiff, ndepriv, lackresb
- Social/housing: famtype, tenure, nsibs, ngrandch
- Lifestyle: smokerstat
- CES-D: cesd_sc, cesd_na

### From financial derived files (wave_X_financial_derived_variables.dta):
- Income quintile: yq5_bu_s
- Wealth quintile: totwq5_bu_s

### From core wave files (wave_X_elsa_data.dta) — to be added later:
- Physical activity, alcohol, social participation, chronic conditions, sleep

## File naming (ELSA dataset, never commit these)
Core:      wave_6_elsa_data_v2.dta / wave_7_elsa_data.dta / wave_8_elsa_data_eul_v2.dta
IFS:       wave_6_ifs_derived_variables.dta (same pattern for 7, 8)
Financial: wave_6_financial_derived_variables.dta (same pattern for 7, 8)

## Notebook pipeline
01_data_audit/        — Akeeb's audit (done)
02_data_loading/      — THIS NOTEBOOK: load, merge, export clean panel
03_preprocessing/     — imputation, encoding, scaling
04_feature_engineering/ — delta features, derived counts
05_modelling/         — Logistic Regression, RF, XGBoost
06_evaluation/        — AUC-ROC, F1, SHAP

## Environment
See environment.yml and requirements.txt in repo root.
Data path handled via config.py — set DATA_ROOT for your runtime.
Never hardcode paths. Never commit .dta files.