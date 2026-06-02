# Pipeline — Technical Steps

Step-by-step record of the work. Steps 1-6 are DONE; step 7 (figures/deck/
report) is in progress. Cluster paths are on the SciNet Teach cluster
(`teach.scinet.utoronto.ca`, userid `lcl_uotmsc1127s1935`).

Environment to reactivate each session:
```
module load python
source ~/venv_nilearn/bin/activate      # nilearn, nibabel, pandas, matplotlib
cd ~/adni/code
```

---

## Step 2 — Download DICOMs from ADNI  [DONE]

Both IDA collections (AD, CN) downloaded as DICOM zips, scp'd to `~/adni/` and
unzipped under `~/adni/{ad,cn}_dicom/`. Metadata CSVs under `~/adni/*_metadata`
are the authoritative subject manifest. Multi-vendor data (Siemens + Philips,
possibly GE). No `$SCRATCH` on Teach — all work in `$HOME`.

## Step 3 — DICOM to BIDS  [DONE]

`dcm2bids` 3.2.0 (venv `~/venv_dcm2bids`). Config `~/adni/dcm2bids_config.json`
maps MPRAGE->T1w, rsfMRI/fcMRI->`task-rest_bold`. One subject (`114_S_6039`)
had blank series descriptions and used a fallback config matching
`MRAcquisitionType`. Output BIDS: `~/adni/bids` (labels like `sub-003S6264`).
A minimal `dataset_description.json` was added at the BIDS root (fMRIprep
requires it).

## Step 4 — fMRIprep preprocessing on SciNet  [DONE]

- Container `~/links/common/fmriprep-25.2.4.simg` (apptainer), FS license
  `~/links/common/fs_license.txt`.
- Offline TemplateFlow pre-staged on the login node into
  `~/templates/.cache/templateflow` (compute nodes have no internet):
  MNI152NLin2009cAsym, MNI152NLin6Asym, OASIS30ANTs.
- Run scripts in `~/adni/code/fmriprep/` (`run1_anat.sh`, `run2_fmri.sh`,
  `submit_all.sh`). Two deliberate changes from the school examples:
  `--fs-no-reconall` (volumetric analysis, no surfaces) and dropped
  `--cifti-output`. `--use-syn-sdc` for fieldmap-less distortion correction.
- Job limits: 12 jobs in the QUEUE total (running + pending), 40 cores each,
  4 h walltime. Batched with a throttled submitter that keeps <=12 queued.
- A full anat+func run is ~42 min/subject. **All 50 verified complete.**
- Outputs: `~/derivatives/adni/fmriprep/25.2.4/sub-<L>/func/`
  - `sub-<L>_task-rest_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz`
  - `sub-<L>_task-rest_desc-confounds_timeseries.tsv`
- Verify loop (read-only): for each `sub-` in `~/adni/bids`, confirm the
  preproc BOLD exists; resubmit any MISSING (fMRIprep resumes).

## Step 5 — Seed-based FC (Nilearn) + seed QC  [DONE]

All analysis code in `~/adni/code/`. Main module: **`fc_utilities.py`**.

### Seed
- sgACC, MNI **(6, 16, -10)**, **5 mm** sphere.
- Citation: Fox et al. 2012, Biol Psychiatry 72(7):595-603,
  doi:10.1016/j.biopsych.2012.04.028.
- Set in `fc_utilities.py` as `SGACC_COORDS` / `SEED_RADIUS`.

### first_level(deriv_root, subj_id, bids_root=None)
Per subject:
1. Read TR per subject from the BOLD JSON sidecar (multi-vendor sample).
2. Confounds via `load_confounds(strategy=("motion","wm_csf"))` — principled
   subset, handles the NaN first frame.
3. Seed time series: `NiftiSpheresMasker` at the seed, radius 5 mm.
4. Whole-brain time series: `NiftiMasker`, `smoothing_fwhm=6`.
   - BOTH maskers use `standardize="zscore_sample"`, `detrend=True`,
     `standardize_confounds=True`, bandpass `low_pass=0.1`, `high_pass=0.01`.
   - The z-scoring is REQUIRED so that `np.dot(brain.T, seed)/n` is a Pearson r
     (not a covariance) before Fisher-z.
5. Pearson r per voxel -> `np.arctanh` (Fisher-z) -> inverse_transform.
6. Write `sub-<L>_task-rest_space-MNI152NLin6Asym_res-2_desc-sgaccFCz.nii.gz`
   next to the subject's BOLD.

### Batching (one job per subject)
A single serial job over 50 subjects exceeded the walltime (~8 min/subject), so
FC is batched one short job per subject:
- `~/adni/code/fc_one.sh` — sbatch script, takes the BIDS label as `$1`,
  skips if the output already exists, runs `first_level`.
- `~/adni/code/submit_fc.sh` — throttled submitter (run under `nohup`); submits
  `fc_one.sh` per subject, retries until the queue has room (<=12), skip-if-
  exists. ~40 min for all 50.
- Monitor: `squeue -u $USER`;
  `ls ~/derivatives/adni/fmriprep/25.2.4/sub-*/func/*sgaccFCz* | wc -l` (-> 50).
- NOTE: re-running after a parameter change requires deleting old maps first
  (skip-if-exists will otherwise skip everything):
  `find ~/derivatives/adni/fmriprep/25.2.4 -name '*sgaccFCz*' -delete`
  (plain `rm` is interactive on this cluster — use `find -delete`).

### Seed coverage / tSNR QC  ** the key analysis **
`~/adni/code/seed_qc.py` — per subject, inside the seed sphere, computes:
- mean tSNR (mean/std over time from the preproc BOLD)
- coverage (fraction of seed voxels inside the brain mask)
Reads the seed from `fc_utilities.py`, so it QCs the same seed the FC used.
Run: `python seed_qc.py` -> prints a table + per-group means, writes
`seed_qc.tsv`. Advisory flags: tSNR<20 or coverage<0.9.

**Result (the project's headline finding):**
- AD mean seed tSNR ~30, coverage 0.91; CN ~43, coverage 0.98.
- 17/50 flagged (12 AD, 5 CN), driven largely by scanner site 168 (~7 AD,
  ~1 CN). Robust to seed radius (5 mm ~= 6 mm).
- => seed signal quality is confounded with group/site; the FC comparison
  can't be read as a disease effect. See PROGRESS.md KEY FINDING.

## Step 6 — Group analysis (AD vs CN)  [DONE]

### participants.tsv
Built by `~/adni/code/build_participants.py` (demographics hardcoded from
DATA_SELECTION.md; `mean_fd` computed from each confounds file via the
`mean_fd()` helper). Columns: `participant_id` (label, no `sub-`),
`group` (AD=1/CN=0), `age`, `sex` (M=1/F=0), `mean_fd`.

### second_level(participants_path, deriv_root, ...)
- `SecondLevelModel`; explicit design = intercept + group (AD=1/CN=0) +
  mean-centered age + sex + mean FD. FC maps loaded in participants.tsv order.
- `compute_contrast("group")` -> z-map; `threshold_stats_img` with
  `multiple_comparison` ('fdr'|'bonferroni'|'fpr') at `alpha`.
- Writes a thresholded `.nii.gz` + a glass-brain `.png`.
- Run (FDR, current default):
  `python -c "from fc_utilities import second_level; second_level('participants.tsv','$HOME/derivatives/adni/fmriprep/25.2.4', out_dir='results')"`
- Exploratory uncorrected (for a visible map):
  `... multiple_comparison='fpr', alpha=0.001, out_dir='results_unc'`

**Result:** no voxels survive FDR q<0.05 (max |z| ~5.2). Uncorrected p<0.001
shows scattered, spatially incoherent voxels. Interpreted as a confounded null
(see Step 5 QC), not a disease effect.

**[DECIDE — team]** correction method (FDR vs cluster-level); whether to run a
sensitivity analysis (mean seed-tSNR as covariate; exclude flagged/site-168 ->
underpowered; site as covariate -> partly collinear with group).

## Step 7 — Figures, presentation, report  [IN PROGRESS]

- Figures: seed location; group glass-brain (`results_unc/AD_vs_CN_sgACC_FC.png`);
  **per-group seed tSNR/coverage from `seed_qc.tsv` (the money figure)**.
- Presentation ~June 5 — lead with the QC confound finding.
- Report ~June 26 — include the methods detail from DATA_SELECTION.md and the
  QC/confound. (Dates unconfirmed — verify against the syllabus.)

---

## GitHub repo structure

Repo `alzheimers-fc-brainhack` (user `afwh12`), uploads via the web UI,
code-only (ADNI data never committed; `.gitignore` excludes data/, results/,
imaging files).

```
alzheimers-fc-brainhack/
  code/
    dcm2bids_config.json, dcm2bids_config_114S6039.json, run_dcm2bids_all.sh
    preprocessing/        # fMRIprep: run1_anat.sh, run2_fmri.sh, submit_all.sh
    connectivity/         # NEW: fc_utilities.py, build_participants.py,
                          #      seed_qc.py, fc_one.sh, submit_fc.sh
  docs/                   # this knowledge base
  README.md, requirements.txt, .gitignore
```

`requirements.txt` should include the FC deps: nilearn, nibabel, pandas,
matplotlib (plus the preprocessing tools already listed).
