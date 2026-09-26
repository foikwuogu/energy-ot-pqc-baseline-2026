#!/usr/bin/env python3
"""Step 3 - compute the baseline indicators; write report/stats.json, tables and the QA report."""
import datetime
import json
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "data", "processed")
INP = os.path.join(ROOT, "data", "raw", "inputs")
C = os.path.join(ROOT, "config")
T = os.path.join(ROOT, "report", "tables")
os.makedirs(T, exist_ok=True)
CFG = json.load(open(os.path.join(C, "scope.json"), encoding="utf-8"))
CW = json.load(open(os.path.join(C, "crypto_cwe_map.json"), encoding="utf-8"))
LOG = json.load(open(os.path.join(P, "build_log.json"), encoding="utf-8"))
Y = CFG["windows"]["edition_year"]
Y0 = CFG["windows"]["trend_start_year"]
BASE = datetime.date.fromisoformat(CFG["baseline_date"])


def pct(n, d):
    return round(100.0 * n / d, 1) if d else None


def main():
    a = pd.read_csv(os.path.join(P, "energy_advisories_crypto.csv"), parse_dates=["release_date"])
    for c in [c for c in a.columns if c.startswith("cat_")] + ["any_crypto", "agility_debt", "in_ytd_window", "ev_charging"]:
        a[c] = a[c].astype(str).str.lower().eq("true")
    cats = list(CW["categories"].keys())
    S = {"edition": Y, "baseline_date": CFG["baseline_date"], "snapshot_cutoff": CFG["windows"]["snapshot_cutoff"],
         "ytd_label": "1 Jan - 10 Sep", "build": LOG,
         "inputs": {"ong_doi": "10.5281/zenodo.22729882", "crosswalk_doi": "10.5281/zenodo.22730718",
                    "cbom_repo": "https://github.com/foikwuogu/cbom-builder", "sources_pulled": "2026-09-12"},
         "category_labels": {k: v["label"] for k, v in CW["categories"].items()}}

    def blk(s):
        n = len(s)
        return {"advisories": int(n), "any_crypto": int(s.any_crypto.sum()), "any_crypto_pct": pct(int(s.any_crypto.sum()), n),
                "agility_debt": int(s.agility_debt.sum()), "agility_debt_pct": pct(int(s.agility_debt.sum()), n),
                "categories": {k: int(s[f"cat_{k}"].sum()) for k in cats},
                "categories_pct": {k: pct(int(s[f"cat_{k}"].sum()), n) for k in cats},
                "vendors_with_crypto_weakness": int(s[s.any_crypto].vendor.nunique())}

    cur = a[(a.release_year == Y) & a.in_ytd_window]
    prv = a[(a.release_year == Y - 1) & a.in_ytd_window]
    hist = a[(a.release_year >= Y0) & (a.release_year < Y)]
    S["ytd_current"] = blk(cur)
    S["ytd_current_excl_ev"] = blk(cur[~cur.ev_charging])
    S["ytd_current_ev_only"] = blk(cur[cur.ev_charging])
    S["ytd_prior"] = blk(prv)
    S["hist"] = blk(hist)
    S["hist_years"] = f"{Y0}-{Y-1}"

    rows = []
    for yr in range(Y0, Y + 1):
        s = a[a.release_year == yr]
        if yr == Y:
            s = s[s.in_ytd_window]
        rows.append({"year": yr, "advisories": int(len(s)), "any_crypto": int(s.any_crypto.sum()), "any_crypto_pct": pct(int(s.any_crypto.sum()), len(s)),
                     "agility_debt_pct": pct(int(s.agility_debt.sum()), len(s)),
                     "hardcoded_secrets_pct": pct(int(s.cat_hardcoded_secrets.sum()), len(s)),
                     "no_encryption_pct": pct(int(s.cat_no_encryption.sum()), len(s))})
    pd.DataFrame(rows).to_csv(os.path.join(T, "t1_crypto_weakness_by_year.csv"), index=False)
    S["trend"] = rows
    hp = [r["any_crypto_pct"] for r in rows if r["year"] < Y]
    S["trend_summary"] = {"min_pct": min(hp), "max_pct": max(hp), "mean_pct_unweighted": round(sum(hp) / len(hp), 1)}

    ct = pd.DataFrame([{"category": k, "label": CW["categories"][k]["label"], "cwes": ", ".join(f"CWE-{c}" for c in CW["categories"][k]["cwes"]),
                        "ytd_current": S["ytd_current"]["categories"][k], "ytd_current_pct": S["ytd_current"]["categories_pct"][k],
                        "hist": S["hist"]["categories"][k], "hist_pct": S["hist"]["categories_pct"][k]} for k in cats])
    ct.to_csv(os.path.join(T, "t2_crypto_categories.csv"), index=False)

    vt = cur[cur.any_crypto].groupby("vendor").size().sort_values(ascending=False)
    S["crypto_vendors_ytd_top"] = [{"vendor": k, "advisories": int(v)} for k, v in vt.head(8).items()]

    # --- crosswalk layers --------------------------------------------------
    cb = pd.read_csv(os.path.join(INP, "cbom_component_crosswalk_v0.1.0.csv"))
    qt = cb.quantum_threat.value_counts()
    S["cbom"] = {"components": int(len(cb)), "broken_by_shor": int(qt.get("broken-by-shor", 0)),
                 "weakened_by_grover": int(qt.get("weakened-by-grover", 0)), "no_crypto": int(qt.get("no-crypto", 0)),
                 "cnsa2_exclusive_2030": int((pd.to_numeric(cb.cnsa2_exclusive_by, errors="coerce") == 2030).sum())}
    pc = pd.read_csv(os.path.join(C, "protocol_pqc_status.csv"))
    S["protocols"] = {"families": int(len(pc)), "with_quantum_vulnerable_asymmetric": int(pc.uses_quantum_vulnerable_asymmetric_crypto.str.startswith("yes").sum()),
                      "with_published_pqc_mechanism": int((pc.published_pqc_mechanism_in_standard == "yes").sum())}
    xw = pd.read_csv(os.path.join(INP, "pqc_protocol_crosswalk_v1.0.csv"))
    S["crosswalk"] = {"rows": int(len(xw)), "protocols": int(xw.protocol.nunique())}

    tl = pd.read_csv(os.path.join(INP, "pqc_policy_timeline_v1.0.csv"))
    def yrs_to(date_str):
        d = datetime.date.fromisoformat(date_str)
        return round((d - BASE).days / 365.25, 1)
    S["deadlines"] = {
        "omb_tls13": {"date": "2030-01-02", "years_from_baseline": yrs_to("2030-01-02")},
        "eo14412_key_establishment": {"date": "2030-12-31", "years_from_baseline": yrs_to("2030-12-31")},
        "eo14412_signatures": {"date": "2031-12-31", "years_from_baseline": yrs_to("2031-12-31")},
        "omb_phase5_complete": {"date": "2035", "years_from_baseline": round(2035 - (BASE.year + (BASE.timetuple().tm_yday / 365.25)), 1)},
    }
    S["timeline_events"] = int(len(tl))
    ps = pd.read_csv(os.path.join(C, "policy_signals.csv"))
    S["policy_signals"] = ps.fillna("").to_dict("records")
    vs = pd.read_csv(os.path.join(C, "vendor_pqc_scan.csv"))
    lv = vs.signal_level.value_counts()
    S["vendor_scan"] = {"vendors": int(len(vs)), "product_level_pqc": int(lv.get("product_level_pqc", 0)),
                        "research_or_ecosystem": int(lv.get("research_or_ecosystem", 0)), "general_guidance": int(lv.get("general_guidance", 0)),
                        "legacy_quantum_safe_claim": int(lv.get("legacy_quantum_safe_claim", 0)), "none_found": int(lv.get("none_found", 0)),
                        "rows": vs.fillna("").to_dict("records")}
    S["cisa_pqc_categories_ot"] = 0  # from config/policy_signals.csv row 2026-01-26; re-check list at release

    # --- indicator table (the baseline itself) -------------------------------
    cu, pr = S["ytd_current"], S["ytd_prior"]
    ind = [
        ("I1", "Energy OT protocol families whose security standard relies on quantum-vulnerable asymmetric cryptography", f"{S['protocols']['with_quantum_vulnerable_asymmetric']} of {S['protocols']['families']}", "config/protocol_pqc_status.csv"),
        ("I2", "Energy OT protocol families with a published PQC mechanism in the standard", f"{S['protocols']['with_published_pqc_mechanism']} of {S['protocols']['families']}", "config/protocol_pqc_status.csv"),
        ("I3", "OT cryptographic components broken by Shor's algorithm (CBOM crosswalk)", f"{S['cbom']['broken_by_shor']} of {S['cbom']['components']}", "CBOM Builder v0.1.0 crosswalk"),
        ("I4", f"Energy OT advisories citing any cryptographic weakness, {Y} ({S['ytd_label']})", f"{cu['any_crypto_pct']}% ({cu['any_crypto']} of {cu['advisories']})", "code/02-03"),
        ("I5", f"Energy OT advisories citing a crypto-agility-debt weakness, {Y}", f"{cu['agility_debt_pct']}% ({cu['agility_debt']} of {cu['advisories']})", "code/02-03"),
        ("I6", f"Energy OT advisories citing hard-coded keys or credentials, {Y}", f"{cu['categories_pct']['hardcoded_secrets']}% ({cu['categories']['hardcoded_secrets']})", "code/02-03"),
        ("I7", "OT/ICS categories on CISA's PQC product-categories list", f"{S['cisa_pqc_categories_ot']}", "config/policy_signals.csv"),
        ("I8", "Top energy OT vendors with a public, product-level PQC availability statement (desk scan)", f"{S['vendor_scan']['product_level_pqc']} of {S['vendor_scan']['vendors']}", "config/vendor_pqc_scan.csv"),
        ("I9", "Years from baseline to the federal key-establishment migration deadline (EO 14412, high-value systems)", f"{S['deadlines']['eo14412_key_establishment']['years_from_baseline']}", "PQC crosswalk v1.0 timeline"),
    ]
    S["indicators"] = [{"id": i, "indicator": t, "value_2026": v, "source": s} for i, t, v, s in ind]
    pd.DataFrame(S["indicators"]).to_csv(os.path.join(T, "t0_baseline_indicators.csv"), index=False)

    json.dump(S, open(os.path.join(ROOT, "report", "stats.json"), "w"), indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o))

    q = [f"QA report - PQC readiness of the energy OT stack: a {Y} baseline", ""]
    q += [f"  {k:45s} {v}" for k, v in LOG.items()]
    q.append(f"  CHECK master rows = input/2: {'PASS' if LOG['master_rows'] * 2 == LOG['input_rows'] else 'FAIL'}")
    q.append(f"  CHECK category counts <= advisories: {'PASS' if all(v <= cu['advisories'] for v in cu['categories'].values()) else 'FAIL'}")
    q.append(f"  CHECK EV + non-EV = all ({S['ytd_current_ev_only']['advisories']} + {S['ytd_current_excl_ev']['advisories']} = {cu['advisories']}): {'PASS' if S['ytd_current_ev_only']['advisories'] + S['ytd_current_excl_ev']['advisories'] == cu['advisories'] else 'FAIL'}")
    q.append(f"  CHECK CBOM threat classes sum: {'PASS' if S['cbom']['broken_by_shor'] + S['cbom']['weakened_by_grover'] + S['cbom']['no_crypto'] == S['cbom']['components'] else 'FAIL'}")
    q.append("\nINDICATORS")
    q += [f"  {r['id']} {r['value_2026']:>22}  {r['indicator']}" for r in S["indicators"]]
    q.append("\nSPOT CHECKS - open each advisory on cisa.gov and confirm the listed crypto CWE appears")
    sp = cur[cur.any_crypto].sort_values("ICS-CERT_Number")
    for _, r in pd.concat([sp.head(4), sp.sample(min(4, len(sp)), random_state=2026)]).drop_duplicates("ICS-CERT_Number").iterrows():
        q.append(f"  {r['ICS-CERT_Number']} | {r['vendor']} | {str(r['title'])[:50]} | crypto CWEs: {r['crypto_cwes']}")
    open(os.path.join(P, "qa_report.txt"), "w", encoding="utf-8").write("\n".join(q) + "\n")
    print("\n".join(q))


if __name__ == "__main__":
    main()
