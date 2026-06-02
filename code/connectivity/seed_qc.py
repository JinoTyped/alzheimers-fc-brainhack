"""
Seed coverage / tSNR QC  (parametrized: works for any seed, not just sgACC).
"""
import os
import argparse
import numpy as np
import nibabel as nib
import pandas as pd
from nilearn.maskers import NiftiSpheresMasker
from fc_utilities import _preproc_bold, SGACC_COORDS, SEED_RADIUS

DERIV = os.path.expanduser("~/derivatives/adni/fmriprep/25.2.4")
PARTICIPANTS = "participants.tsv"
TSNR_FLAG = 20.0
COV_FLAG = 0.90


def _brain_mask(deriv_root, subj_id):
    return os.path.join(
        deriv_root, f"sub-{subj_id}", "func",
        f"sub-{subj_id}_task-rest_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii.gz")


def _tsnr_img(bold_path):
    img = nib.load(bold_path)
    data = img.get_fdata(dtype=np.float32)
    mean = data.mean(axis=-1)
    std = data.std(axis=-1)
    tsnr = np.divide(mean, std, out=np.zeros_like(mean), where=std > 0)
    return nib.Nifti1Image(tsnr, img.affine)


def seed_value(img_3d, coords, radius):
    data = np.asarray(img_3d.get_fdata(), dtype=np.float32)
    img4d = nib.Nifti1Image(data[..., np.newaxis], img_3d.affine)
    masker = NiftiSpheresMasker(
        coords, radius=radius,
        standardize=False, detrend=False, allow_overlap=True, verbose=0)
    return float(np.asarray(masker.fit_transform(img4d)).ravel()[0])


def main(coords, radius, out_path, seed_label):
    df = pd.read_csv(PARTICIPANTS, sep="\t")
    rows = []
    for pid, group in zip(df["participant_id"].astype(str), df["group"]):
        bold = _preproc_bold(DERIV, pid)
        mask = _brain_mask(DERIV, pid)
        try:
            seed_tsnr = seed_value(_tsnr_img(bold), coords, radius)
            cov = seed_value(nib.load(mask), coords, radius)
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
    print(f"\nSeed [{seed_label}]: {tuple(coords[0])} MNI, radius {radius} mm\n")
    print(out.to_string(index=False))
    print("\n--- group means ---")
    print(out.groupby("group")[["seed_tSNR", "coverage"]].mean().round(2).to_string())
    flagged = out[out["flag"] != ""]
    print(f"\n{len(flagged)} subject(s) flagged (tSNR<{TSNR_FLAG} or coverage<{COV_FLAG}):")
    if len(flagged):
        print(flagged[["participant_id", "group", "seed_tSNR", "coverage", "flag"]].to_string(index=False))
    else:
        print("  none")
    out.to_csv(out_path, sep="\t", index=False)
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--coords", default=None, help="seed MNI as 'x,y,z'")
    ap.add_argument("--radius", type=float, default=None)
    ap.add_argument("--suffix", default="")
    ap.add_argument("--label", default=None)
    args = ap.parse_args()
    coords = [tuple(float(v) for v in args.coords.split(","))] if args.coords else SGACC_COORDS
    radius = args.radius if args.radius is not None else SEED_RADIUS
    out_path = f"seed_qc_{args.suffix}.tsv" if args.suffix else "seed_qc.tsv"
    label = args.label or (args.suffix if args.suffix else "sgACC")
    main(coords, radius, out_path, label)
