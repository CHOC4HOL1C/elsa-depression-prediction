"""
Run ELSA_Depression_Prediction_Final_v2.ipynb locally (no Colab needed).

Patches the three Colab-specific assumptions:
  1. ELSA_PATH      -> local UKDA-5050-stata folder
  2. dep install    -> skip the xgboost reinstall (already installed in venv)
  3. OUT_ROOT       -> ../outputs/colab_local_run/  (writable workspace path)

Executes cell-by-cell with live progress prints. The executed notebook is
written to submission/ELSA_Depression_Prediction_Final_v2_executed.ipynb so
the marker / team can inspect cell outputs without re-running.
"""
from __future__ import annotations
import sys, time, json, os
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

REPO   = Path(__file__).resolve().parent.parent
SRC    = REPO / "submission" / "ELSA_Depression_Prediction_Final_v2.ipynb"
DST    = REPO / "submission" / "ELSA_Depression_Prediction_Final_v2_executed.ipynb"
DATA   = Path("/Users/the1finix/Documents/University of Surrey/Feb 2026 Courses/"
              "Surrey Courses/AIH/Group Project/Datasets/UKDA-5050-stata/stata/stata13_se")
OUTDIR = REPO / "outputs" / "colab_local_run"
OUTDIR.mkdir(parents=True, exist_ok=True)


def patch(nb):
    """Apply local-environment patches to known cells (matched by source content)."""
    n_patched = 0
    for c in nb.cells:
        if c.cell_type != "code":
            continue
        src = c.source

        if "ELSA_PATH = " in src and "/content/drive" in src:
            c.source = (
                "# [LOCAL RUN] ELSA_PATH patched to local Mac data folder\n"
                f'ELSA_PATH = r"{DATA}"\n'
            )
            n_patched += 1
            continue

        if "xgboost[cuda]" in src:
            c.source = (
                "# [LOCAL RUN] dependency install skipped — venv already has\n"
                "# pandas, sklearn, xgboost, lightgbm, shap, pyreadstat installed\n"
                "print('Dependencies OK (local venv)')\n"
            )
            n_patched += 1
            continue

        if 'OUT_ROOT  = Path("/content/outputs")' in src:
            c.source = src.replace(
                'OUT_ROOT  = Path("/content/outputs")',
                f'OUT_ROOT  = Path(r"{OUTDIR}")  # [LOCAL RUN]'
            )
            n_patched += 1
            continue

    print(f"Patched {n_patched} cells for local execution")
    return nb


def run():
    print(f"Source : {SRC}")
    print(f"Output : {DST}")
    print(f"Data   : {DATA}  (exists={DATA.exists()})")
    print(f"Outdir : {OUTDIR}")
    print()

    if not DATA.exists():
        sys.exit(f"ELSA data folder not found: {DATA}")

    nb = nbf.read(SRC, as_version=4)
    nb = patch(nb)

    client = NotebookClient(
        nb,
        timeout=1800,
        kernel_name="elsa-local",
        resources={"metadata": {"path": str(REPO / "submission")}},
        record_timing=True,
    )

    t0 = time.time()
    n_total = sum(1 for c in nb.cells if c.cell_type == "code")
    print(f"Executing {n_total} code cells...\n")

    try:
        with client.setup_kernel():
            n_done = 0
            for idx, cell in enumerate(nb.cells):
                if cell.cell_type != "code":
                    continue
                n_done += 1
                src_preview = (cell.source.splitlines() or [""])[0][:70]
                t_cell = time.time()
                try:
                    client.execute_cell(cell, idx)
                except CellExecutionError as e:
                    dt = time.time() - t_cell
                    print(f"[{n_done:>2}/{n_total}] cell {idx:>3} FAIL  "
                          f"({dt:>6.1f}s) {src_preview}")
                    print("--- error ---")
                    print(str(e)[:2000])
                    raise
                dt = time.time() - t_cell
                print(f"[{n_done:>2}/{n_total}] cell {idx:>3} OK    "
                      f"({dt:>6.1f}s) {src_preview}")
                # Persist progress every 5 cells so a crash doesn't lose output
                if n_done % 5 == 0:
                    nbf.write(nb, DST)
    finally:
        nbf.write(nb, DST)

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed/60:.1f} min  -> {DST.name}")
    print(f"Outputs: {OUTDIR}")


if __name__ == "__main__":
    run()
