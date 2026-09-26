# Limitations

1. **Proxies, not direct measurement.** No public dataset records which algorithms run on fielded OT devices. Every indicator is a proxy.
2. **Advisory-level CWE.** A cryptographic CWE may apply to one of several products in an advisory, and CWE assignment practice changes over time.
3. **Category mapping is a judgment** (config/crypto_cwe_map.json). CWE-522 is only partly cryptographic, and it drives much of the 2026 rise, especially in EV-charging advisories (11 of 13).
4. **Self-sourced inputs.** Layers 1-2 reuse the authors' own crosswalk and CBOM catalogue and inherit their limitations (paywalled primary standards; projected PQC replacements).
5. **Federal dates** (EO 14412, OMB M-26-15) come from the crosswalk timeline verified 2026-09-09 and must be re-confirmed at release.
6. **Vendor scan** is a same-day desk scan of public statements, not a survey. "None found" does not mean "none exists."
7. **Network restrictions.** The build environment could not reach cisa.gov or nist.gov directly. Policy and vendor rows were read through a web-fetch tool, so there are no hashed local copies of those pages. The author must re-open each URL.
8. **Input double-ingestion** in ONG-OT v1.1 is corrected by keeping master-file rows only (see the companion report).
9. **Partial year.** The 2026 values cover 1 Jan - 10 Sep.
