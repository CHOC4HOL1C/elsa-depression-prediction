# Documentation

Files in this folder, what they are for, and how to share them.

## Reports

| File | Format | Purpose |
|------|--------|---------|
| [`REPORT.md`](REPORT.md) | Markdown | Source-of-truth project report. Edit this if anything changes. Renders cleanly on GitHub. |
| [`ELSA_Depression_Prediction_Report.docx`](ELSA_Depression_Prediction_Report.docx) | Word | Shareable document for teammates not on GitHub. Editable, viewable on any device. |
| [`team_contributions.md`](team_contributions.md) | Markdown | Per-member contribution summary. Required submission artefact. |
| [`CONTEXT.md`](CONTEXT.md) | Markdown | Project context document for collaborators. |
| [`meeting_minutes/`](meeting_minutes/) | Folder | Group meeting minutes (required submission artefact). |

## Producing a PDF of the report

The DOCX is the cleanest sharing artefact. To generate a PDF copy:

1. Open `ELSA_Depression_Prediction_Report.docx` in Microsoft Word, Apple Pages, Google Docs, or LibreOffice.
2. Choose **File → Save As** (or **Export**) and select **PDF**.

Any of these tools will render the document with full fidelity. We chose not to commit a PDF directly because it would diverge from the live Markdown source the moment anyone edits the report.

## Regenerating the DOCX after editing `REPORT.md`

```bash
python3 docs/build_report_docx.py
```

This rebuilds `ELSA_Depression_Prediction_Report.docx` from `REPORT.md`. The script handles headings, paragraphs, bullet lists, fenced code blocks, pipe tables, inline bold/italic/code, and horizontal rules — i.e. everything used in the report.

The build script needs `python-docx`:

```bash
pip3 install python-docx
```
