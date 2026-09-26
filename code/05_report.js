// Step 5 - build the technical report from report/stats.json (numbers) and config/*.csv (curated tables).
//   node code/05_report.js [--final]
const fs = require("fs");
const path = require("path");
const L = require("./lib_docx");

const ROOT = path.resolve(__dirname, "..");
const S = JSON.parse(fs.readFileSync(path.join(ROOT, "report", "stats.json"), "utf8"));
const M = JSON.parse(fs.readFileSync(path.join(ROOT, "report", "report_meta.json"), "utf8"));
const A = JSON.parse(fs.readFileSync(path.join(ROOT, "AUTHORS.json"), "utf8"));
const FINAL = process.argv.includes("--final");
const FIG = (f) => path.join(ROOT, "report", "figures", f);

function csv(file) { // minimal RFC4180 reader (quoted fields with commas)
  const txt = fs.readFileSync(path.join(ROOT, file), "utf8").trim();
  const rows = []; let row = [], f = "", q = false;
  for (let i = 0; i < txt.length; i++) {
    const c = txt[i];
    if (q) { if (c === '"' && txt[i + 1] === '"') { f += '"'; i++; } else if (c === '"') q = false; else f += c; }
    else if (c === '"') q = true; else if (c === ",") { row.push(f); f = ""; }
    else if (c === "\n") { row.push(f); rows.push(row); row = []; f = ""; } else if (c !== "\r") f += c;
  }
  row.push(f); rows.push(row);
  const h = rows[0];
  return rows.slice(1).map((r) => Object.fromEntries(h.map((k, i) => [k, r[i] || ""])));
}

const n = (x) => (x == null ? "n/a" : Number(x).toLocaleString("en-US"));
const p = (x) => (x == null ? "n/a" : `${Number(x).toFixed(1)}%`);
const Y = S.edition, W = S.ytd_label;
const cu = S.ytd_current, cx = S.ytd_current_excl_ev, ce = S.ytd_current_ev_only, pr = S.ytd_prior, hi = S.hist;
const cb = S.cbom, pc = S.protocols, vs = S.vendor_scan, dl = S.deadlines, lab = S.category_labels;
const doi = M.doi ? `https://doi.org/${M.doi}` : "[DOI - reserve on Zenodo, paste into report/report_meta.json]";
const companion = M.companion_doi ? `https://doi.org/${M.companion_doi}` : "[DOI of the companion annual report]";
const people = [...A.authors, ...A.collaborators];
const kids = []; const add = (...xs) => xs.flat().forEach((x) => kids.push(x));

// ---------- title ----------
add(new L.Paragraph({ spacing: { before: 1400, after: 120 }, children: [new L.TextRun({ text: M.title, bold: true, size: 44, color: "1C5CAB" })] }));
add(new L.Paragraph({ spacing: { after: 360 }, children: [new L.TextRun({ text: `${M.subtitle}. Baseline date ${S.baseline_date}; advisory evidence through ${S.snapshot_cutoff}.`, size: 24, color: L.INK2 })] }));
if (!FINAL) add(L.BANNER("DRAFT for author verification. Not for citation or circulation. Every indicator, curated table row and judgment call must be checked against docs/VERIFY_CHECKLIST.md before release."));
people.forEach((a) => {
  add(new L.Paragraph({ spacing: { after: 20 }, children: [new L.TextRun({ text: a.name + (a.corresponding ? " (corresponding author)" : ""), bold: true, size: 21 })] }));
  add(new L.Paragraph({ spacing: { after: 140 }, children: [new L.TextRun({ text: [a.affiliation, a.orcid ? `ORCID ${a.orcid}` : "", a.email].filter(Boolean).join(" · "), size: 18, color: L.INK2 })] }));
});
add(L.RULEPARA());
add(L.P(`**Version** ${M.version}${FINAL ? "" : " (draft)"} · **Release date** ${M.release_date || "set at release"} · **DOI** ${doi}`));
add(L.P(`**Inputs** ONG-OT Vulnerability Prioritization Dataset v1.1 (doi:${S.inputs.ong_doi}); PQC Readiness Crosswalk for Energy OT Protocols and Identity Systems v1.0 (doi:${S.inputs.crosswalk_doi}); CBOM Builder v0.1.0 component crosswalk (${S.inputs.cbom_repo}).`));
add(L.P(`**Series** ${M.series_note}`));
add(L.P(`**License** ${M.license}`));
add(L.P(`**Suggested citation** ${people.map((a) => `${a.family}, ${a.given.split(" ").map((g) => g[0] + ".").join(" ")}`).join(", ")} (${Y}). _${M.title}_. ${M.subtitle}, v${M.version}. Zenodo. ${doi}`));
add(L.PB());

// ---------- summary ----------
add(L.H1("Summary"));
add(L.P(`Energy-sector operational technology (OT) will have to move from RSA and elliptic-curve cryptography to the NIST post-quantum algorithms (ML-KEM, ML-DSA, SLH-DSA; FIPS 203/204/205). Nobody yet measures how far along that move is. This report sets a baseline of ${S.indicators.length} indicators that can be re-measured each year from public sources. The baseline values, as of ${S.baseline_date}, are:`));
add(L.BUL(`**Standards have not started.** All ${pc.with_quantum_vulnerable_asymmetric} of the ${pc.families} energy OT protocol families examined rely on quantum-vulnerable public-key cryptography wherever they are secured, and ${pc.with_published_pqc_mechanism} of ${pc.families} has a published post-quantum mechanism in its security standard.`));
add(L.BUL(`**Most of the cryptography in use breaks.** ${cb.broken_by_shor} of ${cb.components} catalogued OT cryptographic components (TLS handshakes, device identity certificates, firmware signatures, DNP3 authority keys, OPC UA security policies) use algorithms that Shor's algorithm breaks. ${cb.weakened_by_grover} use symmetric algorithms that only need adequate key sizes, and ${cb.no_crypto} use no cryptography at all.`));
add(L.BUL(`**Crypto-agility debt is visible in the advisory record.** ${p(cu.any_crypto_pct)} of energy OT advisories in ${W} ${Y} cite a cryptographic weakness (${p(cx.any_crypto_pct)} excluding EV-charging platforms), against ${p(pr.any_crypto_pct)} in the same window of ${Y - 1} and ${p(hi.any_crypto_pct)} pooled over ${S.hist_years}. Hard-coded keys or credentials appear in ${p(cu.categories_pct.hardcoded_secrets)} of ${Y} advisories.`));
add(L.BUL(`**The federal program has no OT lane yet.** CISA's January 2026 list of product categories with PQC support names ${S.cisa_pqc_categories_ot} OT or ICS categories and puts OT explicitly out of scope. In a desk scan of ${vs.vendors} major energy OT vendors, ${vs.product_level_pqc} publish a product-level PQC availability statement.`));
add(L.BUL(`**The clock is set by federal deadlines energy does not own.** The federal deadline for moving high-value systems' key establishment to PQC is ${dl.eo14412_key_establishment.years_from_baseline} years from this baseline, and full federal migration is targeted for ${dl.omb_phase5_complete.date}. OT devices bought today will typically still be in service after both dates.`));
add(L.H2("Table 1. The 2026 baseline indicators"));
add(L.TABLE(["ID", "Indicator", `Value, ${Y}`], S.indicators.map((r) => [r.id, r.indicator, r.value_2026]), [700, 6760, 1900]));
add(L.CAP(`Table 1. Each indicator's source and refresh method are in Section 6. Source: report/stats.json, report/tables/t0_baseline_indicators.csv.`));
add(L.PB());

// ---------- 1 ----------
add(L.H1("1. Why a baseline, and why for OT"));
add(L.P(`The quantum risk to OT is less about eavesdropping on today's control traffic than about **authenticity over long lifetimes**. The public-key signatures and certificates that authenticate a firmware image, a device identity or a TLS session in an RTU installed this year may still be relied on in the late 2030s or beyond. If a cryptographically relevant quantum computer exists by then, an attacker could forge them. Confidentiality matters too, for engineering data, credentials and market-sensitive telemetry that may be recorded now and decrypted later. But the defining OT problem is that cryptography is fixed into firmware and hardware that is replaced on decade timescales.`));
add(L.P(`Federal agencies now have a PQC timetable, while critical-infrastructure operators have guidance and no deadline. Without a measured starting point, statements such as "energy OT is behind on PQC" cannot be tested or tracked. This report defines indicators that anyone can re-derive from public sources and records their ${Y} values. It is a companion to _State of OT Vulnerability Exposure in US Oil and Natural Gas, ${Y}_ (${companion}) and shares its advisory snapshot and de-duplication.`));

// ---------- 2 ----------
add(L.H1("2. Method"));
add(L.P(`The baseline has four layers, each built from a different public source.`));
add(L.NUM1(`**Protocol standards (I1, I2).** For each energy OT protocol family, does its security standard use quantum-vulnerable public-key cryptography, and has the standard published a post-quantum mechanism? The source is the authors' PQC Readiness Crosswalk v1.0 (${S.crosswalk.rows} rows across ${S.crosswalk.protocols} protocol and identity entries, author-verified against primary standards on 2026-09-09), summarised in config/protocol_pqc_status.csv.`));
add(L.NUM1(`**Cryptographic components (I3).** The ${cb.components} OT cryptographic components catalogued in the CBOM Builder v0.1.0 crosswalk, each classified as broken by Shor's algorithm, weakened by Grover's algorithm, or using no cryptography.`));
add(L.NUM1(`**Disclosed cryptographic weaknesses (I4-I6).** CISA ICS advisories in energy OT scope, de-duplicated as in the companion report (${n(S.build.unique_pairs)} unique CVE-advisory pairs; ${n(S.build.advisories_in_scope)} advisories in scope), flagged when they cite a cryptographic CWE. The CWEs are grouped into the categories in config/crypto_cwe_map.json. "Crypto-agility debt" is the subset of categories that show cryptography fixed, weak or mishandled in the product: weak algorithms, hard-coded secrets, unprotected credentials, key management, certificate or signature validation, randomness. Missing encryption is reported separately, because a product with no cryptography has nothing to migrate and must adopt cryptography first. Scope matches the companion report except that EV-charging platforms are kept, since charge-point management runs on TLS and PKI, and they are reported separately where they move a number.`));
add(L.NUM1(`**Ecosystem signals (I7-I9).** Federal and industry PQC instruments (config/policy_signals.csv; timeline from the crosswalk v1.0), and a desk scan of public PQC statements by ${vs.vendors} major energy OT vendors (config/vendor_pqc_scan.csv). The vendor list is the companion report's top vendors by ${Y} advisories, dropping a training-equipment supplier and adding Schweitzer Engineering Laboratories for US grid coverage. The scan used web search and vendor newsrooms on ${S.baseline_date}. It records what is publicly findable, which is not the same as what vendors are doing.`));

// ---------- 3 ----------
add(L.H1("3. Findings"));
add(L.H2("3.1 Protocol standards: every secured protocol depends on quantum-vulnerable keys"));
add(L.P(`Where energy OT protocols are secured, they are secured with RSA, ECDH or ECDSA. This covers TLS profiles (IEC 62351-3) for IEC 60870-5-104, DNP3 and ICCP, Modbus/TCP Security's mandatory ECDHE-RSA suite, OPC UA's RSA security policies, the X.509 certificates behind IEC 61850 GOOSE, Sampled Values and MMS, and the authority keys in DNP3 SAv6. None of the ${pc.families} families' security standards has published a post-quantum mechanism (Table 2). A research effort to add PQC to OPC UA exists (the PQCUA consortium proposal, 2025), but it is not a published security policy.`));
const pst = csv("config/protocol_pqc_status.csv");
add(L.TABLE(["Protocol family", "Security standard", "Quantum-vulnerable public-key crypto", "PQC mechanism published"],
  pst.map((r) => [r.protocol_family, r.security_standard, r.uses_quantum_vulnerable_asymmetric_crypto, r.published_pqc_mechanism_in_standard]), [1900, 2700, 3160, 1600]));
add(L.CAP(`Table 2. Protocol standards status. Basis for each row: config/protocol_pqc_status.csv and the PQC Readiness Crosswalk v1.0.`));
add(L.P(`The practical consequence is that no energy OT operator can buy a standards-conformant, post-quantum version of these protocols today. The available route is the one the crosswalk describes: wrap the protocol in a TLS 1.3 tunnel that carries a hybrid classical and ML-KEM key exchange, once OT vendors' TLS stacks support it. That leaves authentication, signatures and certificates, the harder half, dependent on PKI changes across substations, pipelines and control centres.`));

add(L.H2("3.2 Components: most of the cryptography breaks, some needs only larger keys"));
add(L.P(`${cb.broken_by_shor} of ${cb.components} catalogued components rely on RSA, elliptic-curve or EdDSA public keys (Figure 1). These are the TLS handshakes of OT protocols and MQTT gateways, IEEE 802.1AR device identity certificates, firmware and software update signatures, OPC UA security policies and DNP3 SAv6 authority keys. Each must move to ML-KEM for key establishment and ML-DSA or SLH-DSA, or stateful hash-based signatures for firmware, for authentication. ${cb.weakened_by_grover} components (DNP3 SAv5 HMAC, DNP3 SAv6 session AES-GCM, SNMPv3) use symmetric cryptography that stays sound with 256-bit keys. ${cb.no_crypto} (base Modbus and cleartext management protocols) have no cryptography to migrate. Under NSA's CNSA 2.0 schedule, ${cb.cnsa2_exclusive_2030} of the Shor-vulnerable components fall in categories expected to use CNSA 2.0 algorithms exclusively by 2030. That schedule binds national security systems, and the report uses it as a reference point only.`));
add(L.FIG(FIG("fig1_cbom_quantum_threat.png"), `Figure 1. OT cryptographic components by quantum threat class (CBOM Builder v0.1.0 crosswalk, ${cb.components} components).`));

add(L.H2("3.3 Disclosed weaknesses: crypto-agility debt in the advisory record"));
add(L.P(`Across ${S.hist_years}, ${p(hi.any_crypto_pct)} of energy OT advisories cited at least one cryptographic weakness, with year-to-year values between ${p(S.trend_summary.min_pct)} and ${p(S.trend_summary.max_pct)} (Figure 2). In ${W} ${Y} the share is ${p(cu.any_crypto_pct)} (${n(cu.any_crypto)} of ${n(cu.advisories)} advisories), against ${p(pr.any_crypto_pct)} in the same window of ${Y - 1}. EV-charging platforms account for part of the rise: ${n(ce.any_crypto)} of the ${n(ce.advisories)} EV-charging advisories in ${Y} cite a cryptographic weakness, mostly unprotected credentials. Without them the ${Y} share is ${p(cx.any_crypto_pct)}, still above both the ${Y - 1} window and the historical pool.`));
add(L.FIG(FIG("fig2_crypto_weakness_trend.png"), `Figure 2. Share of energy OT advisories citing a cryptographic CWE (${Y}: ${W}). The dashed line is the pooled ${S.hist_years} share.`));
add(L.P(`The category mix (Figure 3) matters more for PQC than the total. Hard-coded keys or credentials (${p(cu.categories_pct.hardcoded_secrets)} of ${Y} advisories) and unprotected credentials (${p(cu.categories_pct.credential_protection)}) show secrets fixed into firmware or stored and sent without protection. Products with these weaknesses cannot rotate keys. They therefore cannot replace an RSA key with an ML-DSA key in the field without a firmware release, and often not without new hardware. Weak or broken algorithms (${p(cu.categories_pct.weak_or_broken_algorithm)}) and missing certificate or signature validation (${p(cu.categories_pct.cert_signature_validation)}) show that classical cryptography is not yet implemented soundly in some products, and PQC migration inherits that gap. ${p(cu.agility_debt_pct)} of ${Y} energy OT advisories carry at least one crypto-agility-debt weakness (indicator I5), spread over ${n(cu.vendors_with_crypto_weakness)} vendors.`));
add(L.FIG(FIG("fig3_crypto_categories.png"), `Figure 3. Cryptographic weakness categories as shares of energy OT advisories: ${Y} (${W}, blue) against ${S.hist_years} (orange). An advisory can cite several categories.`));

add(L.H2("3.4 Ecosystem: guidance without an OT lane"));
add(L.P(`The federal PQC program is advancing on a fixed calendar (Figure 4), but so far none of its instruments specifically covers OT. CISA's 2024 _Post-Quantum Considerations for Operational Technology_ recommends segmentation, crypto-agility and early planning, and sets no deadline. CISA's January 2026 PQC product-categories list, which is meant to steer procurement toward PQC-capable products, names cloud, networking, identity, PKI and endpoint categories and ${S.cisa_pqc_categories_ot} OT or ICS categories. CISA states that OT and IoT devices "are outside the current scope" (Table 3). The federal deadlines in the authors' crosswalk timeline (TLS 1.3 by ${dl.omb_tls13.date}, key establishment for high-value systems by ${dl.eo14412_key_establishment.date}, signatures by ${dl.eo14412_signatures.date}, full migration by ${dl.omb_phase5_complete.date}) bind federal systems. They reach energy operators only through procurement, vendor road maps and any future sector rule.`));
add(L.FIG(FIG("fig4_policy_timeline.png"), `Figure 4. Federal PQC milestones relative to this baseline. Dates are from the PQC Readiness Crosswalk v1.0 timeline (author-verified 2026-09-09).`));
const ps = csv("config/policy_signals.csv");
add(L.TABLE(["Date", "Instrument", "What it says about OT", "Binding on energy operators"], ps.map((r) => [r.date, r.instrument, r.what_it_says_about_ot, r.binding_on_energy_operators]), [1100, 2800, 4000, 1460]));
add(L.CAP(`Table 3. PQC policy and industry signals relevant to OT, beyond the crosswalk timeline. Source: config/policy_signals.csv.`));
add(L.P(`Among vendors (Table 4), the desk scan found ${vs.product_level_pqc} product-level PQC availability statements from the ${vs.vendors} vendors examined. It found ${vs.research_or_ecosystem} research or ecosystem statement, ${vs.general_guidance} general-guidance article, and ${vs.legacy_quantum_safe_claim} older "quantum-safe" marketing claim that describes symmetric encryption with physically random keys rather than a NIST PQC algorithm. For ${vs.none_found} vendors the scan found nothing public. That is a finding about public disclosure, not about vendors' internal road maps, and the next edition should test it with direct vendor inquiries.`));
add(L.TABLE(["Vendor", "Public PQC signal found", "Level", "Date"], vs.rows.map((r) => [r.vendor, r.public_pqc_signal, r.signal_level.replace(/_/g, " "), r.evidence_date || "n/a"]), [2000, 5000, 1400, 960]));
add(L.CAP(`Table 4. Desk scan of public PQC statements, ${S.baseline_date}. Evidence URLs are in config/vendor_pqc_scan.csv. Absence of a public statement is not evidence of absence of work.`));
add(L.PB());

// ---------- 4 ----------
add(L.H1("4. Reading the baseline"));
add(L.P(`Taken together, the indicators describe an OT stack whose cryptography is known and catalogued, but whose standards, products and procurement signals have not yet started moving. The measurements suggest an order of work for the period before sector rules arrive. These are implications of the baseline, not prescriptions.`));
add(L.BUL(`**Inventory first.** Signatures and device identities (firmware signing, 802.1AR certificates, PKI roots) have the longest lifetimes and the hardest migrations, and they account for most of the Shor-vulnerable components. A cryptographic bill of materials covering them is the prerequisite for everything else. CISA's CBOM guidance for critical infrastructure, expected around December ${Y} under EO 14412, should be checked against this baseline when it appears.`));
add(L.BUL(`**Fix crypto-agility debt now.** Hard-coded keys and unprotected credentials block key rotation today, and they will block algorithm replacement later. Treating these advisory classes as PQC-readiness blockers, and not only as ordinary vulnerabilities, links present patching to future migration.`));
add(L.BUL(`**Use TLS 1.3 hybrid tunnels as the near-term path for TCP-based protocols.** For IEC 60870-5-104, DNP3 over TCP, ICCP and Modbus/TCP, a TLS 1.3 layer with hybrid ML-KEM key exchange is the route that does not wait for protocol committees. Serial and bandwidth-constrained links, and the multicast GOOSE and Sampled Values messages with tight latency budgets, need separate engineering study.`));
add(L.BUL(`**Ask vendors for road maps in procurement.** With no OT categories on CISA's PQC list and no public product commitments found, the lever operators hold is procurement language. That means ML-DSA or hash-based firmware signing, field-updatable trust anchors, and crypto-agile TLS stacks.`));

// ---------- 5 ----------
add(L.H1("5. Limitations"));
[
  `**Proxies, not direct measurement.** No public dataset records which OT devices run which algorithms in the field. Every indicator here is a proxy: of standards status, catalogued component classes, disclosed weaknesses or public statements.`,
  `**CWE assignment is advisory-level and uneven.** CISA assigns CWEs per advisory. A cryptographic CWE may apply to one of several products in an advisory, and assignment practice has changed over time.`,
  `**Category mapping is a judgment.** Which CWEs count as cryptographic, and which count as crypto-agility debt, is set in config/crypto_cwe_map.json and can be argued either way. CWE-522 (unprotected credentials) in particular is only partly a cryptographic weakness.`,
  `**Crosswalk inputs are the authors' own.** Layers 1 and 2 reuse the authors' previously published crosswalk and CBOM Builder catalogue, so they inherit those works' limitations. Primary IEC and IEEE standards are paywalled, and the PQC replacement columns are projections rather than published standards.`,
  `**Federal instruments post-date some general references.** The EO 14412 and OMB M-26-15 dates come from the crosswalk timeline verified on 2026-09-09. Their status should be re-confirmed at release and at each refresh.`,
  `**The vendor scan is shallow by design.** It is a reproducible desk scan of public statements on one date, not a survey. It can miss statements in customer portals, product documentation and conference talks.`,
].forEach((t) => add(L.NUM2(t)));

// ---------- 6 ----------
add(L.H1("6. Re-measurement plan"));
add(L.TABLE(["ID", "How to refresh next year"], [
  ["I1-I2", "Re-check each protocol family's security standard (IEC 62351 parts, IEEE 1815, OPC 10000-7, Modbus/TCP Security) for a published PQC mechanism; update config/protocol_pqc_status.csv."],
  ["I3", "Re-run against the current CBOM Builder crosswalk; report additions separately so the ratio stays comparable."],
  ["I4-I6", "Re-run code/02-03 on the next frozen advisory snapshot with config/crypto_cwe_map.json unchanged; report any mapping change as a sensitivity."],
  ["I7", "Re-read CISA's PQC product-categories list for OT or ICS categories."],
  ["I8", "Repeat the desk scan on the same vendor list and add a direct vendor inquiry."],
  ["I9", "Recompute from the baseline date; add any sector-specific instrument (for example FERC, TSA or DOE action) as a new indicator."],
], [900, 8460]));
add(L.CAP(`Table 5. Refresh method for each indicator.`));

// ---------- back matter ----------
add(L.H1("Declarations"));
add(L.P(`**Data and code availability.** ${M.repository}; ${doi}. Inputs: doi:${S.inputs.ong_doi}; doi:${S.inputs.crosswalk_doi}; ${S.inputs.cbom_repo}.`));
add(L.P(`**Author contributions (CRediT).** ${people.map((a) => `${a.name}: ${a.roles.join(", ")}`).join(". ")}.`));
add(L.P(`**Competing interests.** The authors also maintain the crosswalk and CBOM Builder inputs used here. No other interests declared.`));
add(L.P(`**Funding.** No external funding.`));
add(L.P(`**Use of AI tools.** An AI assistant (Claude, Anthropic) was used to write analysis code, draft figures, run the vendor desk scan and draft text. The authors specified the indicators, made every mapping and scope decision recorded in config/, verified each curated row against its cited source, and take full responsibility for the content.`));
add(L.H1("References"));
[
  `National Institute of Standards and Technology (2024). FIPS 203, Module-Lattice-Based Key-Encapsulation Mechanism Standard; FIPS 204, Module-Lattice-Based Digital Signature Standard; FIPS 205, Stateless Hash-Based Digital Signature Standard. https://csrc.nist.gov/projects/post-quantum-cryptography`,
  `National Institute of Standards and Technology (2024). NIST IR 8547 (initial public draft), Transition to Post-Quantum Cryptography Standards. https://nvlpubs.nist.gov/nistpubs/ir/2024/NIST.IR.8547.ipd.pdf`,
  `Cybersecurity and Infrastructure Security Agency (2024). Post-Quantum Considerations for Operational Technology. https://www.cisa.gov/sites/default/files/2024-10/Post-Quantum%20Considerations%20for%20Operational%20Technology%20%28508%29.pdf`,
  `Cybersecurity and Infrastructure Security Agency (2026). Product Categories for Technologies That Use Post-Quantum Cryptography Standards. https://www.cisa.gov/resources-tools/resources/product-categories-technologies-use-post-quantum-cryptography-standards`,
  `National Security Agency (2022). The Commercial National Security Algorithm Suite 2.0 and Quantum Computing FAQ. https://media.defense.gov/2022/Sep/07/2003071836/-1/-1/0/CSI_CNSA_2.0_FAQ_.PDF`,
  `Ikwuogu, F. O., Orimogunje, A., Pinyi, E. O., and Mike-Ewewie, D. (2026). PQC Readiness Crosswalk for Energy OT Protocols and Identity Systems, v1.0. Zenodo. https://doi.org/${S.inputs.crosswalk_doi}`,
  `Ikwuogu, F. O., Abutu, S., and Orimogunje, A. (2026). ONG-OT Vulnerability Prioritization Dataset, v1.1. Zenodo. https://doi.org/${S.inputs.ong_doi}`,
  `Ikwuogu, F. O., and Businge, P. (2026). CBOM Builder, v0.1.0. ${S.inputs.cbom_repo}`,
  `Charter of Trust PQC Working Group (2026). Decrypting the Future: Global Timelines for Post-Quantum Cryptography and Why They Matter. https://www.charteroftrust.com/wp-content/uploads/2026/04/20260115_PQC-Decrypting-the-Future_FINAL-1.pdf`,
  `Mouhtadi, R., Carlier, B., De Mulder, C., and Lebain, L. (2026). Post-Quantum Cryptography for products and OT: from trends to industrial reality. Wavestone RiskInsight. https://www.riskinsight-wavestone.com/en/2026/02/post-quantum-cryptography-for-products-ot-from-trends-to-industrial-reality/`,
  `Systerel (2025). Post-Quantum Cryptography OPC UA Initiative (PQCUA). https://www.systerel.fr/en/news/post-quantum-cryptography-opc-ua-initiative/`,
  `MITRE. Common Weakness Enumeration. https://cwe.mitre.org/`,
].forEach((t) => add(L.NUM3(t)));

add(L.PB());
add(L.H1("Appendix A. Cryptographic CWE categories"));
const t2 = csv("report/tables/t2_crypto_categories.csv");
add(L.TABLE(["Category", "CWEs", `${Y} advisories (${W})`, `${S.hist_years} advisories`], t2.map((r) => [r.label, r.cwes, `${r.ytd_current} (${p(r.ytd_current_pct)})`, `${r.hist} (${p(r.hist_pct)})`]), [2600, 3160, 1800, 1800]));
add(L.CAP(`Table A1. Mapping and counts. Source: config/crypto_cwe_map.json and report/tables/t2_crypto_categories.csv.`));

L.build({ outFile: path.join(ROOT, "report", `Energy_OT_PQC_Baseline_${Y}${FINAL ? "" : "_DRAFT"}.docx`), children: kids, draft: !FINAL, runningTitle: M.title })
  .then((f) => console.log("wrote", f));
