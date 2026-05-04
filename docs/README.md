# Documentation

Files in this folder, what they are for, and how to share them.

## Reports and required submission artefacts

| File | Format | Purpose |
|------|--------|---------|
| [`REPORT.md`](REPORT.md) | Markdown | Source-of-truth project report. Edit this if anything changes. Renders cleanly on GitHub. |
| [`ELSA_Depression_Prediction_Report.docx`](ELSA_Depression_Prediction_Report.docx) | Word | Shareable document for teammates not on GitHub. Editable, viewable on any device. |
| [`team_contributions.md`](team_contributions.md) | Markdown | Per-member contribution summary. Required submission artefact. |
| [`Meeting_Minutes.docx`](Meeting_Minutes.docx) | Word | Project coordination log (live meetings, PR reviews, async syncs, working sessions). Required submission artefact. Filename retained to match the SurreyLearn brief; document title is "Project Coordination Log". |
| [`peer_review_draft.md`](peer_review_draft.md) | Markdown | Private working draft for the peer-review form. Not for submission. |
| [`Peer_Review.docx`](Peer_Review.docx) | Word | Word version of the peer-review draft for offline editing. Not for submission. |
| [`CONTEXT.md`](CONTEXT.md) | Markdown | Project context document for collaborators. |

## Producing a PDF of the report

The DOCX is the cleanest sharing artefact. To generate a PDF copy:

1. Open `ELSA_Depression_Prediction_Report.docx` in Microsoft Word, Apple Pages, Google Docs, or LibreOffice.
2. Choose **File → Save As** (or **Export**) and select **PDF**.

Any of these tools will render the document with full fidelity. We chose not to commit a PDF directly because it would diverge from the live Markdown source the moment anyone edits the report.

## Regenerating the Word documents

The three Word documents in this folder are all generated from text/Markdown source so that they stay reproducible. Run any of these from the repository root:

```bash
# Rebuild the report DOCX from REPORT.md
python3 docs/build_report_docx.py

# Rebuild the coordination log DOCX from the data in the script
python3 docs/build_coordination_log.py

# Rebuild the peer-review DOCX from peer_review_draft.md
python3 docs/build_peer_review_docx.py
```

The report builder handles headings, paragraphs, bullet lists, fenced code blocks, pipe tables, inline bold/italic/code, and horizontal rules. The coordination log builder writes a fresh document each time using the entry data hard-coded inside the script.

The build scripts need `python-docx`:

```bash
pip3 install python-docx
```
