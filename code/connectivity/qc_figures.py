"""
QC figures for the June 5 deck.
Reads seed_qc.tsv (sgACC) and seed_qc_pcc.tsv (PCC) and writes:
  figures/tsnr_sgacc_vs_pcc.png   <- the headline: deficit is sgACC-specific
  figures/flagged_sgacc.png       <- flagged subjects by group at the sgACC

Run from ~/adni/code:  python qc_figures.py
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "figures"
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(0)

sg = pd.read_csv("seed_qc.tsv", sep="\t")
pcc = pd.read_csv("seed_qc_pcc.tsv", sep="\t")
groups = ["AD", "CN"]

# --- Figure 1: tSNR by group, sgACC vs PCC, with individual points ----------
fig, ax = plt.subplots(figsize=(7, 5))
x = np.arange(len(groups))
w = 0.36
for i, (name, d, color) in enumerate([("sgACC", sg, "#c0392b"), ("PCC", pcc, "#2c7fb8")]):
    means = [d.loc[d.group == g, "seed_tSNR"].mean() for g in groups]
    sems = [d.loc[d.group == g, "seed_tSNR"].sem() for g in groups]
    pos = x + (i - 0.5) * w
    ax.bar(pos, means, w, yerr=sems, capsize=4, label=name, color=color, alpha=0.85)
    for j, g in enumerate(groups):
        vals = d.loc[d.group == g, "seed_tSNR"].values
        jit = (rng.random(len(vals)) - 0.5) * w * 0.7
        ax.scatter(np.full(len(vals), pos[j]) + jit, vals, s=14, color="k", alpha=0.35, zorder=3)

ax.axhline(20, ls="--", lw=1, color="grey")
ax.text(len(groups) - 0.5, 21, "tSNR = 20 (flag)", fontsize=8, color="grey")
ax.set_xticks(x)
ax.set_xticklabels(groups)
ax.set_ylabel("Seed tSNR (mean \u00b1 SEM, points = subjects)")
ax.set_title("Seed signal quality: the AD deficit is sgACC-specific")
ax.legend(title="Seed")
fig.tight_layout()
fig.savefig(f"{OUT}/tsnr_sgacc_vs_pcc.png", dpi=200)
print("wrote figures/tsnr_sgacc_vs_pcc.png")

# --- Figure 2: flagged subjects by group at the sgACC -----------------------
fig2, ax2 = plt.subplots(figsize=(5, 4))
flagged = (sg["flag"].fillna("") != "").groupby(sg["group"]).sum()
vals = [int(flagged.get(g, 0)) for g in groups]
ax2.bar(groups, vals, color=["#c0392b", "#2c7fb8"], alpha=0.85)
for i, v in enumerate(vals):
    ax2.text(i, v + 0.1, str(v), ha="center")
ax2.set_ylabel("# subjects flagged (tSNR<20 or coverage<0.9)")
ax2.set_title("sgACC seed: flagged subjects by group")
fig2.tight_layout()
fig2.savefig(f"{OUT}/flagged_sgacc.png", dpi=200)
print("wrote figures/flagged_sgacc.png")
