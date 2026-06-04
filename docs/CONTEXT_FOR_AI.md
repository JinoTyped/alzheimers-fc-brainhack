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

**WHERE I AM NOW (June 4, 2026 — Week 4, Thursday; presenting Fri June 5,
3:00–3:20 pm):** The whole pipeline is DONE end-to-end, plus a PCC positive
control and sensitivity analyses; figures are done and the deck is finalized
(minus a cut Lyanne slide). Specifically:

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
- **PCC positive control done** — same QC at a low-dropout posterior-cingulate
  seed (MNI 0, −52, 26, 5 mm): AD ~66 / CN ~72 tSNR, full coverage, zero
  flagged. Proves the AD deficit is sgACC-specific, not global. This is the
  deck's money slide.
- **Sensitivity analyses done** — exclude site 168 (n=42, groups stay matched
  sex p=1.0 / age p=0.62) still null; iterative 2-SD high-motion removal still
  null. The null is robust (also settles the high-motion subject 013S6768).

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

**Decisions (mostly resolved as of June 4):**
1. Correction method → **FDR q<0.05 primary** (uncorrected p<0.001 only for a
   visible exploratory map; cluster-level not pursued).
2. QC confound framing → **lead with it**; PCC control is the clincher.
3. Sensitivity → **done** (exclude site 168 still null; high-motion removal
   still null).
4. High-motion subject 013S6768 → **removed in sensitivity, null unchanged.**
5. Lyanne's slide → **cut** (not presenting Friday); presenters Michael/Zaki/Jino.

**Still open:**
- Grading weights — confirm against the syllabus (~20/30/30/20; slot date/time
  June 5 3:00–3:20 and report June 26 are confirmed, weights are not).
- GitHub push of `code/connectivity/` + docs + requirements; Michael's push
  access (his code still on Drive).
- Slide 3 resting-state fix in the built deck (was "task-based").

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
