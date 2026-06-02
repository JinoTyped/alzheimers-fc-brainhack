#!/usr/bin/env python
"""Iterative 2-SD motion-outlier rejection on mean FD (Michael's "2SD, twice").

Reads participants.tsv (columns: participant_id, group [AD=1/CN=0], age,
sex [M=1/F=0], mean_fd), reports who would be dropped on each pass, says
whether 013S6768 survives, and writes a reduced manifest you can feed to
second_level() as a sensitivity check.

Run from ~/adni/code:  python motion_outlier.py
"""
import pandas as pd

P = "participants.tsv"
df = pd.read_csv(P, sep="\t")

keep = df.copy()
for it in (1, 2):
    mu = keep["mean_fd"].mean()
    sd = keep["mean_fd"].std(ddof=1)
    thr = mu + 2 * sd
    dropped = keep[keep["mean_fd"] > thr]
    print(f"Pass {it}: mean={mu:.3f}  sd={sd:.3f}  threshold(mean+2SD)={thr:.3f}")
    if len(dropped):
        for _, r in dropped.iterrows():
            grp = "AD" if r["group"] == 1 else "CN"
            print(f"   DROP {r['participant_id']}  ({grp}, mean_fd={r['mean_fd']:.3f})")
    else:
        print("   nothing above threshold")
    keep = keep[keep["mean_fd"] <= thr]

ad_k = int((keep["group"] == 1).sum()); ad_n = int((df["group"] == 1).sum())
cn_k = int((keep["group"] == 0).sum()); cn_n = int((df["group"] == 0).sum())
print(f"\nSurvivors: {len(keep)} / {len(df)}   AD {ad_k}/{ad_n}   CN {cn_k}/{cn_n}")

# Did the known high-motion subject (013S6768, FD ~0.80) survive?
norm = df["participant_id"].astype(str).str.replace("_", "", regex=False)
mask = norm.str.contains("013S6768")
if mask.any():
    row = df[mask].iloc[0]
    survived = row["participant_id"] in set(keep["participant_id"])
    print(f"013S6768: mean_fd={row['mean_fd']:.3f} -> "
          f"{'KEPT' if survived else 'DROPPED'} by 2SDx2")

keep.to_csv("participants_motion2sd.tsv", sep="\t", index=False)
print("\nwrote participants_motion2sd.tsv  (re-run second_level on this for the sensitivity model)")
