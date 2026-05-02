"""
Assemble the final submission package for SurreyLearn upload.

Run:    python3 submission/build_submission_package.py
Output: submission/ELSA_Depression_Prediction_Submission/   (folder)
        submission/ELSA_Depression_Prediction_Submission.zip (zipped bundle)

Idempotent — re-running cleans and rebuilds the staging folder.
"""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGE = ROOT / "submission" / "ELSA_Depression_Prediction_Submission"
ZIP_OUT = ROOT / "submission" / "ELSA_Depression_Prediction_Submission.zip"


# (source path relative to repo root, destination path relative to STAGE)
FILES = [
    # === Code (notebooks + supporting) ===
    ("submission/ELSA_Depression_Prediction.ipynb",
     "code/ELSA_Depression_Prediction.ipynb"),
    ("submission/ELSA_Depression_Prediction_Full.ipynb",
     "code/ELSA_Depression_Prediction_Full.ipynb"),
    ("submission/README.md",
     "code/README.md"),
    ("submission/requirements.txt",
     "code/requirements.txt"),

    # === Documents ===
    ("docs/ELSA_Depression_Prediction_Report.docx",
     "documents/ELSA_Depression_Prediction_Report.docx"),
    ("docs/REPORT.md",
     "documents/REPORT.md"),
    ("docs/team_contributions.md",
     "documents/team_contributions.md"),
    ("docs/Meeting_Minutes.docx",
     "documents/Meeting_Minutes.docx"),

    # === Presentation ===
    ("presentation/ELSA_Depression_Prediction.pptx",
     "presentation/ELSA_Depression_Prediction.pptx"),
    ("presentation/SPEAKER_NOTES.md",
     "presentation/SPEAKER_NOTES.md"),
    ("presentation/QA_FLASHCARDS.md",
     "presentation/QA_FLASHCARDS.md"),
]

TOP_README = """\
# ELSA Depression Prediction — Group 4 Submission

**Module:** AI and Healthcare (EEEM069) — University of Surrey
**MSc Artificial Intelligence (2025/26)**
**Group 4 — "Health is Wealth"**

Akeeb Lawel  |  Fiyin Akano  |  Zannat Chowdhury Sagar
Giridhar Nampally  |  Pushkar Jadhav  |  Poorna Golla

---

## Folder layout

| Folder | Contents |
|--------|----------|
| `code/` | The submission notebooks and dependencies |
| `documents/` | Project report, team contributions, meeting minutes |
| `presentation/` | 10-minute slide deck, speaker notes, Q&A flashcards |

---

## How to evaluate this submission

### 1. Read the report (5 min)
Open `documents/ELSA_Depression_Prediction_Report.docx`. The Executive Summary on page 1 gives the headline finding; the rest of the document is the full project narrative.

### 2. Run the code (10–15 min on Colab)

The lecturer-facing notebook is `code/ELSA_Depression_Prediction.ipynb`.

1. Upload it to Google Colab.
2. Make the ELSA UKDA-5050 Stata folder accessible (Drive mount or direct upload).
3. Edit the **`ELSA_PATH`** variable in **Section 0** to point at the `stata13_se` folder.
4. **Runtime → Run all** (`Cmd/Ctrl + F9`).
5. Read the inline interpretation paragraphs as you go — every result is followed by an explanation.

A more elaborate appendix notebook (`code/ELSA_Depression_Prediction_Full.ipynb`) runs the complete experimental sweep (3 prediction arms × 5 feature configurations × 4 models = 60 baseline experiments + hyperparameter tuning + calibration + ensemble) for evaluators who want the full sweep. Recommended only if you have 30+ minutes.

### 3. Watch the presentation (10 min)

The slide deck is `presentation/ELSA_Depression_Prediction.pptx` (12 slides, designed for a 10-minute slot).

`presentation/SPEAKER_NOTES.md` contains the timed presenter scripts. `presentation/QA_FLASHCARDS.md` is the Q&A preparation pack.

---

## Headline result (one-line summary)

The best machine-learning model trained on Wave 6 + Wave 7 ELSA features predicts Wave 8 depression (CES-D ≥ 3) with **ROC-AUC 0.85** and **71% recall** — and even after stripping out every depression-history feature, the model still achieves **AUC 0.77** using only physical health, mobility, finances, and demographics.

This is the central scientific finding: **depression risk leaves a measurable footprint in non-mental-health data 2–4 years before symptoms emerge.**

---

## Coursework deliverable mapping

| Marking criterion | Where to find it |
|-------------------|------------------|
| Background description | Report §2 + Slide 2 |
| Data analysis pipeline + rationale | Report §5 + Slides 4–7 + Notebook §§ 1–6 |
| Results and prediction analysis | Report §6 + Slides 8–10 + Notebook §§ 7–9 |
| Limitations and future direction | Report §§8–9 + Slides 11–12 |
| Code + README | `code/` folder |
| Presentation slides | `presentation/` folder |
| Team member roles document | `documents/team_contributions.md` |
| Meeting minutes | `documents/Meeting_Minutes.docx` |

---

*Submitted: see SurreyLearn submission timestamp.*
"""


def stage():
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)

    missing = []
    for src_rel, dst_rel in FILES:
        src = ROOT / src_rel
        dst = STAGE / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not src.exists():
            missing.append(src_rel)
            continue
        shutil.copy2(src, dst)
        print(f"  + {dst_rel}")

    # Top-level README
    (STAGE / "README.md").write_text(TOP_README, encoding="utf-8")
    print(f"  + README.md")

    if missing:
        print()
        print("WARNING — missing source files:")
        for m in missing:
            print(f"    {m}")


def zip_bundle():
    if ZIP_OUT.exists():
        ZIP_OUT.unlink()
    with zipfile.ZipFile(ZIP_OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in STAGE.rglob("*"):
            if path.is_file():
                zf.write(path, arcname=path.relative_to(STAGE.parent))
    size_kb = ZIP_OUT.stat().st_size // 1024
    print(f"\nZipped: {ZIP_OUT.name}  ({size_kb} KB)")


def main():
    print(f"Staging at: {STAGE}\n")
    stage()
    print()
    zip_bundle()
    print(f"\n\u2713 Submission package ready: {STAGE.relative_to(ROOT)}")
    print(f"  Top-level zip:         {ZIP_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
