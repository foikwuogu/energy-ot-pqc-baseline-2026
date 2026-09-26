#!/usr/bin/env python3
"""Step 1 - collect the frozen inputs and log provenance.

Inputs (all published by the same author group, cited by DOI or repository):
  1. ONG-OT Vulnerability Prioritization Dataset v1.1 (doi:10.5281/zenodo.22729882) - CISA ICS advisories + KEV/EPSS/Vulnrichment.
  2. PQC Readiness Crosswalk for Energy OT Protocols and Identity Systems v1.0 (doi:10.5281/zenodo.22730718)
     - data/processed/crosswalk.csv and timeline.csv, vendored in data/raw/inputs/.
  3. CBOM Builder v0.1.0 component crosswalk (github.com/foikwuogu/cbom-builder) - pqc_crosswalk.csv, vendored in data/raw/inputs/.

Usage:
  python code/01_ingest.py --ong path/to/ong_ot_dataset_v1.1.csv
  python code/01_ingest.py            # downloads input 1 from Zenodo (inputs 2-3 are already in the repository)
"""
import argparse
import datetime
import hashlib
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
INP = os.path.join(RAW, "inputs")
ONG = os.path.join(RAW, "ong_ot_dataset_v1.1.csv")
SOURCES = {
    "pqc_protocol_crosswalk_v1.0.csv": "https://doi.org/10.5281/zenodo.22730718 (data/processed/crosswalk.csv)",
    "pqc_policy_timeline_v1.0.csv": "https://doi.org/10.5281/zenodo.22730718 (data/processed/timeline.csv)",
    "cbom_component_crosswalk_v0.1.0.csv": "https://github.com/foikwuogu/cbom-builder (data/processed/pqc_crosswalk.csv, v0.1.0)",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def log(path, src, note):
    line = " | ".join([datetime.date.today().isoformat(), os.path.basename(path), f"{os.path.getsize(path)} bytes",
                       f"sha256:{sha256(path)}", src, note])
    with open(os.path.join(RAW, "PROVENANCE.txt"), "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ong", help="local copy of ong_ot_dataset_v1.1.csv")
    a = ap.parse_args()
    if a.ong:
        shutil.copyfile(a.ong, ONG)
        src = "https://doi.org/10.5281/zenodo.22729882 (local copy of the published file)"
    else:
        # reuse the companion report's downloader
        sib = os.path.join(ROOT, "..", "ong-ot-exposure-report-2026", "code", "01_ingest.py")
        if not os.path.exists(sib):
            sys.exit("Pass --ong <path>, or download ong_ot_dataset_v1.1.csv from https://doi.org/10.5281/zenodo.22729882")
        subprocess.check_call([sys.executable, sib])
        shutil.copyfile(os.path.join(ROOT, "..", "ong-ot-exposure-report-2026", "data", "raw", "ong_ot_dataset_v1.1.csv"), ONG)
        src = "https://doi.org/10.5281/zenodo.22729882"
    log(ONG, src, "frozen advisory snapshot")
    for f, s in SOURCES.items():
        log(os.path.join(INP, f), s, "vendored crosswalk input")


if __name__ == "__main__":
    main()
