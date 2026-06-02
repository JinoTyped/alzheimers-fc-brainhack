# Context for Continuing in a New Chat

Paste this into a new AI chat to bring it up to speed instantly. Then attach
whichever other knowledge base files are relevant (PROGRESS.md, PIPELINE.md,
DATA_SELECTION.md, PROJECT_PLAN.md, README.md).

---

I'm the project lead on a group project for BrainHack School 2026 (a
neuroimaging summer school in Toronto). Here's the full context.

**The project:** a seed-based resting-state functional connectivity (FC)
analysis of the subgenual anterior cingulate cortex (sgACC), comparing
Alzheimer's disease (AD) patients vs cognitively normal (CN) controls.

**Data:** ADNI, phase ADNI3. Resting-state fMRI + T1 MPRAGE, raw DICOM. Final
sample is 25 AD + 25 CN, sex-balanced (13 M / 12 F per group) and age-matched
(AD mean 74.1, CN 74.6). Single-band rs-fMRI only. Multi-vendor / multi-site
(Siemens + Philips, possibly GE).

**Pipeline (all built and run):** DICOM → BIDS (`dcm2bids`) → fMRIprep on the
SciNet Teach cluster → Nilearn seed-to-voxel FC → AD-vs-CN second-level model
with age/sex/motion covariates.

**Team:** effective working team is me (Zaki — data/pipeline/QC), Michael (FC
analysis code + seed coordinate; GitHub `chichael-meng`), and Jino (repo, deck,
figures). Lyanne contributes separate rsfMRI work, limited availability. Two
other members aren't contributing.

**WHERE I AM NOW (June 2, 2026 — Week 4; final presentation ~June 5):**
The whole pipeline is DONE end-to-end. Specifically:

- **Preprocessing complete** — all 50 subjects through fMRIprep
  (MNI152NLin6Asym, 2 mm; `--use-syn-sdc`, `--fs-no-reconall`). Verified.
- **FC code debugged + run** — Michael's first draft was fixed into a working
  `fc_utilities.py` (`first_level` per subject, `second_level` for the group).
  Key fixes: `standardize="zscore_sample"` on both maskers (so dot/n is a
  Pearson r, not covariance, before Fisher-z); confounds via `load_confounds`
  (motion + wm_csf); per-subject TR from the BOLD JSON sidecar.
- **Seed LOCKED:** Fox et al. 2012 sgACC, MNI (6, 16, −10), **5 mm** sphere
  (doi:10.1016/j.biopsych.2012.04.028).
- **First-level FC run on all 50** — Fisher-z seed-to-voxel maps
  (`..._desc-sgaccFCz.nii.gz`), batched as one short job per subject
  (`fc_one.sh` + `submit_fc.sh`, throttled to the 12-job queue cap). A single
  serial job timed out (~8 min/subject × 50 > walltime), hence the per-subject
  parallel approach.
- **Group analysis run** — Nilearn `SecondLevelModel`, AD vs CN, covariates
  age (mean-centered) + sex + mean FD. **No voxels survive FDR q<0.05**
  (max |z| ~5.2). Uncorrected p<0.001 shows only scattered noise.
- **Seed coverage / tSNR QC done** (`seed_qc.py`) — and it's the key result.

**THE KEY FINDING (this anchors the presentation):** the sgACC seed does not
carry equal-quality signal in the two groups. AD mean seed tSNR ~30 (coverage
0.91) vs CN ~43 (coverage 0.98); 17/50 subjects flagged for low tSNR/coverage
(12 AD, 5 CN), largely driven by scanner **site 168** (~7 AD subjects, ~1 CN).
Robust to seed radius (5 mm ≈ 6 mm). So site and group are partly confounded,
the seed sits in a susceptibility-dropout region, and the AD-vs-CN FC
comparison can't be interpreted as a disease effect. The QC is the honest,
defensible story.

**Cluster setup (SciNet Teach, userid `lcl_uotmsc1127s1935`):**
- BIDS: `~/adni/bids`; fMRIprep derivatives:
  `~/derivatives/adni/fmriprep/25.2.4/`.
- Analysis code: `~/adni/code/` (`fc_utilities.py`, `build_participants.py`,
  `seed_qc.py`, `fc_one.sh`, `submit_fc.sh`); fMRIprep scripts in
  `~/adni/code/fmriprep/`.
- Python env: `~/venv_nilearn` (nilearn, nibabel, pandas, matplotlib).
  Reactivate each session: `module load python; source ~/venv_nilearn/bin/activate`.
- Outputs: `results/` (FDR, empty by design), `results_unc/` (uncorrected map +
  glass-brain PNG), `participants.tsv`, `seed_qc.tsv`.

**Open decisions (team, at the June 2 meeting):**
1. Correction method — FDR q<0.05 (current) vs cluster-level (more sensitive).
2. How to frame the QC confound for June 5 (lead with it as the finding).
3. Any sensitivity analysis — add mean seed-tSNR as a covariate, or exclude
   flagged/site-168 subjects (caveat: drops AD to ~13, underpowered).
4. High-motion subject 013S6768 (mean FD ~0.80) — threshold or keep.
5. Confirm grading weights + June 5/26 dates against the syllabus (unconfirmed).
6. Michael's GitHub push access (his code still on Drive).

**GitHub:** repo `alzheimers-fc-brainhack` (user `afwh12`), uploads via the web
UI. Code-only (ADNI data never committed). Today's code goes under
`code/connectivity/`. `requirements.txt` should add nilearn, nibabel, pandas,
matplotlib.

**What I need help with:** [DESCRIBE YOUR CURRENT QUESTION HERE]

---

## How to keep this knowledge base current

After any significant work session, update:
- `PROGRESS.md` — move steps between NOT STARTED / DONE, add to the decision log
- `PROJECT_PLAN.md` — if roles, timeline, or scope change
- `DATA_SELECTION.md` — if the sample changes
- `PIPELINE.md` — fill in specifics (commands, paths, coordinates) once run
Update the "Last updated" date in `PROGRESS.md` each time.
