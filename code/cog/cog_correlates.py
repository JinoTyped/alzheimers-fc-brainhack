#!/usr/bin/env python
"""
Within-AD cognitive correlate analysis: sgACC FC ~ MMSE.

Does sgACC seed-to-voxel FC correlate with MMSE within the Alzheimer's
disease group (n=25)?

Model (SecondLevelModel, AD subjects only):
    FC ~ MMSE + age + sex + mean_fd

Sign convention: MMSE higher = better cognition, so a positive beta at a
voxel means stronger sgACC FC is associated with better cognitive performance.

Both FDR q<0.05 and uncorrected p<0.001 maps are saved. Given n=25, FDR may
be empty; the uncorrected map is included for exploratory visualisation.

Inputs (must exist in ~/adni/code):
    participants.tsv  -- built by build_participants.py (all 50 subjects)
    cog_scores.tsv    -- built by prepare_cog_scores.py
                         columns: participant_id, MMSE

Outputs: results_cog/
    ad_cog_manifest.tsv        subjects + MMSE scores used in the model
    MMSE_sgACC_FC_fdr.nii.gz   FDR q<0.05 thresholded z-map
    MMSE_sgACC_FC_fdr.png
    MMSE_sgACC_FC_unc.nii.gz   uncorrected p<0.001 z-map
    MMSE_sgACC_FC_unc.png

Run from ~/adni/code:
    python cog_correlates.py
"""
import argparse
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
from nilearn.glm.second_level import SecondLevelModel
from nilearn.glm import threshold_stats_img
from nilearn.plotting import plot_glass_brain

# fc_utilities lives in the sibling connectivity/ folder
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "connectivity"))
from fc_utilities import _fc_output

DERIV = os.path.expanduser("~/derivatives/adni/fmriprep/25.2.4")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--participants",
                    default=os.path.join(HERE, "..", "connectivity", "participants.tsv"))
    ap.add_argument("--cog-scores",
                    default=os.path.join(HERE, "cog_scores.tsv"))
    ap.add_argument("--out-dir",
                    default=os.path.join(HERE, "results_cog"))
    args = ap.parse_args()

    for path in (args.participants, args.cog_scores):
        if not os.path.exists(path):
            sys.exit(f"ERROR: {path} not found.\n"
                     f"  Run build_participants.py first (participants.tsv), or\n"
                     f"  prepare_cog_scores.py --adnimerge <path> (cog_scores.tsv).")

    # ---- merge ----------------------------------------------------------------
    df_part = pd.read_csv(args.participants, sep="\t")
    df_cog  = pd.read_csv(args.cog_scores,  sep="\t")
    df_cog["participant_id"] = df_cog["participant_id"].astype(str)

    df_ad = df_part[df_part["group"] == 1].copy()
    df_ad["participant_id"] = df_ad["participant_id"].astype(str)
    df = df_ad.merge(df_cog[["participant_id", "MMSE"]],
                     on="participant_id", how="inner").reset_index(drop=True)

    missing = set(df_ad["participant_id"]) - set(df["participant_id"])
    if missing:
        print(f"No cog_scores entry for: {sorted(missing)}")

    df = df[df["MMSE"].notna()].reset_index(drop=True)
    n = len(df)
    print(f"AD subjects with MMSE: {n}")
    if n < 8:
        sys.exit("ERROR: fewer than 8 AD subjects with MMSE. Check cog_scores.tsv.")

    # ---- manifest -------------------------------------------------------------
    os.makedirs(args.out_dir, exist_ok=True)
    df.to_csv(os.path.join(args.out_dir, "ad_cog_manifest.tsv"), sep="\t", index=False)

    # ---- model ----------------------------------------------------------------
    mmse = df["MMSE"].astype(float).values
    age  = df["age"].astype(float).values
    fc_maps = [_fc_output(DERIV, pid) for pid in df["participant_id"]]

    design = pd.DataFrame({
        "intercept": np.ones(n),
        "MMSE":      mmse - mmse.mean(),
        "age":       age  - age.mean(),
        "sex":       df["sex"].astype(float).values,
        "mean_fd":   df["mean_fd"].astype(float).values,
    })

    print(f"MMSE: mean={mmse.mean():.1f}  SD={mmse.std():.1f}  "
          f"range=[{mmse.min():.0f}, {mmse.max():.0f}]")
    print("Fitting SecondLevelModel ...")

    model = SecondLevelModel(n_jobs=2, verbose=1).fit(
        fc_maps, design_matrix=design)
    stat_img = model.compute_contrast("MMSE", output_type="z_score")

    # ---- threshold + save -----------------------------------------------------
    for tag, alpha, height_control in [
        ("fdr", 0.05,  "fdr"),
        ("unc", 0.001, "fpr"),
    ]:
        thr_img, threshold = threshold_stats_img(
            stat_img, alpha=alpha, height_control=height_control,
            two_sided=True)
        q_or_p = "q" if tag == "fdr" else "p"
        stem   = os.path.join(args.out_dir, f"MMSE_sgACC_FC_{tag}")
        title  = f"sgACC FC ~ MMSE  |  AD only (n={n})  |  {tag} {q_or_p}<{alpha}"

        thr_img.to_filename(stem + ".nii.gz")
        display = plot_glass_brain(
            thr_img, threshold=threshold, plot_abs=False,
            colorbar=True, title=title)
        display.savefig(stem + ".png", dpi=150)
        display.close()
        print(f"[{tag}] threshold={threshold:.3f}  -> {os.path.basename(stem)}.nii.gz")

    print(f"\nDone. Results in {args.out_dir}/")


if __name__ == "__main__":
    main()
