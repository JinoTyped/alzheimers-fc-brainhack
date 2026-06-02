"""
sgACC seed coverage / tSNR QC.

The gate flagged at the proposal: before trusting any FC value, confirm the
seed sphere actually sits on usable BOLD signal. The sgACC sits in the
ventromedial / orbitofrontal region prone to susceptibility dropout in EPI,
so a seed there can carry little real signal -> FC maps become noise.

For each subject this computes, inside the seed sphere:
  - mean tSNR  = mean_over_time / std_over_time, averaged across seed voxels
    (computed from the fMRIprep preprocessed BOLD)
  - coverage   = fraction of seed-sphere voxels inside the subject's brain mask
    (1.0 = sphere fully covered by acquired/brain data)

Run on the cluster from ~/adni/code (needs the FC env + participants.tsv):
    source ~/venv_nilearn/bin/activate
    cd ~/adni/code
    python seed_qc.py

Reads SGACC_COORDS / SEED_RADIUS from fc_utilities.py, so it QCs the SAME seed
the FC used. Change the seed there and re-run this to compare candidates.

How to read it:
  - Healthy cortical tSNR is roughly 40-100+. Ventromedial PFC/OFC often drops
    well below that. As a rough usability line, tSNR < ~20 is a concern.
  - Coverage < ~0.9 means part of the sphere falls outside the brain mask
    (seed partly off the acquired volume) -> unreliable.
  - WATCH THE PER-GROUP MEANS: if AD and CN differ systematically in seed tSNR
    or coverage, that is itself a confound that can manufacture (or erase) a
    group "difference". This matters as much as the absolute values.
TODO (team): set the tSNR / coverage thresholds you'll defend, then decide
whether to keep the current seed, move it, or flag specific subjects.
"""

import os
import numpy as np
import nibabel as nib
import pandas as pd
from nilearn.maskers import NiftiSpheresMasker

from fc_utilities import _preproc_bold, SGACC_COORDS, SEED_RADIUS

DERIV = os.path.expanduser("~/derivatives/adni/fmriprep/25.2.4")
PARTICIPANTS = "participants.tsv"

# rough advisory thresholds (not authoritative - the team sets these)
TSNR_FLAG = 20.0
COV_FLAG = 0.90


def _brain_mask(deriv_root, subj_id):
    return os.path.join(
        deriv_root, f"sub-{subj_id}", "func",
        f"sub-{subj_id}_task-rest_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii.gz")


def _tsnr_img(bold_path):
    img = nib.load(bold_path)
    data = img.get_fdata(dtype=np.float32)          # X,Y,Z,T
    mean = data.mean(axis=-1)
    std = data.std(axis=-1)
    tsnr = np.divide(mean, std, out=np.zeros_like(mean), where=std > 0)
    return nib.Nifti1Image(tsnr, img.affine)


def seed_value(img_3d):
    """Mean of a 3D image's voxels inside the seed sphere (no standardizing).

    NiftiSpheresMasker expects 4D, so add a singleton time axis; ravel the
    output so it works regardless of whether nilearn returns (1, n) or (n,).
    """
    data = np.asarray(img_3d.get_fdata(), dtype=np.float32)
    img4d = nib.Nifti1Image(data[..., np.newaxis], img_3d.affine)
    masker = NiftiSpheresMasker(
        SGACC_COORDS, radius=SEED_RADIUS,
        standardize=False, detrend=False, allow_overlap=True, verbose=0)
    return float(np.asarray(masker.fit_transform(img4d)).ravel()[0])


def main():
    df = pd.read_csv(PARTICIPANTS, sep="\t")
    rows = []
    for pid, group in zip(df["participant_id"].astype(str), df["group"]):
        bold = _preproc_bold(DERIV, pid)
        mask = _brain_mask(DERIV, pid)
        try:
            tsnr_img = _tsnr_img(bold)
            seed_tsnr = seed_value(tsnr_img)
            # coverage = mean of the 0/1 brain mask over the sphere
            cov = seed_value(nib.load(mask))
        except Exception as e:
            print(f"  !! {pid}: {e}")
            seed_tsnr, cov = float("nan"), float("nan")
        flags = []
        if seed_tsnr < TSNR_FLAG:
            flags.append("LOW_tSNR")
        if cov < COV_FLAG:
            flags.append("LOW_cov")
        rows.append({"participant_id": pid,
                     "group": "AD" if group == 1 else "CN",
                     "seed_tSNR": round(seed_tsnr, 1),
                     "coverage": round(cov, 3),
                     "flag": ",".join(flags)})

    out = pd.DataFrame(rows)
    print(f"\nSeed: {SGACC_COORDS[0]} MNI, radius {SEED_RADIUS} mm\n")
    print(out.to_string(index=False))

    print("\n--- group means ---")
    print(out.groupby("group")[["seed_tSNR", "coverage"]].mean().round(2).to_string())

    flagged = out[out["flag"] != ""]
    print(f"\n{len(flagged)} subject(s) flagged (tSNR<{TSNR_FLAG} or coverage<{COV_FLAG}):")
    if len(flagged):
        print(flagged[["participant_id", "group", "seed_tSNR", "coverage", "flag"]].to_string(index=False))
    else:
        print("  none")

    out.to_csv("seed_qc.tsv", sep="\t", index=False)
    print("\nwrote seed_qc.tsv")


if __name__ == "__main__":
    main()
