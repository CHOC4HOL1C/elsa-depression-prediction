"""
Build the ELSA Depression Prediction 10-minute presentation deck.

Run:  python3 presentation/build_deck.py
Outputs: presentation/ELSA_Depression_Prediction.pptx

12 slides, ~50 seconds per slide for a 10-minute slot
(plus 5 minutes for Q&A as per coursework brief).
"""
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "outputs" / "figures"
OUT = ROOT / "presentation" / "ELSA_Depression_Prediction.pptx"

# ── Style palette ──────────────────────────────────────────────────────────
NAVY   = RGBColor(0x1F, 0x2D, 0x5C)
TEAL   = RGBColor(0x18, 0x6F, 0x82)
CORAL  = RGBColor(0xE5, 0x6B, 0x5C)
AMBER  = RGBColor(0xE0, 0xA3, 0x2A)
GREEN  = RGBColor(0x2E, 0x8B, 0x57)
GREY   = RGBColor(0x55, 0x5C, 0x66)
LIGHT  = RGBColor(0xF4, 0xF5, 0xF7)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)

# ── Helpers ─────────────────────────────────────────────────────────────────
prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)

BLANK = prs.slide_layouts[6]
TOTAL = 12  # we update this at the end after we count slides


def add_rect(slide, left, top, width, height, fill):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
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
                size=16, color=NAVY, spacing=6):
    """Bullets accept a **bold** prefix syntax: '**Title** rest'."""
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(spacing)
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
            run.text = "\u2022 " + b
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
    add_rect(slide, 0, 0, prs.slide_width, Inches(0.12), NAVY)
    add_text(slide, Inches(0.5), Inches(0.20), Inches(12.5), Inches(0.7),
             title, size=30, bold=True, color=NAVY)
    if subtitle:
        add_text(slide, Inches(0.5), Inches(0.78), Inches(12.5), Inches(0.4),
                 subtitle, size=15, color=GREY)


def add_footer(slide, page_num):
    add_text(slide, Inches(0.5), Inches(7.10), Inches(8), Inches(0.3),
             "ELSA Depression Prediction  |  AI & Healthcare  |  University of Surrey  2025/26",
             size=10, color=GREY)
    add_text(slide, Inches(11.5), Inches(7.10), Inches(1.5), Inches(0.3),
             f"{page_num} / {TOTAL}", size=10, color=GREY, align=PP_ALIGN.RIGHT)


def section_band(slide, top, text, accent=NAVY, height_in=0.95, body_color=GREY,
                 body_size=14, label="Takeaway"):
    add_rect(slide, Inches(0.5), top, Inches(12.3), Inches(height_in), LIGHT)
    add_text(slide, Inches(0.7), top + Inches(0.10), Inches(12), Inches(0.4),
             label, size=12, bold=True, color=accent)
    add_text(slide, Inches(0.7), top + Inches(0.42), Inches(12), Inches(0.5),
             text, size=body_size, color=body_color)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 1 — Title
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, prs.slide_width, prs.slide_height, NAVY)
add_rect(s, 0, 0, Inches(0.4), prs.slide_height, CORAL)

add_text(s, Inches(0.9), Inches(2.0), Inches(11), Inches(0.7),
         "Predicting Depression in Older Adults",
         size=44, bold=True, color=WHITE)
add_text(s, Inches(0.9), Inches(2.85), Inches(11), Inches(0.6),
         "Early prediction from 4 years out using ELSA longitudinal data",
         size=22, color=WHITE)

add_text(s, Inches(0.9), Inches(4.2), Inches(11), Inches(0.4),
         "Akeeb Lawel  \u2022  Fiyin Akano  \u2022  Zannat Chowdhury Sagar",
         size=16, color=WHITE)
add_text(s, Inches(0.9), Inches(4.55), Inches(11), Inches(0.4),
         "Giridhar Nampally  \u2022  Pushkar Jadav  \u2022  Poorna Golla",
         size=16, color=WHITE)
add_text(s, Inches(0.9), Inches(5.6), Inches(11), Inches(0.4),
         "MSc Artificial Intelligence  \u2022  AI and Healthcare  \u2022  2025/26",
         size=14, color=LIGHT)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 2 — The Problem
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_header(s, "The Problem",
           "Late-life depression: prevalent, disabling, and largely invisible")

add_text(s, Inches(0.5), Inches(1.4), Inches(6), Inches(0.4),
         "The clinical reality", size=18, bold=True, color=TEAL)
add_bullets(s, Inches(0.5), Inches(1.85), Inches(6), Inches(4), [
    "**WHO**  ~7% of adults 60+ globally have depression",
    "Most never receive a diagnosis or treatment",
    "Drivers: stigma, somatic presentation, comorbidity, time-poor primary care",
    "Linked to worse outcomes in CVD, dementia, all-cause mortality",
    "Universal screening is impractical at population scale",
], size=15, spacing=8)

add_text(s, Inches(7.0), Inches(1.4), Inches(6), Inches(0.4),
         "The ML opportunity", size=18, bold=True, color=CORAL)
add_bullets(s, Inches(7.0), Inches(1.85), Inches(6), Inches(4), [
    "Routine survey or health-record data is already collected",
    "ML can flag the highest-risk for clinician follow-up",
    "Saves clinician time \u2014 better than untargeted screening",
    "Most beneficial when prediction is **early enough** to act on",
], size=15, spacing=8)

section_band(s, Inches(5.95),
             "Goal  \u2014  Predict depression onset 2 to 4 years ahead from data already in routine collection.",
             accent=NAVY, body_size=15, label="Project goal")
add_footer(s, 2)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3 — Research Questions
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_header(s, "Research Questions",
           "Three questions, locked before any modelling began")

# RQ cards
rqs = [
    ("RQ1", "Can ML predict depression onset 2 to 4 years ahead\nfrom ELSA survey data alone?", CORAL),
    ("RQ2", "Does combining two waves of data improve\nover single-wave models?", TEAL),
    ("RQ3", "Which feature domains carry independent predictive\nsignal beyond prior depression history?", AMBER),
]
card_w = Inches(4.0)
card_h = Inches(3.5)
y = Inches(1.6)
for i, (k, v, c) in enumerate(rqs):
    x = Inches(0.5 + i * 4.15)
    add_rect(s, x, y, card_w, card_h, LIGHT)
    add_rect(s, x, y, card_w, Inches(0.6), c)
    add_text(s, x, y + Inches(0.10), card_w, Inches(0.4),
             k, size=20, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(s, x + Inches(0.25), y + Inches(0.85), card_w - Inches(0.5),
             card_h - Inches(0.9), v, size=15, color=NAVY)

section_band(s, Inches(5.45),
             "Mapping  \u2014  RQ2 answered by the three prediction arms; RQ3 answered by SHAP and the leakage sensitivity analysis.",
             accent=NAVY, body_size=14, label="How we answer them",
             height_in=1.5)
add_footer(s, 3)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4 — ELSA Dataset and Wave Selection
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_header(s, "ELSA: The Dataset",
           "Representative panel of English adults 50+, biennial since 2002")

# Left: what's in ELSA
add_text(s, Inches(0.5), Inches(1.4), Inches(6.2), Inches(0.4),
         "What's in the data", size=18, bold=True, color=TEAL)
add_bullets(s, Inches(0.5), Inches(1.85), Inches(6.2), Inches(3), [
    "Same individuals followed every 2 years (Waves 1 to 11)",
    "Health, cognition, social, economic, lifestyle",
    "**8-item CES-D depression scale** at every wave",
    "UK Data Service deposit 5050 (Stata format)",
], size=14, spacing=6)

# Right: wave selection box
add_text(s, Inches(7.0), Inches(1.4), Inches(6), Inches(0.4),
         "Why Waves 6, 7, 8?  (Akeeb's audit)", size=18, bold=True, color=CORAL)
add_bullets(s, Inches(7.0), Inches(1.85), Inches(6), Inches(3.5), [
    "**93\u201397%** valid CES-D in every wave",
    "**>90%** participant overlap across consecutive waves",
    "13,920 unique variables, but only 2,656 common to all waves",
    "Waves 6\u20137\u20138 = strongest consecutive longitudinal block",
], size=14, spacing=6)

# Sample funnel along bottom
metric_top = Inches(5.1)
metric_h = Inches(1.55)
funnel = [("10,601", "Wave 6 IFS\nrespondents"),
          ("9,666", "Wave 7 IFS\nrespondents"),
          ("8,445", "Wave 8 IFS\nrespondents"),
          ("7,535", "Inner-join\nW6\u2229W7\u2229W8"),
          ("7,211", "After valid\nCES-D filter")]
xs = [Inches(0.5 + i * 2.55) for i in range(5)]
for (val, lab), x in zip(funnel, xs):
    add_rect(s, x, metric_top, Inches(2.45), metric_h, LIGHT)
    add_text(s, x, metric_top + Inches(0.12), Inches(2.45), Inches(0.5),
             val, size=22, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    add_text(s, x, metric_top + Inches(0.78), Inches(2.45), Inches(0.7),
             lab, size=11, color=GREY, align=PP_ALIGN.CENTER)
    if x != xs[-1]:
        # arrow
        add_text(s, x + Inches(2.45), metric_top + Inches(0.55), Inches(0.1),
                 Inches(0.5), "\u25B6", size=14, color=GREY)
add_footer(s, 4)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 5 — Outcome variable + CES-D fix
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_header(s, "The Outcome Variable",
           "Binary depression label \u2014 CES-D \u2265 3 at Wave 8")

# Left: the outcome distribution
add_image(s, FIG / "outcome_distribution.png",
          Inches(0.5), Inches(1.4), width=Inches(7.5))

# Right: definition and fix
add_text(s, Inches(8.5), Inches(1.4), Inches(4.6), Inches(0.4),
         "Why CES-D \u2265 3", size=18, bold=True, color=TEAL)
add_bullets(s, Inches(8.5), Inches(1.85), Inches(4.6), Inches(2.0), [
    "Validated 8-item depression screen",
    "Steffick (2000) cutoff",
    "**~19%** observed prevalence \u2014 matches literature",
], size=13, spacing=6)

add_text(s, Inches(8.5), Inches(3.55), Inches(4.6), Inches(0.4),
         "The CES-D fix", size=18, bold=True, color=CORAL)
add_bullets(s, Inches(8.5), Inches(4.00), Inches(4.6), Inches(2.5), [
    "**Earlier bug**: raw items on a 0-3 scale \u2192 prevalence ~74%",
    "**Fix**: switched to IFS-validated cesd_sc",
    "Range corrected to 0-8; prevalence drops to 19%",
    "Lesson: always validate against published prevalence",
], size=12, spacing=4)

section_band(s, Inches(6.4),
             "Class imbalance handled via class_weight='balanced' (LR, RF) and scale_pos_weight=4 (XGB).",
             accent=NAVY, body_size=13, label="Imbalance handling",
             height_in=0.6)
add_footer(s, 5)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 6 — Pipeline overview
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_header(s, "The Pipeline",
           "End-to-end reproducible Colab notebook")

# Pipeline stages as a horizontal flow
stages = [
    ("1. Load + merge",  "IFS / Core / Financial files\nInner join on idauniq",        TEAL),
    ("2. Preprocess",    "Recode -1/-8/-9 \u2192 NaN\nDrop >40% missing\n(train-only)",  TEAL),
    ("3. Engineer",      "10 derived features\nincl. CES-D change",                    CORAL),
    ("4. Split",         "75/25 stratified test\n5-fold stratified CV",                NAVY),
    ("5. Train + tune",  "LR, RF, XGB, LGBM\nRandomizedSearchCV",                      AMBER),
    ("6. Evaluate",      "AUC, F1, recall\nCalibration\nSHAP",                         GREEN),
]
card_w = Inches(2.0)
card_h = Inches(2.4)
y = Inches(1.6)
gap = Inches(0.13)
total_w = card_w * 6 + gap * 5
start_x = (prs.slide_width - total_w) // 2
for i, (head, body, c) in enumerate(stages):
    x = start_x + i * (card_w + gap)
    add_rect(s, x, y, card_w, card_h, LIGHT)
    add_rect(s, x, y, card_w, Inches(0.55), c)
    add_text(s, x, y + Inches(0.10), card_w, Inches(0.4),
             head, size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(s, x + Inches(0.15), y + Inches(0.7), card_w - Inches(0.3),
             card_h - Inches(0.8), body, size=11, color=NAVY)

# Engineered features list
add_text(s, Inches(0.5), Inches(4.4), Inches(12.3), Inches(0.4),
         "10 engineered features capture longitudinal dynamics",
         size=15, bold=True, color=NAVY)
features = [
    "**cesd_change** (W7-W6)",
    "**mobility_count** W6/W7",
    "**adl_count** W6/W7",
    "**iadl_count** W6/W7",
    "**functional_burden** W6/W7",
    "**mobility_change** (W7-W6)",
]
fx = Inches(0.5)
fy = Inches(4.85)
fw = Inches(2.05)
for i, f in enumerate(features):
    cx = Inches(0.5 + i * 2.13)
    add_rect(s, cx, fy, fw, Inches(0.55), LIGHT)
    add_bullets(s, cx + Inches(0.05), fy + Inches(0.13), fw - Inches(0.1),
                Inches(0.4), [f], size=11, spacing=0)

section_band(s, Inches(5.85),
             "All preprocessing fit on training data only \u2014 zero test-set leakage. Median imputation and scaling inside sklearn Pipelines.",
             accent=NAVY, body_size=12, label="Methodology",
             height_in=0.95)
add_footer(s, 6)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 7 — Three prediction arms (RQ2 design)
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_header(s, "Experimental Design",
           "Three prediction arms \u00d7 five feature configurations \u00d7 four models")

# Three arm cards
arms = [
    ("W6 only",   "~4-year horizon",   "68 features",   CORAL),
    ("W7 only",   "~2-year horizon",   "68 features",   AMBER),
    ("W6 + W7",   "Combined longitudinal",  "138 features\n+ change features",  TEAL),
]
card_w = Inches(4.0)
card_h = Inches(2.3)
y = Inches(1.55)
for i, (head, sub, body, c) in enumerate(arms):
    x = Inches(0.5 + i * 4.15)
    add_rect(s, x, y, card_w, card_h, LIGHT)
    add_rect(s, x, y, card_w, Inches(0.55), c)
    add_text(s, x, y + Inches(0.10), card_w, Inches(0.4),
             head, size=18, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(s, x + Inches(0.25), y + Inches(0.7), card_w - Inches(0.5),
             Inches(0.4), sub, size=13, color=GREY)
    add_text(s, x + Inches(0.25), y + Inches(1.15), card_w - Inches(0.5),
             card_h - Inches(1.2), body, size=14, color=NAVY)

# Five configs row
cy = Inches(4.05)
add_text(s, Inches(0.5), cy, Inches(12.3), Inches(0.4),
         "Five feature configurations per arm (RQ3 design)",
         size=15, bold=True, color=NAVY)
configs = [
    ("full", "All predictors"),
    ("no_cesd", "Drop prior CES-D"),
    ("health_only", "SRH + chronic"),
    ("function_cog", "Mobility + ADL + cognition"),
    ("socioeconomic", "Wealth + employ + social"),
]
ccy = cy + Inches(0.5)
ccw = Inches(2.46)
for i, (name, desc) in enumerate(configs):
    cx = Inches(0.5 + i * 2.55)
    add_rect(s, cx, ccy, ccw, Inches(1.2), LIGHT)
    add_text(s, cx, ccy + Inches(0.18), ccw, Inches(0.4),
             name, size=14, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    add_text(s, cx + Inches(0.1), ccy + Inches(0.6), ccw - Inches(0.2),
             Inches(0.5), desc, size=11, color=GREY, align=PP_ALIGN.CENTER)

section_band(s, Inches(6.0),
             "3 arms \u00d7 5 configs \u00d7 4 models = 60 baseline experiments. Best config per arm then tuned via RandomizedSearchCV (50 iter, 5-fold).",
             accent=NAVY, body_size=12, label="Total experiments",
             height_in=0.95)
add_footer(s, 7)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 8 — Headline Results
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_header(s, "Headline Results",
           "Tuned Random Forest combining W6+W7 \u2014 AUC 0.85 on held-out test set")

add_image(s, FIG / "roc_curves.png",
          Inches(0.5), Inches(1.4), height=Inches(3.7))
add_image(s, FIG / "pr_curves.png",
          Inches(6.7), Inches(1.4), height=Inches(3.7))

# Headline metric strip
band_top = Inches(5.4)
add_rect(s, Inches(0.5), band_top, Inches(12.3), Inches(1.55), LIGHT)
add_text(s, Inches(0.7), band_top + Inches(0.08), Inches(12), Inches(0.4),
         "Best tuned model per arm (test set)", size=14, bold=True, color=NAVY)

cols = [
    ("W6 only (~4 yr)", "AUC 0.819", "F1 0.532  Recall 0.732", AMBER),
    ("W7 only (~2 yr)", "AUC 0.824", "F1 0.545  Recall 0.668", AMBER),
    ("W6+W7 combined",  "AUC 0.848", "F1 0.582  Recall 0.714", CORAL),
]
for i, (head, auc, rest, color) in enumerate(cols):
    cx = Inches(0.7 + i * 4.05)
    add_text(s, cx, band_top + Inches(0.5), Inches(4), Inches(0.4),
             head, size=13, bold=True, color=color)
    add_text(s, cx, band_top + Inches(0.85), Inches(4), Inches(0.4),
             auc, size=18, bold=True, color=color)
    add_text(s, cx, band_top + Inches(1.20), Inches(4), Inches(0.3),
             rest, size=11, color=GREY)
add_footer(s, 8)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 9 — Interpretation: SHAP
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_header(s, "What Drives the Predictions?",
           "SHAP feature importance \u2014 Random Forest, W6+W7 full model")

add_image(s, FIG / "shap_bar_rf.png",
          Inches(0.5), Inches(1.4), height=Inches(5.2))

# Right column — interpretation
add_text(s, Inches(7.5), Inches(1.4), Inches(5.6), Inches(0.4),
         "Top predictors (full model)", size=18, bold=True, color=TEAL)
add_bullets(s, Inches(7.5), Inches(1.85), Inches(5.6), Inches(2.5), [
    "**Prior CES-D**  state dependence dominates",
    "**Self-rated health**  subjective vitality",
    "**Mobility count**  physical function decline",
    "**CES-D change**  worsening trajectory matters",
    "**Financial difficulty**  socioeconomic strain",
], size=14, spacing=5)

add_text(s, Inches(7.5), Inches(4.2), Inches(5.6), Inches(0.4),
         "What this shows", size=18, bold=True, color=CORAL)
add_bullets(s, Inches(7.5), Inches(4.65), Inches(5.6), Inches(2.5), [
    "Late-life depression has a **biopsychosocial** signature",
    "Physical, mental, and social signals all visible 2-4 yrs ahead",
    "Aligns with established gerontological depression literature",
], size=12, spacing=4)
add_footer(s, 9)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 10 — Leakage Sensitivity (the central scientific finding)
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_header(s, "Beyond Depression History",
           "Even without prior CES-D, the model still predicts well")

add_image(s, FIG / "leakage_sensitivity.png",
          Inches(0.5), Inches(1.4), height=Inches(4.0))

# Right: explanation
add_text(s, Inches(7.5), Inches(1.4), Inches(5.6), Inches(0.4),
         "The leakage test", size=18, bold=True, color=TEAL)
add_bullets(s, Inches(7.5), Inches(1.85), Inches(5.6), Inches(2), [
    "Strip every CES-D-related feature; refit",
    "Tests: is the model just \"depressed people stay depressed\"?",
], size=14, spacing=5)

add_text(s, Inches(7.5), Inches(3.4), Inches(5.6), Inches(0.4),
         "What we found", size=18, bold=True, color=CORAL)
add_bullets(s, Inches(7.5), Inches(3.85), Inches(5.6), Inches(2.5), [
    "**AUC 0.848 \u2192 0.773** (drop of 0.075)",
    "Drop is real \u2014 prior depression matters",
    "But 0.77 is still a clinically usable screening signal",
    "Achieved with **no mental health features at all**",
], size=13, spacing=5)

# Bottom finding band
add_rect(s, Inches(0.5), Inches(6.05), Inches(12.3), Inches(0.95), NAVY)
add_text(s, Inches(0.7), Inches(6.15), Inches(12), Inches(0.4),
         "Headline scientific finding", size=12, bold=True, color=CORAL)
add_text(s, Inches(0.7), Inches(6.50), Inches(12), Inches(0.5),
         "Depression risk leaves a measurable footprint in physical, functional, and economic data 2\u20134 years before symptoms emerge.",
         size=14, color=WHITE)
add_footer(s, 10)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 11 — Limitations
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_header(s, "Limitations",
           "Where the model can and cannot be trusted")

# Two columns
add_text(s, Inches(0.5), Inches(1.4), Inches(6.2), Inches(0.4),
         "Methodological", size=18, bold=True, color=CORAL)
add_bullets(s, Inches(0.5), Inches(1.85), Inches(6.2), Inches(4.5), [
    "**Screening, not diagnosis**  CES-D \u2265 3 flags symptoms, not MDD",
    "**Observational**  associations, not causal claims",
    "**Attrition bias**  ~30% of W6 sample dropped (likely sicker)",
    "**State dependence**  prior CES-D dominates the full model",
    "**Imbalance**  precision \u2248 49%; ~half of flagged are false +ve",
], size=14, spacing=6)

add_text(s, Inches(7.0), Inches(1.4), Inches(6), Inches(0.4),
         "Generalisability", size=18, bold=True, color=AMBER)
add_bullets(s, Inches(7.0), Inches(1.85), Inches(6), Inches(4.5), [
    "Validated only on **English population aged 50+**",
    "Excludes institutionalised and care-home residents",
    "ELSA cohort effects (e.g. 1950s-born \u2260 today's 50-year-olds)",
    "**Fairness not yet evaluated** across sex, ethnicity, SES",
    "Threshold of 0.5 is naive \u2014 deployment must tune to capacity",
], size=14, spacing=6)

section_band(s, Inches(6.05),
             "These limitations were noted explicitly in the GitHub PR review process and accepted as documented constraints, not silent gaps.",
             accent=NAVY, body_size=12, label="Transparency",
             height_in=0.95)
add_footer(s, 11)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 12 — Future and Conclusion
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_header(s, "Future Directions and Conclusion",
           "From a coursework prototype to a clinical research roadmap")

add_text(s, Inches(0.5), Inches(1.4), Inches(6.2), Inches(0.4),
         "Future directions", size=18, bold=True, color=TEAL)
add_bullets(s, Inches(0.5), Inches(1.85), Inches(6.2), Inches(4.5), [
    "**Incident-only model**  exclude already-depressed at baseline",
    "**External validation**  HRS (US), SHARE (EU), TILDA (Ireland)",
    "**Biomarkers**  add ELSA nurse-visit blood data",
    "**Trajectory models**  RNNs across many waves",
    "**Fairness audit**  calibration across subgroups",
    "**Cost-effectiveness**  QALY analysis with intervention data",
], size=13, spacing=5)

add_text(s, Inches(7.0), Inches(1.4), Inches(6), Inches(0.4),
         "Take-home messages", size=18, bold=True, color=CORAL)
add_bullets(s, Inches(7.0), Inches(1.85), Inches(6), Inches(4.5), [
    "**RQ1**  AUC 0.85 = clinically useful early prediction",
    "**RQ2**  Two waves > one, but recent snapshot \u2248 combined",
    "**RQ3**  Non-mental-health features carry independent signal",
    "Routine over-50 health-check data could feed this model today",
], size=13, spacing=5)

# Bottom conclusion band
add_rect(s, Inches(0.5), Inches(5.9), Inches(12.3), Inches(1.1), NAVY)
add_text(s, Inches(0.7), Inches(6.0), Inches(12), Inches(0.4),
         "In one sentence", size=12, bold=True, color=CORAL)
add_text(s, Inches(0.7), Inches(6.35), Inches(12), Inches(0.6),
         "Routine survey data can flag future depression with clinically useful accuracy 2\u20134 years in advance \u2014 even without using depression history at all.",
         size=15, bold=True, color=WHITE)
add_footer(s, 12)


# ─────────────────────────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────────────────────────
TOTAL = len(prs.slides)
OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(str(OUT))
print(f"Saved deck: {OUT}")
print(f"Slide count: {len(prs.slides)}")
