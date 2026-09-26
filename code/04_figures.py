#!/usr/bin/env python3
"""Step 4 - figures from report/stats.json (DRAFT-stamped unless --final)."""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "report", "figures")
S = json.load(open(os.path.join(ROOT, "report", "stats.json"), encoding="utf-8"))
FINAL = "--final" in sys.argv
os.makedirs(FIG, exist_ok=True)
BLUE, ORANGE, B300 = "#2a78d6", "#eb6834", "#86b6ef"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
Y = S["edition"]
SRC = f"Sources: CISA ICS advisories via ONG-OT dataset v1.1 (doi:{S['inputs']['ong_doi']}); PQC crosswalk v1.0 (doi:{S['inputs']['crosswalk_doi']}); CBOM Builder v0.1.0."
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF})


def finish(fig, name, title, note=SRC):
    fig.canvas.draw()
    bb = fig.axes[0].get_tightbbox(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())
    fig.text(bb.x0, bb.y1 + 0.03, title, ha="left", va="bottom", fontsize=11, color=INK, fontweight="bold")
    fig.text(bb.x0, bb.y0 - 0.03, note, fontsize=7, color=INK2, ha="left", va="top")
    if not FINAL:
        fig.text(0.5, 0.5, "DRAFT", fontsize=70, color="#d0cfca", alpha=0.35, ha="center", va="center", rotation=25, zorder=100)
    fig.savefig(os.path.join(FIG, name), dpi=200, bbox_inches="tight")
    plt.close(fig)


def f1_trend():
    t = pd.DataFrame(S["trend"])
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    ax.bar(t.year, t.any_crypto_pct, 0.7, color=BLUE, edgecolor=SURF)
    m = S["hist"]["any_crypto_pct"]
    ax.axhline(m, color=INK2, linewidth=1, linestyle=(0, (4, 3)))
    ax.text(t.year.min() - 0.4, m + 0.8, f"{S['hist_years']} pooled: {m}%", fontsize=7.5, color=INK2)
    last = t.iloc[-1]
    ax.annotate(f"{last.any_crypto_pct}%\n({S['ytd_current_excl_ev']['any_crypto_pct']}% excl. EV charging)", (last.year, last.any_crypto_pct),
                xytext=(0, 4), textcoords="offset points", ha="center", fontsize=7.5, color=INK)
    ax.set_xticks(t.year); ax.set_xticklabels(t.year, fontsize=7.5); ax.grid(axis="x", visible=False)
    ax.set_ylim(0, max(t.any_crypto_pct) * 1.3)
    ax.set_ylabel("% of energy OT advisories")
    finish(fig, "fig2_crypto_weakness_trend.png", f"Figure 2. Energy OT advisories citing a cryptographic weakness (CWE), {t.year.min()}-{Y}")


def f2_categories():
    lab = S["category_labels"]
    cur, hist = S["ytd_current"]["categories_pct"], S["hist"]["categories_pct"]
    keys = sorted(lab, key=lambda k: cur[k])
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    for i, k in enumerate(keys):
        ax.plot([hist[k], cur[k]], [i, i], color=GRID, linewidth=2, zorder=1)
    ax.scatter([hist[k] for k in keys], range(len(keys)), s=42, color=ORANGE, edgecolor=SURF, linewidth=1.5, zorder=2, label=f"{S['hist_years']}")
    ax.scatter([cur[k] for k in keys], range(len(keys)), s=42, color=BLUE, edgecolor=SURF, linewidth=1.5, zorder=3, label=f"{Y}, {S['ytd_label']}")
    ax.set_yticks(range(len(keys))); ax.set_yticklabels([lab[k] for k in keys], fontsize=8); ax.grid(axis="y", visible=False)
    ax.set_xlabel("% of energy OT advisories citing the category")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.35, -0.16), ncol=2, fontsize=7.5)
    finish(fig, "fig3_crypto_categories.png", "Figure 3. Cryptographic weakness categories, current window against history")


def f3_cbom():
    c = S["cbom"]
    labels = ["Broken by Shor's algorithm\n(RSA, ECDH/ECDSA, EdDSA)", "Weakened by Grover's algorithm\n(AES, HMAC: key-size margin)", "No cryptography at all\n(cleartext protocols)"]
    vals = [c["broken_by_shor"], c["weakened_by_grover"], c["no_crypto"]]
    fig, ax = plt.subplots(figsize=(7.2, 2.4))
    ax.barh(labels[::-1], vals[::-1], color=BLUE, edgecolor=SURF, height=0.6)
    for i, v in enumerate(vals[::-1]):
        ax.text(v + 0.15, i, f"{v} of {c['components']}", va="center", fontsize=8, color=INK2)
    ax.set_xlim(0, c["components"]); ax.grid(axis="y", visible=False)
    ax.set_xlabel("OT cryptographic components in the CBOM crosswalk")
    finish(fig, "fig1_cbom_quantum_threat.png", "Figure 1. Quantum threat to the cryptography energy OT protocols and identities use")


def f4_timeline():
    # (date, label, vertical level); CISA's 2024 OT guidance and 2026 product list are in Table 3, not here
    ev = [("2024-08-13", "FIPS 203/204/205\nfinal", 0.7), ("2026-06-22", "EO 14412", -0.7),
          (S["baseline_date"], "This baseline", 1.5), ("2030-01-02", "Federal TLS 1.3 floor\n(OMB M-26-15)", -0.7),
          ("2030-12-31", "Federal HVA key\nestablishment (EO 14412)", 0.7), ("2031-12-31", "Federal HVA signatures\n(EO 14412)", -1.5),
          ("2035-06-30", "Federal migration\ncomplete (2035)", 0.7)]
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.axhline(0, color=INK2, linewidth=1)
    for ds, lab, lv in ev:
        x = pd.Timestamp(ds)
        base = lab == "This baseline"
        ax.plot([x, x], [0, lv * 0.9], color=GRID, linewidth=1)
        ax.scatter([x], [0], s=64 if base else 36, color=ORANGE if base else BLUE, edgecolor=SURF, linewidth=1.5, zorder=3)
        ax.text(x, lv, lab, ha="center", va="bottom" if lv > 0 else "top", fontsize=7, color=INK if base else INK2, fontweight="bold" if base else "normal")
    ax.set_ylim(-2.3, 2.3); ax.set_yticks([]); ax.grid(False)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(pd.Timestamp("2023-06-30"), pd.Timestamp("2036-12-31"))
    finish(fig, "fig4_policy_timeline.png", "Figure 4. The federal PQC clock that energy OT will inherit",
           note="Federal deadlines bind federal systems, not utilities or pipeline operators. Source: PQC crosswalk v1.0 timeline (author-verified 2026-09-09).")


if __name__ == "__main__":
    for f in [f1_trend, f2_categories, f3_cbom, f4_timeline]:
        f()
    print("figures written", "(FINAL)" if FINAL else "(DRAFT)")
