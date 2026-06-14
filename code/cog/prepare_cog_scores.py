#!/usr/bin/env python
"""
Extract MMSE scores from the ADNI MMSE.csv file for the 25 AD subjects
in this study, and write cog_scores.tsv.

Usage (run from code/cog/):
    python prepare_cog_scores.py
    python prepare_cog_scores.py --mmse MMSE.csv --out cog_scores.tsv

Output: cog_scores.tsv  (columns: participant_id, MMSE)

For each subject the script uses the baseline visit (VISCODE 'bl', 'm00',
or 'sc'). If none of those exist it falls back to the earliest VISDATE.
"""
import argparse
import os
import sys
import pandas as pd

AD_SUBJECTS = [
    "003S6264", "011S4827", "011S6303", "013S6768", "019S6585",
    "019S6712", "032S6600", "035S6660", "035S6927", "036S6179",
    "100S6713", "114S6039", "114S6368", "114S6595", "123S6825",
    "130S6072", "168S6142", "168S6735", "168S6754", "168S6827",
    "168S6828", "168S6843", "168S6921", "305S6810", "305S6881",
]

BASELINE_VISCODES = {"bl", "m00", "sc"}
HERE = os.path.dirname(os.path.abspath(__file__))


def bids_to_adni(bids_id):
    """003S6264 -> 003_S_6264"""
    idx = bids_id.index("S")
    return f"{bids_id[:idx]}_S_{bids_id[idx+1:]}"


def pick_baseline_row(sub_df):
    vis = sub_df["VISCODE"].str.strip().str.lower()
    bl = sub_df[vis.isin(BASELINE_VISCODES)]
    if not bl.empty:
        return bl.iloc[0]
    if "VISDATE" in sub_df.columns:
        return sub_df.sort_values("VISDATE").iloc[0]
    return sub_df.iloc[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mmse", default=os.path.join(HERE, "MMSE.csv"),
                    help="Path to ADNI MMSE.csv (default: MMSE.csv alongside this script)")
    ap.add_argument("--out",  default=os.path.join(HERE, "cog_scores.tsv"))
    args = ap.parse_args()

    if not os.path.exists(args.mmse):
        sys.exit(f"ERROR: {args.mmse} not found.")

    df = pd.read_csv(args.mmse, low_memory=False)
    df.columns = df.columns.str.strip()

    for col in ("PTID", "VISCODE", "MMSCORE"):
        if col not in df.columns:
            sys.exit(f"ERROR: expected column '{col}' not found.\n"
                     f"  Columns present: {list(df.columns)}")

    rows = []
    not_found = []

    for bids_id in AD_SUBJECTS:
        adni_id = bids_to_adni(bids_id)
        sub_df = df[df["PTID"].str.strip() == adni_id]
        if sub_df.empty:
            print(f"  NOT FOUND: {bids_id} ({adni_id})")
            not_found.append(bids_id)
            rows.append({"participant_id": bids_id, "MMSE": float("nan")})
            continue
        r = pick_baseline_row(sub_df)
        mmse = float(r["MMSCORE"]) if pd.notna(r["MMSCORE"]) else float("nan")
        rows.append({"participant_id": bids_id, "MMSE": mmse})

    out = pd.DataFrame(rows, columns=["participant_id", "MMSE"])
    out.to_csv(args.out, sep="\t", index=False)

    n_valid = out["MMSE"].notna().sum()
    print(f"Wrote {args.out}  ({n_valid}/25 subjects have MMSE scores)")
    if not_found:
        print(f"  Not found in MMSE.csv: {not_found}")
    if n_valid < 10:
        print("WARNING: fewer than 10 subjects have MMSE — model will be underpowered.")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
