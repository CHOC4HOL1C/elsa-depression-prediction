# Predicting Depression in Older Adults Using ELSA Longitudinal Data

## Overview

This is a group project for the MSc Artificial Intelligence programme at the University of Surrey (2025–2026). The project applies machine learning techniques to longitudinal survey data from the English Longitudinal Study of Ageing (ELSA) to predict depression outcomes in older adults, using the CES-D (Center for Epidemiologic Studies Depression Scale) as the primary outcome measure.

Waves 6, 7, and 8 of the ELSA dataset are used to examine temporal patterns and build predictive models that could support early identification of depression risk in older populations.

## Dataset

**English Longitudinal Study of Ageing (ELSA)**
- Waves used: Wave 6 (2012–13), Wave 7 (2014–15), Wave 8 (2016–17)
- Outcome variable: CES-D score / depression classification
- Access: Data obtained under the UK Data Service data use agreement

> **Important:** Raw ELSA data files (`.dta`, `.csv`, `.xlsx`) must **never** be committed to this repository. See `.gitignore` and the data use agreement for details.

## Project Structure

```
elsa-depression-prediction/
├── data/                        # Raw and processed data (gitignored)
├── notebooks/
│   ├── 01_data_audit/           # Explore wave structure, missingness, variables
│   ├── 02_data_loading/         # Load and merge waves
│   ├── 03_preprocessing/        # Cleaning, imputation, encoding
│   ├── 04_feature_engineering/  # Feature selection and construction
│   ├── 05_modelling/            # Train ML models
│   └── 06_evaluation/           # Evaluate, compare, interpret models
├── outputs/
│   ├── figures/                 # Saved plots and visualisations
│   └── results/                 # Model outputs, metrics, tables
├── docs/
│   ├── meeting_minutes/         # Notes from team meetings
│   └── team_contributions.md    # Member roles and contributions
└── requirements.txt
```

## How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/CHOC4HOL1C/elsa-depression-prediction.git
   cd elsa-depression-prediction
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Place ELSA data files in the `data/` directory (not committed to git).

4. Run notebooks in order, starting with `01_data_audit/`.

## Team Contributions

See [docs/team_contributions.md](docs/team_contributions.md) for a full breakdown of member roles and responsibilities.

## Team Members

| Name | GitHub |
|------|--------|
| Zannat Chowdhury Sagar | [@CHOC4HOL1C](https://github.com/CHOC4HOL1C) |
| Akeeb Lawel | [TEAMMATE_GITHUB_USERNAME] |
| Fiyin Akano | [TEAMMATE_GITHUB_USERNAME] |
| Giridhar Nampally | [TEAMMATE_GITHUB_USERNAME] |
| Pushkar Jadav | [TEAMMATE_GITHUB_USERNAME] |
| Poorna Golla | [TEAMMATE_GITHUB_USERNAME] |

**University of Surrey — MSc Artificial Intelligence, 2025–2026**

## Requirements

See [requirements.txt](requirements.txt) for the full list of Python dependencies.
