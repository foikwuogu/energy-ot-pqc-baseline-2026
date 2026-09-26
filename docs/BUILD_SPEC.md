# Build spec: PQC Readiness of the Energy OT Stack: A 2026 Baseline

```
PROJECT:        PQC readiness of the energy OT stack: a 2026 baseline. Archetype: technical report (9) built on an evidence map (7) + analysis (8).
QUESTION:       Where does energy-sector OT stand today on the move to post-quantum cryptography, measured by indicators that can be
                re-measured every year from public sources?
SOURCES:        ONG-OT dataset v1.1 (doi:10.5281/zenodo.22729882; CISA ICS advisories via ICS Advisory Project, ODbL);
                PQC Readiness Crosswalk v1.0 (doi:10.5281/zenodo.22730718; crosswalk.csv, timeline.csv; author-verified 2026-09-09);
                CBOM Builder v0.1.0 component crosswalk (github.com/foikwuogu/cbom-builder);
                public web sources for config/policy_signals.csv and config/vendor_pqc_scan.csv (URLs in each row; scan date 2026-09-23).
UNIT:           protocol family (I1-I2); cryptographic component (I3); CISA advisory (I4-I6); instrument / vendor (I7-I8); date (I9).
MEASURES:       see report Table 1 / report/tables/t0_baseline_indicators.csv.
OUTPUTS:        report/Energy_OT_PQC_Baseline_2026.docx + .pdf; figures 1-4; tables t0-t2; report/stats.json; data/processed/energy_advisories_crypto.csv.
VENUES:         GitHub release v0.1.0 (foikwuogu/energy-ot-pqc-baseline-2026); Zenodo report with DOI (Dec 2026); optional arXiv cs.CR.
VERIFY POINTS:  crypto CWE category map; protocol status table; policy signals rows; vendor scan rows; federal dates (EO 14412, OMB M-26-15);
                spot-check advisories; all prose.
LICENSE:        code MIT; report/figures/docs CC BY 4.0; derived advisory tables ODbL v1.0.
ASSUMPTIONS:    scope = companion report scope with EV charging kept; authors = standard block + standard co-authors;
                the planning tag on the original plan item was removed from the title.
```
