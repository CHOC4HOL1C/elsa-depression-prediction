"""
config.py — ELSA project runtime configuration
------------------------------------------------
Auto-detects the runtime environment and sets DATA_ROOT accordingly.
Add your own environment block if needed — do NOT commit actual paths
containing personal data locations.

Priority order:
  1. ELSA_DATA_ROOT environment variable (set this on HPC / lab computers)
  2. Google Drive mount (Colab)
  3. Local fallback (macOS/Linux)
"""

import os
from pathlib import Path

# ── 1. Honour explicit environment variable (HPC, lab, CI) ──────────────────
if "ELSA_DATA_ROOT" in os.environ:
    DATA_ROOT = Path(os.environ["ELSA_DATA_ROOT"])

# ── 2. Google Colab + Drive ──────────────────────────────────────────────────
elif Path("/content/drive/MyDrive").exists():
    DATA_ROOT = Path("/content/drive/MyDrive/ELSA/data/UKDA-5050-stata/stata/stata13_se")

# ── 3. Local macOS / Linux fallback ─────────────────────────────────────────
else:
    # Edit this to your local path, but do not commit personal paths.
    # Better: set ELSA_DATA_ROOT in your shell profile instead.
    DATA_ROOT = Path.home() / "data" / "ELSA" / "UKDA-5050-stata" / "stata" / "stata13_se"

# ── Derived paths ────────────────────────────────────────────────────────────
# Core wave files
CORE = {
    6: DATA_ROOT / "wave_6_elsa_data_v2.dta",
    7: DATA_ROOT / "wave_7_elsa_data.dta",
    8: DATA_ROOT / "wave_8_elsa_data_eul_v2.dta",
}

# IFS derived variable files
IFS = {
    6: DATA_ROOT / "wave_6_ifs_derived_variables.dta",
    7: DATA_ROOT / "wave_7_ifs_derived_variables.dta",
    8: DATA_ROOT / "wave_8_ifs_derived_variables.dta",
}

# Financial derived files (quintile summary vars only)
FIN = {
    6: DATA_ROOT / "wave_6_financial_derived_variables.dta",
    7: DATA_ROOT / "wave_7_financial_derived_variables.dta",
    8: DATA_ROOT / "wave_8_financial_derived_variables.dta",
}

# ── Output directory (safe to commit contents) ───────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent
OUTPUTS   = REPO_ROOT / "outputs"
OUTPUTS.mkdir(exist_ok=True)


def check_paths() -> None:
    """Print a path health-check. Call at the top of any notebook."""
    print(f"Runtime: {'Colab' if Path('/content').exists() else 'Local/HPC'}")
    print(f"DATA_ROOT: {DATA_ROOT}")
    all_ok = True
    for label, d in [("Core", CORE), ("IFS", IFS), ("Financial", FIN)]:
        for wave, p in d.items():
            exists = p.exists()
            status = "✓" if exists else "✗ MISSING"
            print(f"  {status}  W{wave} {label}: {p.name}")
            if not exists:
                all_ok = False
    if all_ok:
        print("\nAll data files found.")
    else:
        print("\nSome files missing — check DATA_ROOT or set ELSA_DATA_ROOT env var.")
