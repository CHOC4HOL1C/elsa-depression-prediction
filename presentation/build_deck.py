"""
Build the ELSA Depression Prediction 5-minute presentation deck.

Run:  python3 presentation/build_deck.py
Outputs: presentation/ELSA_Depression_Prediction.pptx
"""
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "outputs" / "figures"
OUT = ROOT / "presentation" / "ELSA_Depression_Prediction.pptx"

# ── Style palette ──────────────────────────────────────────────────────────
NAVY   = RGBColor(0x1F, 0x2D, 0x5C)
TEAL   = RGBColor(0x18, 0x6F, 0x82)
CORAL  = RGBColor(0xE5, 0x6B, 0x5C)
GREY   = RGBColor(0x55, 0x5C, 0x66)
LIGHT  = RGBColor(0xF4, 0xF5, 0xF7)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)

# ── Helpers ─────────────────────────────────────────────────────────────────
prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)

BLANK = prs.slide_layouts[6]


def add_rect(slide, left, top, width, height, fill, line=None):
    from pptx.enum.shapes import MSO_SHAPE
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background() if line is None else None
    if line is None:
        shape.line.fill.background()
    return shape


def add_text(slide, left, top, width, height, text,
             size=18, bold=False, color=NAVY, align=PP_ALIGN.LEFT,
             font="Calibri"):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font
    return tb


def add_bullets(slide, left, top, width, height, bullets,
                size=16, color=NAVY, bold_first=False, spacing=6):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(spacing)
        # Optional bold-prefix syntax: "**Title** rest of bullet"
        if "**" in b:
            parts = b.split("**")
            for j, part in enumerate(parts):
                if not part:
                    continue
                run = p.add_run()
                run.text = part
                run.font.size = Pt(size)
                run.font.color.rgb = color
                run.font.name = "Calibri"
                run.font.bold = (j % 2 == 1)
        else:
            run = p.add_run()
            run.text = "• " + b
            run.font.size = Pt(size)
            run.font.color.rgb = color
            run.font.name = "Calibri"
    return tb


def add_image(slide, path, left, top, width=None, height=None):
    if width and height:
        return slide.shapes.add_picture(str(path), left, top, width=width, height=height)
    if width:
        return slide.shapes.add_picture(str(path), left, top, width=width)
    if height:
        return slide.shapes.add_picture(str(path), left, top, height=height)
    return slide.shapes.add_picture(str(path), left, top)


def add_header(slide, title, subtitle=None):
    # Top accent bar
    add_rect(slide, 0, 0, prs.slide_width, Inches(0.12), NAVY)
    # Title
    add_text(slide, Inches(0.5), Inches(0.25), Inches(12.5), Inches(0.7),
             title, size=30, bold=True, color=NAVY)
    if subtitle:
        add_text(slide, Inches(0.5), Inches(0.85), Inches(12.5), Inches(0.4),
                 subtitle, size=15, color=GREY)


def add_footer(slide, page_num, total=7):
    add_text(slide, Inches(0.5), Inches(7.10), Inches(7),
             Inches(0.3),
             "ELSA Depression Prediction  |  AI & Healthcare  |  University of Surrey  2025/26",
             size=10, color=GREY)
    add_text(slide, Inches(11.5), Inches(7.10), Inches(1.5), Inches(0.3),
             f"{page_num} / {total}",
             size=10, color=GREY, align=PP_ALIGN.RIGHT)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 1 — Title
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
# Full-bleed navy
add_rect(s, 0, 0, prs.slide_width, prs.slide_height, NAVY)
# Side accent
add_rect(s, 0, 0, Inches(0.4), prs.slide_height, CORAL)

add_text(s, Inches(0.9), Inches(2.2), Inches(11), Inches(0.7),
         "Predicting Depression in Older Adults",
         size=44, bold=True, color=WHITE)
add_text(s, Inches(0.9), Inches(3.0), Inches(11), Inches(0.6),
         "Early prediction from 4 years out using ELSA longitudinal data",
         size=22, color=WHITE)

add_text(s, Inches(0.9), Inches(4.2), Inches(11), Inches(0.4),
         "Akeeb Lawel  |  Fiyin Akano  |  Zannat Chowdhury Sagar",
         size=16, color=WHITE)
add_text(s, Inches(0.9), Inches(4.55), Inches(11), Inches(0.4),
         "Giridhar Nampally  |  Pushkar Jadav  |  Poorna Golla",
         size=16, color=WHITE)
add_text(s, Inches(0.9), Inches(5.4), Inches(11), Inches(0.4),
         "MSc Artificial Intelligence  •  AI and Healthcare  •  2025/26",
         size=14, color=LIGHT)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 2 — The Problem and the Question
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, prs.slide_width, prs.slide_height, WHITE)
add_header(s, "The Problem", "Depression in older adults is underdiagnosed and undertreated")

# Left column — clinical context
add_text(s, Inches(0.5), Inches(1.4), Inches(6), Inches(0.4),
         "Why this matters", size=18, bold=True, color=TEAL)
add_bullets(s, Inches(0.5), Inches(1.85), Inches(6), Inches(3.5), [
    "**WHO**: 7% of adults over 60 globally have depression",
    "Most never receive a diagnosis or treatment",
    "Stigma, somatic presentation, comorbidity, time-poor primary care",
    "Linked to worse outcomes in CVD, dementia, and mortality",
    "Routine screening is impractical at population scale",
], size=15, spacing=8)

# Right column — our research questions
add_text(s, Inches(7.0), Inches(1.4), Inches(6), Inches(0.4),
         "Our research questions", size=18, bold=True, color=CORAL)
add_bullets(s, Inches(7.0), Inches(1.85), Inches(6), Inches(3.5), [
    "**RQ1**  Can ML predict depression onset 2 to 4 years ahead from survey data?",
    "**RQ2**  Does longitudinal data beat single-wave models?",
    "**RQ3**  What predicts depression beyond prior depression history?",
], size=15, spacing=12)

# Bottom callout
add_rect(s, Inches(0.5), Inches(5.8), Inches(12.3), Inches(0.95), LIGHT)
add_text(s, Inches(0.7), Inches(5.92), Inches(12), Inches(0.4),
         "Approach", size=14, bold=True, color=NAVY)
add_text(s, Inches(0.7), Inches(6.25), Inches(12), Inches(0.5),
         "Train models on Wave 6 + Wave 7 ELSA features to predict CES-D \u2265 3 at Wave 8.",
         size=15, color=GREY)
add_footer(s, 2)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3 — Data and Pipeline
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_header(s, "Data and Pipeline",
           "ELSA Waves 6, 7, 8 \u2014 7,211 participants present in all three waves")

# Top metric strip
metric_top = Inches(1.4)
metric_h = Inches(1.05)
labels = [("7,211", "Participants"),
          ("19.0%", "Depression prevalence"),
          ("138", "W6+W7 features"),
          ("4 algorithms", "LR, RF, XGB, LGBM"),
          ("3 arms × 5 configs", "60 experiments")]
xs = [Inches(0.5 + i * 2.55) for i in range(5)]
for (val, lab), x in zip(labels, xs):
    add_rect(s, x, metric_top, Inches(2.45), metric_h, LIGHT)
    add_text(s, x, metric_top + Inches(0.10), Inches(2.45), Inches(0.5),
             val, size=20, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    add_text(s, x, metric_top + Inches(0.62), Inches(2.45), Inches(0.4),
             lab, size=11, color=GREY, align=PP_ALIGN.CENTER)

# Outcome figure
add_image(s, FIG / "outcome_distribution.png",
          Inches(0.5), Inches(2.75), width=Inches(7.6))

# Right side — pipeline summary
add_text(s, Inches(8.5), Inches(2.85), Inches(4.5), Inches(0.4),
         "Pipeline (run-once Colab notebook)", size=14, bold=True, color=TEAL)
add_bullets(s, Inches(8.5), Inches(3.30), Inches(4.6), Inches(3.5), [
    "Inner-join W6+W7+W8 on idauniq",
    "Recode survey codes (-1, -8, -9 \u2192 NaN)",
    "Drop >40% missing (train-only)",
    "Engineer 10 derived features inc. CES-D change",
    "75/25 stratified split, 5-fold CV",
    "RandomizedSearchCV tuning",
    "Calibration via isotonic regression",
], size=13, spacing=4)

# Note on CES-D fix
add_rect(s, Inches(0.5), Inches(6.3), Inches(12.3), Inches(0.65), LIGHT)
add_text(s, Inches(0.7), Inches(6.40), Inches(12), Inches(0.4),
         "Methodological note  \u2014  Use IFS-validated cesd_sc (range 0\u20138, prevalence 19%); raw PSced reconstruction produced an artefactual range of 8\u201316 (74%)",
         size=11, color=GREY)
add_footer(s, 3)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4 — Results
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_header(s, "Results",
           "Random Forest combining W6+W7 \u2014 AUC 0.85 on held-out test set")

# Left: ROC curves
add_image(s, FIG / "roc_curves.png",
          Inches(0.5), Inches(1.5), height=Inches(3.7))

# Right: PR curves
add_image(s, FIG / "pr_curves.png",
          Inches(6.7), Inches(1.5), height=Inches(3.7))

# Bottom strip — headline numbers
band_top = Inches(5.5)
add_rect(s, Inches(0.5), band_top, Inches(12.3), Inches(1.55), LIGHT)
add_text(s, Inches(0.7), band_top + Inches(0.08), Inches(12), Inches(0.4),
         "Best tuned model per arm", size=14, bold=True, color=NAVY)

cols = [
    ("W6 only (~4 yr)", "AUC 0.819", "F1 0.532  Recall 0.732"),
    ("W7 only (~2 yr)", "AUC 0.824", "F1 0.545  Recall 0.668"),
    ("W6+W7 combined", "AUC 0.848", "F1 0.582  Recall 0.714"),
]
col_w = Inches(4.0)
for i, (head, auc, rest) in enumerate(cols):
    cx = Inches(0.7 + i * 4.05)
    color = NAVY if i < 2 else CORAL
    add_text(s, cx, band_top + Inches(0.5), col_w, Inches(0.4),
             head, size=13, bold=True, color=color)
    add_text(s, cx, band_top + Inches(0.85), col_w, Inches(0.4),
             auc, size=18, bold=True, color=color)
    add_text(s, cx, band_top + Inches(1.20), col_w, Inches(0.3),
             rest, size=11, color=GREY)
add_footer(s, 4)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 5 — Interpretation: SHAP Two-Act Narrative
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_header(s, "What drives the model?",
           "SHAP analysis reveals depression's biopsychosocial footprint")

# Left: SHAP figure (this is the ranked feature view)
add_image(s, FIG / "shap_bar_rf.png",
          Inches(0.5), Inches(1.4), height=Inches(5.2))

# Right column — interpretation
add_text(s, Inches(7.5), Inches(1.4), Inches(5.6), Inches(0.4),
         "Top predictors", size=18, bold=True, color=TEAL)
add_bullets(s, Inches(7.5), Inches(1.85), Inches(5.6), Inches(2.5), [
    "**Prior CES-D**  state dependence",
    "**Self-rated health**  subjective vitality",
    "**Mobility count**  physical function",
    "**CES-D change**  worsening trajectory",
    "**Financial difficulty**  socioeconomic strain",
], size=14, spacing=6)

add_text(s, Inches(7.5), Inches(4.30), Inches(5.6), Inches(0.4),
         "Why this matters", size=18, bold=True, color=CORAL)
add_bullets(s, Inches(7.5), Inches(4.75), Inches(5.6), Inches(2.5), [
    "Depression leaves a measurable footprint in physical health and finances",
    "Aligns with biopsychosocial model of late-life depression",
    "Non-mental-health features carry independent signal",
], size=13, spacing=5)
add_footer(s, 5)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 6 — Leakage Sensitivity (the central scientific claim)
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_header(s, "Beyond depression history",
           "Even without prior CES-D, the model still predicts well")

# Left: leakage figure
add_image(s, FIG / "leakage_sensitivity.png",
          Inches(0.5), Inches(1.5), height=Inches(4.0))

# Right: explanation
add_text(s, Inches(7.5), Inches(1.5), Inches(5.6), Inches(0.4),
         "The leakage test", size=18, bold=True, color=TEAL)
add_bullets(s, Inches(7.5), Inches(1.95), Inches(5.6), Inches(2.5), [
    "Drop every CES-D feature; retrain",
    "Tests: is the model just \"depressed people stay depressed\"?",
], size=14, spacing=6)

add_text(s, Inches(7.5), Inches(3.55), Inches(5.6), Inches(0.4),
         "What we found", size=18, bold=True, color=CORAL)
add_bullets(s, Inches(7.5), Inches(4.00), Inches(5.6), Inches(2.5), [
    "**AUC 0.85 \u2192 0.77** with no prior CES-D",
    "Drop is real (\u20070.07) but model still useful",
    "Health, mobility, finances carry independent signal",
    "Clinical novelty: predict from non-mental-health data",
], size=13, spacing=5)

# Bottom takeaway band
add_rect(s, Inches(0.5), Inches(6.0), Inches(12.3), Inches(0.95), NAVY)
add_text(s, Inches(0.7), Inches(6.10), Inches(12), Inches(0.4),
         "Headline finding", size=12, bold=True, color=CORAL)
add_text(s, Inches(0.7), Inches(6.45), Inches(12), Inches(0.5),
         "Depression risk is detectable from physical health and social factors alone \u2014 a viable population-screening signal.",
         size=14, color=WHITE)
add_footer(s, 6)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 7 — Limitations and Future Directions
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_header(s, "Limitations and future directions",
           "Where the model can and cannot be trusted")

# Two columns
add_text(s, Inches(0.5), Inches(1.5), Inches(6), Inches(0.4),
         "Limitations", size=18, bold=True, color=CORAL)
add_bullets(s, Inches(0.5), Inches(1.95), Inches(6), Inches(4.5), [
    "**Screening, not diagnosis**  CES-D \u2265 3 flags symptoms, not MDD",
    "**Observational design**  associations, not causes",
    "**Attrition bias**  ~30% of W6 sample excluded; likely sicker",
    "**State dependence**  prior CES-D dominates the full model",
    "**Generalisability**  English 50+ population only",
    "**Precision \u2248 49%**  ~half of flagged are false positives",
], size=13, spacing=6)

add_text(s, Inches(7.0), Inches(1.5), Inches(6), Inches(0.4),
         "Future directions", size=18, bold=True, color=TEAL)
add_bullets(s, Inches(7.0), Inches(1.95), Inches(6), Inches(4.5), [
    "**Incident-only model**  exclude already-depressed at baseline",
    "**External validation**  HRS (US), SHARE (EU), TILDA (Ireland)",
    "**Biomarkers**  add ELSA nurse-visit blood data",
    "**Trajectory models**  RNNs across multiple waves",
    "**Fairness audit**  calibration across sex, ethnicity, SES",
    "**Cost-effectiveness**  QALY analysis with intervention data",
], size=13, spacing=6)

# Bottom conclusion band
add_rect(s, Inches(0.5), Inches(6.05), Inches(12.3), Inches(0.95), LIGHT)
add_text(s, Inches(0.7), Inches(6.15), Inches(12), Inches(0.4),
         "Conclusion", size=14, bold=True, color=NAVY)
add_text(s, Inches(0.7), Inches(6.50), Inches(12), Inches(0.5),
         "Routine survey data can flag future depression with clinically useful accuracy 2-4 years in advance.",
         size=14, color=GREY)
add_footer(s, 7)


# ─────────────────────────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────────────────────────
OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(str(OUT))
print(f"Saved deck: {OUT}")
print(f"Slide count: {len(prs.slides)}")
