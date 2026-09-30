# PQC Readiness of the Energy OT Stack: A 2026 Baseline

**Status:** v1.0.0, published on Zenodo 2026-09-26 (author-verified; see docs/VERIFY_CHECKLIST.md) | **DOI (v1.0.0):** [10.5281/zenodo.22975133](https://doi.org/10.5281/zenodo.22975133) · **All versions:** [10.5281/zenodo.22975132](https://doi.org/10.5281/zenodo.22975132) | **Companion:** annual report, 10.5281/zenodo.22974795

A technical report setting nine re-measurable indicators of how far energy-sector operational technology (OT) has moved toward post-quantum cryptography (FIPS 203/204/205). The indicators cover protocol standards, the cryptographic components in use, cryptographic weaknesses disclosed in CISA ICS advisories, and ecosystem signals (federal instruments, CISA's PQC product categories, a vendor desk scan). It is a companion to *State of OT Vulnerability Exposure in US Oil and Natural Gas, 2026*.

**Authors:** Friday Ogochukwu Ikwuogu ([ORCID 0009-0009-2222-1318](https://orcid.org/0009-0009-2222-1318)), Independent Researcher, Odessa, Texas, USA (corresponding); Abidemi Orimogunje (Redeemer's University); Eria Othieno Pinyi (University of Fairfax); David Mike-Ewewie (University of Texas Permian Basin).

## What is here
```
report/Energy_OT_PQC_Baseline_2026.docx/.pdf         the report (final, v1.0.0)
report/stats.json, report/tables/t0_baseline_indicators.csv   the baseline values
config/crypto_cwe_map.json          CWE -> cryptographic weakness category (judgment)
config/protocol_pqc_status.csv      I1-I2, per protocol family
config/policy_signals.csv           dated OT-relevant PQC instruments, with URLs
config/vendor_pqc_scan.csv          vendor desk scan, with URLs
data/raw/inputs/                    vendored crosswalk inputs (PQC crosswalk v1.0, CBOM Builder v0.1.0)
code/01_ingest.py ... 05_report.js  pipeline in run order
docs/                               BUILD_SPEC, CODEBOOK, LIMITATIONS, VERIFY_CHECKLIST, NEXT_STEPS, PUBLISH_GUIDE
```

## Reproduce
```
pip install -r requirements.txt && npm install
python code/01_ingest.py --ong path/to/ong_ot_dataset_v1.1.csv   # from https://doi.org/10.5281/zenodo.22729882
./run_all.sh            # watermarked working copy
./run_all.sh --final    # clean release build (used for v1.0.0)
```

## Sources
ONG-OT Vulnerability Prioritization Dataset v1.1 (https://doi.org/10.5281/zenodo.22729882); PQC Readiness Crosswalk for Energy OT Protocols and Identity Systems v1.0 (https://doi.org/10.5281/zenodo.22730718); CBOM Builder v0.1.0 (https://github.com/foikwuogu/cbom-builder); public URLs listed per row in config/.

## Limitations, license, citation
See docs/LIMITATIONS.md. Code MIT; report, figures and docs CC BY 4.0; derived advisory tables ODbL v1.0. Cite via CITATION.cff.

## AI assistance

**AI assistance:** AI coding tools (Claude, Anthropic) were used for code scaffolding, test fixtures, and documentation drafting. The problem definition, methodology, classification rules, mappings, and analytic decisions are the author's own.
