#!/usr/bin/env python3
"""Step 2 - de-duplicate, scope to energy OT, and flag cryptographic weaknesses per advisory.

Writes data/processed/energy_advisories_crypto.csv (one row per advisory, all years, in scope only)
       data/processed/build_log.json
"""
import json
import os
import re

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "ong_ot_dataset_v1.1.csv")
OUT = os.path.join(ROOT, "data", "processed")
CFG = json.load(open(os.path.join(ROOT, "config", "scope.json"), encoding="utf-8"))
CW = json.load(open(os.path.join(ROOT, "config", "crypto_cwe_map.json"), encoding="utf-8"))
CAT_OF = {f"CWE-{c}": k for k, v in CW["categories"].items() for c in v["cwes"]}


def main():
    os.makedirs(OUT, exist_ok=True)
    log = {}
    d = pd.read_csv(RAW, low_memory=False)
    log["input_rows"] = int(len(d))
    m = d[d["__source_file"].str.contains(CFG["dedup"]["keep_source_file_pattern"])].copy()
    log["master_rows"] = int(len(m))
    sc = CFG["scope"]
    sec = m["Critical_Infrastructure_Sector"].fillna("").str.contains(sc["sector_regex"], case=False, regex=True)
    cls = m["ong_product_class"].fillna("unmapped").ne("unmapped")
    us = m["Product_Distribution"].fillna("").str.contains(sc["us_distribution_regex"], case=False, regex=True)
    adv_in = (set(m.loc[sec | cls, "ICS-CERT_Number"])) & set(m.loc[us, "ICS-CERT_Number"])
    m = m.drop_duplicates(CFG["dedup"]["key"], keep="first")
    log["unique_pairs"] = int(len(m))
    m["release_date"] = pd.to_datetime(m["Original_Release_Date"], format="%m/%d/%Y", errors="coerce")
    w = CFG["windows"]
    md = m["release_date"].dt.strftime("%m-%d")
    m["in_ytd_window"] = (md >= w["ytd_start_month_day"]) & (md <= w["ytd_end_month_day"])
    m["in_scope"] = m["ICS-CERT_Number"].isin(adv_in)
    log["advisories_total"] = int(m["ICS-CERT_Number"].nunique())
    s = m[m.in_scope]
    g = s.groupby("ICS-CERT_Number")
    adv = pd.DataFrame({
        "release_date": g["release_date"].first(),
        "in_ytd_window": g["in_ytd_window"].first(),
        "vendor": g["Vendor"].first(),
        "title": g["ICS-CERT_Advisory_Title"].first(),
        "cvss_severity": g["CVSS_Severity"].first(),
        "cwe_raw": g["CWE_Number"].first(),
        "n_cves": g["cve_id"].nunique(),
    }).reset_index()
    adv["release_year"] = adv.release_date.dt.year
    adv["cwes"] = adv.cwe_raw.fillna("").map(lambda x: sorted(set(re.findall(r"CWE-\d+", x)), key=lambda c: int(c[4:])))
    adv["crypto_cwes"] = adv.cwes.map(lambda l: ";".join(c for c in l if c in CAT_OF))
    for k in CW["categories"]:
        adv[f"cat_{k}"] = adv.cwes.map(lambda l, k=k: any(CAT_OF.get(c) == k for c in l))
    adv["any_crypto"] = adv[[f"cat_{k}" for k in CW["categories"]]].any(axis=1)
    adv["agility_debt"] = adv[[f"cat_{k}" for k in CW["agility_debt_categories"]]].any(axis=1)
    adv["ev_charging"] = (adv.title.fillna("") + " " + adv.vendor.fillna("")).str.contains(r"charg|\bEV\b|OCPP|EVSE|wallbox", case=False, regex=True)
    adv.drop(columns=["cwes"]).to_csv(os.path.join(OUT, "energy_advisories_crypto.csv"), index=False)
    log["advisories_in_scope"] = int(len(adv))
    log["advisories_in_scope_with_any_crypto_cwe"] = int(adv.any_crypto.sum())
    json.dump(log, open(os.path.join(OUT, "build_log.json"), "w"), indent=2)
    print(json.dumps(log, indent=2))


if __name__ == "__main__":
    main()
