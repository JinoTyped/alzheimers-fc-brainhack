"""
sgACC seed-based functional connectivity utilities
BrainHack School 2026 - AD vs CN (ADNI3, fMRIprep derivatives, Nilearn)

Cleaned-up / debugged version of Michael's first draft.

Entry points
------------
first_level(deriv_root, subj_id, bids_root=None)
    Per-subject sgACC seed-to-voxel FC, Fisher-z transformed, written to disk.
second_level(participants_path, deriv_root)
    AD-vs-CN group contrast on the first-level maps -> thresholded stat map
    + glass-brain PNG.
mean_fd(deriv_root, subj_id)
    Helper to compute the per-subject motion covariate for participants.tsv.

Search this file for "TODO" for the decisions the group still needs to lock
(seed coordinate/radius, confound strategy, multiple-comparison method).

Notes on what changed from the draft (so the diff is transparent for the repo):
  * added standardize="zscore_sample" to both maskers  -> required so that
    np.dot(brain.T, seed)/n is a Pearson r, not a covariance (this matches the
    official Nilearn seed-based-connectivity example). Without it, arctanh()
    receives values outside [-1, 1] and returns inf/NaN.
  * replaced confounds=[full_tsv_path] with load_confounds(): selects a
    principled subset of fMRIprep's confounds and handles the NaN first row.
  * TR is read per-subject from the BOLD JSON sidecar (sample is multi-vendor).
  * second_level: reads the real participants.tsv (TSV sep), builds an explicit
    design matrix, loads FC maps in the SAME order as the participants table,
    fixed the undefined-variable and unclosed-paren bugs, saves a PNG.
"""

import json
import os

import matplotlib
matplotlib.use("Agg")  # headless (SciNet) - render figures to file, no display

import numpy as np
import pandas as pd
from nilearn.maskers import NiftiSpheresMasker, NiftiMasker
from nilearn.interfaces.fmriprep import load_confounds
from nilearn.glm.second_level import SecondLevelModel
from nilearn.glm import threshold_stats_img
from nilearn.plotting import plot_glass_brain


# --- sgACC seed -------------------------------------------------------------
# TODO (team): confirm coordinate, radius, and citation. (6, 16, -10) in MNI is
# a commonly used sgACC seed; Michael used radius=5, PIPELINE.md notes 6 mm is
# typical. Lock this with the paper you cite.
SGACC_COORDS = [(6, 16, -10)]   # MNI152 - VERIFY against citation
SEED_RADIUS = 5                 # mm

# Resting-state bandpass
LOW_PASS = 0.1
HIGH_PASS = 0.01
SMOOTHING_FWHM = 6              # mm, applied to the whole-brain map


def _preproc_bold(deriv_root, subj_id):
    """Path to a subject's fMRIprep preprocessed BOLD."""
    return os.path.join(
        deriv_root, f"sub-{subj_id}", "func",
        f"sub-{subj_id}_task-rest_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz",
    )


def _confounds_tsv(deriv_root, subj_id):
    """Path to a subject's fMRIprep confounds TSV."""
    return os.path.join(
        deriv_root, f"sub-{subj_id}", "func",
        f"sub-{subj_id}_task-rest_desc-confounds_timeseries.tsv",
    )


def _fc_output(deriv_root, subj_id):
    """Path for the first-level Fisher-z FC map."""
    return _preproc_bold(deriv_root, subj_id).replace(
        "_desc-preproc_bold.nii.gz", "_desc-sgaccFCz.nii.gz")


def _get_tr(deriv_root, subj_id, bids_root=None):
    """Read RepetitionTime (seconds) from the BOLD JSON sidecar.

    Tries the fMRIprep derivative sidecar first, then the raw BIDS sidecar.
    Reading per-subject matters because the sample is multi-vendor.
    """
    candidates = [_preproc_bold(deriv_root, subj_id).replace(".nii.gz", ".json")]
    if bids_root:
        candidates.append(os.path.join(
            bids_root, f"sub-{subj_id}", "func",
            f"sub-{subj_id}_task-rest_bold.json"))
    for path in candidates:
        if os.path.exists(path):
            with open(path) as f:
                meta = json.load(f)
            if "RepetitionTime" in meta:
                return float(meta["RepetitionTime"])
    raise FileNotFoundError(
        f"RepetitionTime not found for sub-{subj_id}. "
        f"Check the BOLD .json sidecar (raw BIDS or derivatives).")


def first_level(deriv_root, subj_id, bids_root=None, save=True):
    """sgACC seed-to-voxel FC for one subject. Returns the Fisher-z niimg."""
    func_path = _preproc_bold(deriv_root, subj_id)
    t_r = _get_tr(deriv_root, subj_id, bids_root)

    # Principled confound subset (also strips the NaN first row for us).
    # TODO (team): confirm strategy. motion + wm_csf is a sane default; add
    # "global_signal" only if the group agrees. NOTE: "high_pass" is left OUT of
    # the strategy on purpose because we band-pass in the masker below - keeping
    # both would high-pass twice.
    confounds, sample_mask = load_confounds(
        func_path,
        strategy=("motion", "wm_csf"),
        motion="basic",
        wm_csf="basic",
    )

    common = dict(
        detrend=True,
        standardize="zscore_sample",   # <-- makes dot/n a Pearson r
        standardize_confounds=True,
        low_pass=LOW_PASS,
        high_pass=HIGH_PASS,
        t_r=t_r,
        memory="nilearn_cache",
        memory_level=1,
        verbose=0,
    )

    seed_masker = NiftiSpheresMasker(SGACC_COORDS, radius=SEED_RADIUS, **common)
    seed_ts = seed_masker.fit_transform(
        func_path, confounds=confounds, sample_mask=sample_mask)

    brain_masker = NiftiMasker(smoothing_fwhm=SMOOTHING_FWHM, **common)
    brain_ts = brain_masker.fit_transform(
        func_path, confounds=confounds, sample_mask=sample_mask)

    # Pearson r per voxel (both series z-scored above), then Fisher-z.
    seed_to_voxel = np.dot(brain_ts.T, seed_ts) / seed_ts.shape[0]
    seed_to_voxel = np.clip(seed_to_voxel, -0.999999, 0.999999)  # guard arctanh
    seed_to_voxel_z = np.arctanh(seed_to_voxel)
    fc_img = brain_masker.inverse_transform(seed_to_voxel_z.T)

    if save:
        out = _fc_output(deriv_root, subj_id)
        fc_img.to_filename(out)
        print(f"sub-{subj_id}: wrote {out}")
    return fc_img


def mean_fd(deriv_root, subj_id):
    """Mean framewise displacement for one subject (the NaN first frame is
    skipped by .mean()). Use this to fill the mean_fd column of participants.tsv."""
    fd = pd.read_csv(_confounds_tsv(deriv_root, subj_id), sep="\t")
    return fd["framewise_displacement"].mean()


def second_level(participants_path, deriv_root,
                 contrast="group", output_stat="z_score",
                 multiple_comparison="fdr", alpha=0.05, out_dir="."):
    """AD-vs-CN group contrast on the first-level Fisher-z maps.

    participants_path : TSV with columns
        participant_id : BIDS label WITHOUT the 'sub-' prefix, e.g. 003S6264
        group          : AD=1, CN=0   (so the 'group' beta = AD - CN)
        age            : numeric (mean-centered internally)
        sex            : numeric, e.g. M=1, F=0
        mean_fd        : per-subject mean framewise displacement (see mean_fd())
    Row order of this table defines subject order; FC maps load in that order.

    multiple_comparison : 'fdr', 'bonferroni', or 'fpr'  (assumes a z-map)
    alpha               : q (fdr/bonferroni) or p (fpr)
    """
    df = pd.read_csv(participants_path, sep="\t")

    # FC maps in the SAME order as the participants table.
    fc_maps = [_fc_output(deriv_root, str(pid)) for pid in df["participant_id"]]

    # Explicit design: intercept + group regressor + nuisance covariates.
    age = df["age"].astype(float).values
    design = pd.DataFrame({
        "intercept": np.ones(len(df)),
        "group": df["group"].astype(float).values,        # AD=1, CN=0
        "age": age - age.mean(),                           # mean-centered
        "sex": df["sex"].astype(float).values,
        "mean_fd": df["mean_fd"].astype(float).values,
    })

    model = SecondLevelModel(n_jobs=2, verbose=1).fit(fc_maps, design_matrix=design)
    stat_img = model.compute_contrast(contrast, output_type=output_stat)

    # TODO (team): pick the correction. 'fdr' q=0.05 is Michael's placeholder;
    # cluster-level thresholding may be more sensitive given the small sample
    # and sgACC signal dropout.
    thr_img, threshold = threshold_stats_img(
        stat_img, alpha=alpha, height_control=multiple_comparison, two_sided=True)

    os.makedirs(out_dir, exist_ok=True)
    display = plot_glass_brain(
        thr_img, threshold=threshold, plot_abs=False, colorbar=True,
        title=f"AD vs CN  sgACC FC  ({multiple_comparison} {alpha})")
    display.savefig(os.path.join(out_dir, "AD_vs_CN_sgACC_FC.png"))
    display.close()

    out = os.path.join(out_dir, "AD_vs_CN_sgACC_FC.nii.gz")
    thr_img.to_filename(out)
    print(f"wrote {out}  (threshold={threshold:.3f})")
    return thr_img, threshold


if __name__ == "__main__":
    # Smoke test on the one subject that's already proven through fMRIprep.
    DERIV = os.path.expanduser("~/derivatives/adni/fmriprep/25.2.4")
    BIDS = os.path.expanduser("~/adni/bids")
    first_level(DERIV, "003S6264", bids_root=BIDS)
