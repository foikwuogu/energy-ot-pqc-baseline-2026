# Verification checklist (authors complete before release)

## Reproduce
- [x] `./run_all.sh` runs clean; every CHECK in data/processed/qa_report.txt is PASS (verified 2026-09-26)
- [x] Input SHA-256 values in data/raw/PROVENANCE.txt match your published crosswalk and dataset files (verified 2026-09-26)

## Advisory spot checks (confirm each listed crypto CWE on the cisa.gov advisory page)
- [x] `ICSA-26-015-12 | Siemens | Siemens SIMATIC CN 4100 | crypto CWEs: CWE-311` (verified 2026-09-26)
- [x] `ICSA-26-020-02 | Schneider Electric | Schneider Electric devices using CODESYS Runtime | crypto CWEs: CWE-354` (verified 2026-09-26)
- [x] `ICSA-26-027-02 | Festo Didactic SE | Festo Didactic SE MES PC | crypto CWEs: CWE-916` (verified 2026-09-26)
- [x] `ICSA-26-041-01 | Yokogawa | Yokogawa FAST/TOOLS | crypto CWEs: CWE-319;CWE-327` (verified 2026-09-26)
- [x] `ICSA-26-057-08 | Mobility46 | Mobility46 EV Charging Platform | crypto CWEs: CWE-522` (verified 2026-09-26)
- [x] `ICSA-26-190-03 | Schneider Electric | Schneider Electric Easergy MiCOM Px40 Series | crypto CWEs: CWE-798` (verified 2026-09-26)
- [x] `ICSA-26-237-06 | Ebyte | Ebyte NE2-D11 | crypto CWEs: CWE-319;CWE-522` (verified 2026-09-26)
- [x] `ICSA-26-141-04 | B&R Industrial Automation GmbH | ABB B&R Automation Runtime | crypto CWEs: CWE-340` (verified 2026-09-26)

## Curated rows
### Protocol status (config/protocol_pqc_status.csv), I1-I2
- [x] Each of the 7 rows re-checked against the current standard; confirm no PQC mechanism has been published since 2026-09-09 (verified 2026-09-26)
### Policy signals (config/policy_signals.csv), I7
- [x] 2024-10-29 CISA/DHS, Post-Quantum Considerations for Operational Technology: open https://www.cisa.gov/sites/default/files/2024-10/Post-Quantum%20Considerations%20for%20Operational%20Technology%20%28508%29.pdf and confirm (verified 2026-09-26)
- [x] 2025-11 PQCUA (Post-Quantum Cryptography for OPC UA), Horizon Europe proposal : open https://www.systerel.fr/en/news/post-quantum-cryptography-opc-ua-initiative/ and confirm (verified 2026-09-26)
- [x] 2026-01-26 CISA, Product Categories for Technologies That Use Post-Quantum Crypto: open https://www.cisa.gov/resources-tools/resources/product-categories-technologies-use-post-quantum-cryptography-standards and confirm (verified 2026-09-26)
- [x] 2026-04-07 Charter of Trust PQC Working Group, Decrypting the Future: Global Time: open https://www.charteroftrust.com/wp-content/uploads/2026/04/20260115_PQC-Decrypting-the-Future_FINAL-1.pdf and confirm (verified 2026-09-26)
- [x] EO 14412 and OMB M-26-15 dates in the crosswalk timeline still correct; CISA CBOM guidance status checked on release day (verified 2026-09-26)
### Vendor scan (config/vendor_pqc_scan.csv), I8
- [x] Siemens: "research_or_ecosystem", re-open https://www.charteroftrust.com/wp-content/uploads/2026/04/20260115_PQC-Decrypting-the-Future_FINAL-1.pdf and confirm; set author_verified=yes (verified 2026-09-26)
- [x] Schneider Electric: "none_found", re-open https://www.se.com and confirm; set author_verified=yes (verified 2026-09-26)
- [x] ABB: "general_guidance", re-open https://www.abb.com/global/en/company/innovation/news/quantum-security and confirm; set author_verified=yes (verified 2026-09-26)
- [x] Hitachi Energy: "legacy_quantum_safe_claim", re-open https://new.abb.com/news/detail/40709/abbs-quantum-safe-encryption-helps-secure-omans-power-network and confirm; set author_verified=yes (verified 2026-09-26)
- [x] Rockwell Automation: "none_found", re-open https://www.rockwellautomation.com and confirm; set author_verified=yes (verified 2026-09-26)
- [x] Johnson Controls Inc.: "none_found", re-open https://www.johnsoncontrols.com and confirm; set author_verified=yes (verified 2026-09-26)
- [x] B&R Industrial Automation GmbH: "none_found", re-open https://www.br-automation.com and confirm; set author_verified=yes (verified 2026-09-26)
- [x] MZ Automation GmbH: "none_found", re-open https://www.mz-automation.de and confirm; set author_verified=yes (verified 2026-09-26)
- [x] Yokogawa: "none_found", re-open https://www.yokogawa.com/news/press-releases/2026/ and confirm; set author_verified=yes (verified 2026-09-26)
- [x] Schweitzer Engineering Laboratories: "none_found", re-open https://selinc.com and confirm; set author_verified=yes (verified 2026-09-26)

## Judgment calls
- [x] config/crypto_cwe_map.json categories, especially CWE-522 in credential_protection and the agility-debt set (verified 2026-09-26)
- [x] EV charging kept in the PQC scope (the companion report excludes it) (verified 2026-09-26)
- [x] Vendor list: companion top-10 minus Festo Didactic, plus SEL (verified 2026-09-26)

## Authors, prose, release
- [x] AUTHORS.json order and roles confirmed by each co-author (verified 2026-09-26)
- [x] Every sentence rewritten or approved in your own voice, particularly the Summary and Section 4 (verified 2026-09-26)
- [x] DOI reserved: 10.5281/zenodo.22975133; companion DOI 10.5281/zenodo.22974795 set in report/report_meta.json (2026-09-26); release_date still to set
- [x] `./run_all.sh --final` built v1.0.0 on the author's computer 2026-09-26; publish gate clear
- [x] Evidence log row written the day of release (2026-09-26)
