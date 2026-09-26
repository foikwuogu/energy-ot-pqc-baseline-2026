# Codebook

## data/processed/energy_advisories_crypto.csv (one row per in-scope advisory)
| Column | Definition |
|---|---|
| ICS-CERT_Number, vendor, title, cvss_severity, cwe_raw | As published by CISA via the ICS Advisory Project (advisory-level). |
| release_date, release_year, in_ytd_window | Parsed from Original_Release_Date; window 01-01 to 09-10. |
| n_cves | Unique CVEs in the advisory (after de-duplication). |
| crypto_cwes | The advisory's CWEs that appear in config/crypto_cwe_map.json. |
| cat_<category> | True if the advisory cites any CWE in that category. |
| any_crypto | Any category, including no_encryption. |
| agility_debt | Any of the agility_debt_categories. |
| ev_charging | Title/vendor matches the EV-charging pattern (kept in scope; reported separately). |

## config/
- crypto_cwe_map.json: CWE-to-category map (authors' judgment).
- protocol_pqc_status.csv: one row per protocol family, basis in the PQC crosswalk v1.0.
- policy_signals.csv: dated OT-relevant PQC instruments beyond the crosswalk timeline.
- vendor_pqc_scan.csv: desk scan of public PQC statements; signal_level in {product_level_pqc, research_or_ecosystem, general_guidance, legacy_quantum_safe_claim, none_found}.
- scope.json: scope, windows, baseline date.

## report/stats.json
indicators (I1-I9), ytd_current / ytd_current_excl_ev / ytd_current_ev_only / ytd_prior / hist blocks, trend, cbom, protocols, deadlines, policy_signals, vendor_scan.
