#!/usr/bin/env python
"""Sensitivity: exclude scanner site 168, then check whether the sex/age
matching still holds on the reduced sample, and write a manifest to re-run
second_level() on.

Site is the leading numeric block of the ADNI ID (168S6921 -> 168).
Uses Fisher's exact for the sex x group test: at ~18 AD the expected cell
counts are too small for chi-square to be valid.

Run from ~/adni/code:  python exclude_site168.py
"""
import pandas as pd
from scipy.stats import fisher_exact, ttest_ind

EXCLUDE = ["168"]  # switch/add sites here if needed

df = pd.read_csv("participants.tsv", sep="\t")
sid = df["participant_id"].astype(str).str.replace("_", "", regex=False)
df["site"] = sid.str.extract(r"^(\d+)")[0]
red = df[~df["site"].isin(EXCLUDE)].copy()

def counts(d):
    return int((d.group == 1).sum()), int((d.group == 0).sum())

adF, cnF = counts(df); adR, cnR = counts(red)
print(f"Full:    AD {adF}  CN {cnF}  (n={len(df)})")
print(f"No-168:  AD {adR}  CN {cnR}  (n={len(red)})  -- dropped {len(df) - len(red)}")

# sex x group 2x2 (sex: M=1/F=0)  -> Fisher's exact
a = int(((red.group == 1) & (red.sex == 1)).sum())  # AD, M
b = int(((red.group == 1) & (red.sex == 0)).sum())  # AD, F
c = int(((red.group == 0) & (red.sex == 1)).sum())  # CN, M
d = int(((red.group == 0) & (red.sex == 0)).sum())  # CN, F
print(f"\nReduced sex x group:  AD {a}M/{b}F   CN {c}M/{d}F")
_, p_sex = fisher_exact([[a, b], [c, d]])
print(f"Fisher exact (sex ~ group): p = {p_sex:.3f}")

# age balance after exclusion
ad_age = red.loc[red.group == 1, "age"]; cn_age = red.loc[red.group == 0, "age"]
t, p_age = ttest_ind(ad_age, cn_age)
print(f"Age:  AD {ad_age.mean():.1f}  CN {cn_age.mean():.1f}  t={t:.2f}  p={p_age:.3f}")

red.drop(columns=["site"]).to_csv("participants_no168.tsv", sep="\t", index=False)
print("\nwrote participants_no168.tsv  -> re-run second_level on this file")
