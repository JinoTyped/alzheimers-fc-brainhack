# Progress Tracker

_Last updated: June 1, 2026 (Week 4, Day 1 — full FC pipeline run end-to-end; seed QC done)_

## Pipeline status

| # | Step | Status | Owner |
|---|------|--------|-------|
| 1 | Select subjects (25 AD + 25 CN) | DONE | Zaki |
| 2 | Download DICOMs from ADNI | DONE | Zaki |
| 3 | DICOM -> BIDS conversion (dcm2bids) | DONE | Zaki |
| 4 | fMRIprep preprocessing on SciNet | DONE | Zaki |
| 5 | Seed-based FC analysis (Nilearn) + seed QC | DONE | Michael (code) / Zaki (run) |
| 6 | Group analysis AD vs CN | DONE (result confounded — see below) | Zaki |
| 7 | Figures, presentation, report | NOT STARTED | All |

## Side tasks

- [x] Lock sgACC seed coordinate + citation — DONE (Fox et al. 2012; see decision log)
- [x] Confirm SciNet job limit (12 in the queue)
- [x] Test SciNet teach cluster login
- [ ] Set up GitHub repo + structure + `.gitignore` — repo exists; push today's code (`code/connectivity/`) + updated docs
- [ ] Fix pitch slide: "task-based fMRI" -> "resting-state fMRI"
- [ ] Confirm grading weights + deadline dates against the syllabus (still unconfirmed)

## What's done in detail

**Steps 1-3 (selection, download, BIDS).** Unchanged — see earlier entries and
`DATA_SELECTION.md` / `PIPELINE.md`.

**Step 4 — fMRIprep preprocessing (complete).**
- All 50 subjects preprocessed on the SciNet Teach cluster; every subject has its
  final `space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz` + confounds TSV.
  Verified with the read-only "MISSING" loop (printed nothing).
- Outputs in `~/derivatives/adni/fmriprep/25.2.4/`.

**Step 5 — Seed-based FC + QC (complete).**
- Michael's first-draft FC code was debugged into a working `fc_utilities.py`
  (`first_level` per subject, `second_level` for the group model). Proven
  end-to-end on sub-003S6264, then run across all 50.
- Seed: Fox et al. 2012 sgACC, MNI (6, 16, -10), **5 mm** sphere (matches the
  paper's ROI).
- Per-subject seed-to-voxel Pearson r -> Fisher-z maps written next to each
  subject's BOLD as `..._desc-sgaccFCz.nii.gz`.
- Batched as one short job per subject (`fc_one.sh` + `submit_fc.sh`, throttled to
  the 12-job queue cap, skip-if-exists), ~40 min for all 50.
- **Seed coverage / tSNR QC done** (`seed_qc.py`) — the gate flagged at the
  proposal. See the finding below.

**Step 6 — Group analysis (run; result not interpretable as a disease effect).**
- `SecondLevelModel`, AD vs CN, covariates age (mean-centered) + sex + mean FD.
- **At FDR q < 0.05, no voxels survive** (max |z| ~5.2). An exploratory
  uncorrected map (voxel p < 0.001) shows only scattered, spatially incoherent
  voxels — consistent with no robust group difference.
- This null is expected given the QC confound below; the comparison as run cannot
  be interpreted as an AD-vs-CN connectivity difference.

## KEY FINDING — seed signal-quality confound (June 1)

The sgACC seed coverage/tSNR QC turned up a real, presentable result:

- **AD has systematically worse signal at the sgACC seed than CN.** Group means:
  AD seed tSNR ~30, coverage 0.91; CN seed tSNR ~43, coverage 0.98.
- **17 of 50 subjects flagged** (tSNR < 20 or coverage < 0.9): **12 AD, 5 CN.**
- **Driven largely by site 168**, which contributes ~7 subjects to AD and ~1 to
  CN and has uniformly poor sgACC tSNR. So scanner site and group are partially
  the same variable here — a site x group confound.
- **Robust to seed radius:** the 5 mm and 6 mm runs give nearly identical QC
  numbers, so this is a genuine seed-location / site problem, not a parameter
  artifact.

Implication: a naive AD-vs-CN sgACC FC comparison in this sample is confounded by
seed-region signal quality (susceptibility dropout, worse in AD/site-168). The QC
itself is the strongest result and should anchor the presentation. (QC table saved
as `seed_qc.tsv`.)

## What's next (immediate)

1. **June 1 meeting (12:30):** decide (a) correction method — FDR vs cluster-level
   (cluster-level is more sensitive); (b) how to frame the QC/confound for June 5;
   (c) whether to run sensitivity analyses.
2. **Push to GitHub:** today's code under `code/connectivity/` (`fc_utilities.py`,
   `build_participants.py`, `seed_qc.py`, `fc_one.sh`, `submit_fc.sh`); update
   `requirements.txt` (nilearn, nibabel, pandas, matplotlib); push these docs.
3. **Figures + deck** for June 5 — lead with the QC finding.
4. Confirm grading weights + deadline dates against the syllabus.

## Decision log (additions June 1)

- **sgACC seed LOCKED: Fox et al. 2012, MNI (6, 16, -10), 5 mm sphere.**
  Fox MD, Buckner RL, White MP, Greicius MD, Pascual-Leone A. "Efficacy of
  transcranial magnetic stimulation targets for depression is related to
  intrinsic functional connectivity with the subgenual cingulate." Biol
  Psychiatry 2012;72(7):595-603. doi:10.1016/j.biopsych.2012.04.028. (Canonical
  sgACC coordinate from a depression-TMS context, reused here as a standard sgACC
  location. Radius set to 5 mm to match the paper's ROI.)
- **FC code design (debugged from Michael's draft).** Both maskers use
  `standardize="zscore_sample"` so `dot(brain.T, seed)/n` is a Pearson r (not a
  covariance) before Fisher-z. Confounds via `load_confounds` (motion + wm_csf),
  which also handles the NaN first frame. TR read per-subject from the BOLD JSON
  sidecar (sample is multi-vendor). Second-level uses an explicit design matrix
  (intercept, group [AD=1/CN=0], mean-centered age, sex, mean FD) with FC maps
  loaded in the same order as `participants.tsv`. matplotlib forced to the Agg
  backend (headless cluster).
- **FC batching = one job per subject + throttled submitter.** A single serial
  job over 50 subjects exceeded the 4h walltime (~8 min/subject). Switched to one
  `fc_one.sh` job per subject via `submit_fc.sh` (skip-if-exists, <=12 in queue),
  mirroring the fMRIprep batching pattern. ~40 min for all 50.
- **Group result is a confounded null.** No voxels survive FDR q<0.05 for AD vs
  CN. Not interpreted as a disease effect because of the seed signal-quality
  confound (see KEY FINDING).

## Open questions / to confirm

- **Correction method** — FDR q<0.05 (current) vs cluster-level thresholding.
  Team decision; cluster-level may be more sensitive given small n + sgACC
  dropout.
- **How to handle the confound** — options to discuss: present the QC as the
  headline finding; add mean seed-tSNR as a group-analysis covariate; exclude
  flagged / site-168 subjects (note: drops ~12 AD -> badly underpowered);
  add scanner/site as a covariate (partly collinear with group).
- **High-motion subject 013S6768** (AD, mean FD ~0.80) — decide whether to apply a
  motion threshold or leave it (it's in the model as a covariate).
- **Scanner-vendor confound** — now has concrete evidence via site 168; tie this
  to the QC finding in the methods/limitations.
- Exact grading weights and deadline dates — confirm against the syllabus
  (~20/30/30/20 and June 5 / June 26 still unconfirmed).
