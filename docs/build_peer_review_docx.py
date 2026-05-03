"""
Convert docs/peer_review_draft.md into a polished Word document for sharing.

Usage:  python3 docs/build_peer_review_docx.py
Output: docs/Peer_Review.docx

Reuses the same Markdown->DOCX conversion approach as build_report_docx.py.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Cm, Pt, RGBColor

# Reuse the parser + renderer helpers from build_report_docx by importing them
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_report_docx import (  # type: ignore
    _hr,
    _heading,
    _paragraph,
    _bullet,
    _code_block,
    _table,
    parse_markdown,
    NAVY,
    TEAL,
    GREY,
    INK,
)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "peer_review_draft.md"
OUT = ROOT / "docs" / "Peer_Review.docx"


def build():
    md = SRC.read_text(encoding="utf-8")
    doc = Document()

    # A4 page setup
    for section in doc.sections:
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin = Cm(2.2)
        section.right_margin = Cm(2.2)

    # Default font
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    # Cover-style title block
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = title.add_run("Peer Review")
    run.bold = True
    run.font.size = Pt(28)
    run.font.color.rgb = NAVY
    run.font.name = "Calibri"

    sub = doc.add_paragraph()
    sub.paragraph_format.space_after = Pt(2)
    sub_run = sub.add_run(
        "Group 4 \u2014 \u201cHealth is Wealth\u201d"
    )
    sub_run.italic = True
    sub_run.font.size = Pt(13)
    sub_run.font.color.rgb = TEAL
    sub_run.font.name = "Calibri"

    meta = doc.add_paragraph()
    meta.paragraph_format.space_after = Pt(2)
    meta_run = meta.add_run(
        "AI and Healthcare (EEEM069) \u2014 University of Surrey, MSc Artificial Intelligence (2025/26)"
    )
    meta_run.font.size = Pt(11)
    meta_run.font.color.rgb = GREY

    reviewer = doc.add_paragraph()
    reviewer.paragraph_format.space_after = Pt(2)
    reviewer_run = reviewer.add_run("Reviewer: Akano Fiyinfoluwa")
    reviewer_run.font.size = Pt(11)
    reviewer_run.bold = True
    reviewer_run.font.color.rgb = NAVY

    _hr(doc)

    # Process Markdown body, skipping the first H1 (we have a title block)
    skip_first_h1 = True
    for tok in parse_markdown(md):
        kind = tok[0]
        if kind == "heading":
            level, text = tok[1], tok[2]
            if skip_first_h1 and level == 1:
                skip_first_h1 = False
                continue
            _heading(doc, text, level)
        elif kind == "para":
            _paragraph(doc, tok[1])
        elif kind == "bullet":
            _bullet(doc, tok[1])
        elif kind == "code":
            _code_block(doc, tok[1])
        elif kind == "table":
            _table(doc, tok[1], tok[2])
        elif kind == "hr":
            _hr(doc)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUT))
    print(f"Saved: {OUT}")
    print(f"Size: {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    build()
