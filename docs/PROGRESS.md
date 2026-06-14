# Progress Tracker

_Last updated: June 14, 2026 — Gallery submission complete: index.md report written from the KB + 3 figures, PR #430 opened to the BHS website (awaiting maintainer merge). IMS peer-assessment form submitted. All figures pulled off the cluster locally ahead of the June 21 account cutoff. Report deadline CONFIRMED June 26._

## Pipeline status

| # | Step | Status | Owner |
|---|------|--------|-------|
| 1 | Select subjects (25 AD + 25 CN) | DONE | Zaki |
| 2 | Download DICOMs from ADNI | DONE | Zaki |
| 3 | DICOM -> BIDS conversion (dcm2bids) | DONE | Zaki |
| 4 | fMRIprep preprocessing on SciNet | DONE | Zaki |
| 5 | Seed-based FC (Nilearn) + seed QC + PCC control | DONE | Michael (code) / Zaki (run, QC) |
| 6 | Group analysis AD vs CN + sensitivity | DONE (result confounded — see KEY FINDING) | Zaki |
| 7 | Figures, presentation, report/gallery | DONE — presented June 5; gallery PR #430 submitted (awaiting merge) | Zaki, Michael, Jino |

## Side tasks

- [x] Lock sgACC seed coordinate + citation — Fox et al. 2012, (6,16,-10), 5 mm
- [x] Confirm SciNet job limit (12 in the queue)
- [x] PCC positive-control seed QC — confirms the sgACC deficit is region-specific
- [x] Sensitivity analyses — exclude site / exclude high-motion (both still null)
- [x] Money figures done (flagged-subjects bar; sgACC-vs-PCC tSNR; glass-brain)
- [x] Slide 2 anatomy image — reuse the sgACC (area 25) figure from the proposal deck
- [x] Cut slide 8 (Lyanne's analysis) — Lyanne not presenting Friday; presenters Michael/Zaki/Jino
- [x] Slide 3 resting-state fix (was "task-based") — done before the June 5 talk
- [ ] Push final connectivity code to the project repo (`code/connectivity/`) + updated docs + requirements (separate from the gallery PR)
- [ ] Michael: get GitHub push access working (code currently on Drive)
- [x] Report deadline confirmed: June 26, via GitHub PR (Erin Dickie announcement, June 8). Course is credit/no-credit for Zaki (IMS), so weights are moot.
- [x] Gallery submission — content/en/project/sgacc-fc-alzheimers/index.md + 3 figures, PR #430 opened to school-brainhack.github.io (awaiting review/merge).
- [x] IMS peer-assessment form submitted (self + Jino + Michael — only the 3 IMS-credit students were assessed).
- [ ] Optional: anonymous course feedback survey (Erin's request).

## What's done in detail

**Steps 1-3 (selection, download, BIDS).** Complete — see `DATA_SELECTION.md`
and `PIPELINE.md`.

**Step 4 — fMRIprep preprocessing (complete).**
- All 50 subjects through fMRIprep on the SciNet Teach cluster
  (MNI152NLin6Asym res-2; `--use-syn-sdc`, `--fs-no-reconall`). Verified every
  subject has its final preproc BOLD + confounds TSV.
- Outputs: `~/derivatives/adni/fmriprep/25.2.4/`.

**Step 5 — Seed-based FC + QC (complete).**
- Michael's draft FC code debugged into a working `fc_utilities.py`
  (`first_level` per subject, `second_level` group). Proven on sub-003S6264,
  run across all 50.
- Seed: Fox et al. 2012, MNI (6,16,-10), 5 mm sphere.
- Per-subject Fisher-z seed-to-voxel maps (`..._desc-sgaccFCz.nii.gz`).
- Batched one short job per subject (`fc_one.sh` + `submit_fc.sh`, skip-if-
  exists, <=12 in queue) after a single serial job hit the walltime.
- Seed coverage/tSNR QC done (`seed_qc.py`) — see KEY FINDING.
- **PCC positive control (added June 4).** Re-ran the identical seed QC at a
  low-dropout DMN node (posterior cingulate) as a control. Both groups look
  healthy and overlapping (AD ~66 / CN ~72 tSNR, full coverage, **zero
  flagged**); the same AD scans that crater near tSNR ~10 at the sgACC sit at
  50–80 at the PCC. Confirms the AD signal deficit is **sgACC-specific**
  (a dropout-localized effect), not globally bad data.
  PCC seed: MNI (0, -52, 26), 5 mm (`seed_qc.py --coords 0,-52,26 --radius 5
  --suffix pcc --label PCC`); figure via `qc_figures.py`.

**Step 6 — Group analysis (run; not interpretable as a disease effect).**
- `SecondLevelModel`, AD vs CN, covariates age (centered) + sex + mean FD.
- **FDR q<0.05: no voxels survive** (max |z| ~5.2). Uncorrected p<0.001:
  scattered, spatially incoherent voxels — consistent with no robust effect.
- **Sensitivity analyses (added June 4) — the null is robust:**
  - Exclude site 168 entirely (n=42): groups stay matched (sex p=1.0, age
    p=0.62), still no voxels survive FDR.
  - Iterative 2-SD high-motion removal on mean FD (applied twice): still null.
    Resolves the 013S6768 "threshold or keep" question — removed, result
    unchanged.

**Step 7 — Figures, presentation, gallery submission (complete).**
- Presented Fri June 5, 3:00–3:20 pm (Michael / Zaki / Jino). Talk delivered the
  QC-confound headline with the PCC control as the clincher; Q&A covered field-map
  distortion correction (future work to recover sgACC signal) and the TMS
  "background connectivity" interpolation trick.
- Gallery page = the sole graded report deliverable (no separate document).
  `content/en/project/sgacc-fc-alzheimers/index.md` written from the knowledge
  base; 3 figures embedded (tsnr_sgacc_vs_pcc.png, flagged_sgacc.png,
  glassbrain_uncorrected.png). Submitted as **PR #430** to
  `school-brainhack.github.io`; awaiting maintainer review/merge.
- All figures pulled off the cluster to `~/bhs_figs` ahead of the June 21 account
  cutoff — project is now cluster-independent.

## KEY FINDING — seed signal-quality confound

- **AD has systematically worse signal at the sgACC seed than CN:** mean seed
  tSNR AD ~30 / CN ~43; coverage AD 0.91 / CN 0.98.
- **17/50 flagged** (tSNR<20 or coverage<0.9): **12 AD, 5 CN.**
- **Driven largely by site 168** (~7 AD, ~1 CN), uniformly poor sgACC tSNR ->
  scanner site and group partly the same variable (site x group confound).
- **Robust to seed radius** (5 mm ~= 6 mm) -> real seed-location/site effect,
  not a parameter artifact.
- Implication: the AD-vs-CN sgACC FC comparison is confounded by seed-region
  signal quality (susceptibility dropout, worse in AD/site-168) and can't be
  read as a disease effect. **The QC is the strongest result — it anchored the
  presentation and the gallery report.** (Table: `seed_qc.tsv`.)
- **Corroborated two ways (June 4):** (1) a PCC positive control shows both
  groups have healthy, overlapping signal there (zero flagged) — so the deficit
  is sgACC-specific, not bad data everywhere; (2) the null survives excluding
  site 168 (still matched) and removing high-motion subjects — so we're not
  hiding a real effect. The story is a clean, defensible confounded null.

## What's next (immediate)

1. **PR #430 awaiting review/merge** — a BHS maintainer (Ju-Chi) has to approve
   and merge it; link posted in the Discord thread. Out of our hands until then.
2. **Optional:** anonymous course feedback survey (Erin's request).
3. **Optional:** push final connectivity code + updated docs to the project repo
   (`JinoTyped/alzheimers-fc-brainhack`) if not already synced.

With the gallery PR submitted and the IMS peer-assessment form in, the graded
work is effectively complete pending the merge.

## Decision log (additions June 1-2)

- **sgACC seed LOCKED: Fox et al. 2012, MNI (6,16,-10), 5 mm sphere.**
  doi:10.1016/j.biopsych.2012.04.028. Canonical subgenual ROI; 5 mm matches the
  paper.
- **FC code design (debugged from Michael's draft):** both maskers
  `standardize="zscore_sample"` (dot/n = Pearson r before Fisher-z); confounds
  via `load_confounds` (motion + wm_csf, handles NaN first frame); TR per
  subject from BOLD JSON sidecar; second-level explicit design (intercept,
  group [AD=1/CN=0], centered age, sex, mean FD), FC maps loaded in
  participants.tsv order; matplotlib Agg backend (headless).
- **FC batching = one job per subject + throttled submitter.** Serial job over
  50 exceeded walltime (~8 min/subj); switched to `fc_one.sh` per subject via
  `submit_fc.sh` (skip-if-exists, <=12 in queue), ~40 min for all 50.
- **Group result is a confounded null** — no voxels survive FDR q<0.05; not a
  disease effect (see KEY FINDING).

### Additions June 4
- **PCC positive control added** — AD ~66 / CN ~72 tSNR, full coverage, zero
  flagged. The AD signal deficit is sgACC-specific, not global. This is the
  clinching evidence; it became the deck's money slide (sgACC vs PCC tSNR).
- **Sensitivity analyses added** — exclude site 168 (n=42, groups stay matched
  sex p=1.0 / age p=0.62) → still null; iterative 2-SD high-motion removal
  (×2) → still null. The null is robust.
- **Correction method settled: FDR q<0.05 is primary** (the null); uncorrected
  p<0.001 shown only as an exploratory visible map. Cluster-level not pursued.
- **Confound handling settled** — lead with the QC; PCC control + sensitivity
  are the support. No seed-tSNR-covariate or site-covariate model needed for
  the talk (site is partly collinear with group; QC + control + sensitivity
  make the point more cleanly).
- **Slide 8 (Lyanne's separate rsfMRI analysis) cut** — Lyanne is not presenting
  Friday. Presenters: Michael, Zaki, Jino. Talk drops ~8 → ~7 min (still inside
  5–10). Lyanne stays on the title slide / thanks as a team member.
- **Slide 2 anatomy** — reuse the proposal deck's sgACC (area 25) figure.
- **Presentation slot CONFIRMED:** Fri June 5, 3:00–3:20 pm; talk 5–10 min
  (target ~7); 20-min slot leaves room for Q&A.

### Additions June 14
- Deadline CONFIRMED: June 26, submitted via GitHub PR (Erin Dickie, June 8). The
  gallery page IS the sole graded report deliverable — no separate document
  (TA-confirmed earlier).
- Cluster sunset: SciNet Teach account active only to June 21; data centre fully
  down June 22-26 (through the deadline). All three figures pulled to ~/bhs_figs
  before the cutoff → project is now cluster-independent.
- Gallery page built from README/PROGRESS/DATA_SELECTION content; folder
  sgacc-fc-alzheimers; figures tsnr_sgacc_vs_pcc.png, flagged_sgacc.png,
  glassbrain_uncorrected.png (renamed from AD_vs_CN_sgACC_FC.png). PR #430.
- Published author list: all 6 team members (Zaki, Michael, Jino, Lyanne, Rehan,
  Gabby). IMS peer-assessment (separate IMS-module requirement) covered only the
  3 IMS-credit students.

## Open questions / to confirm

- **Nothing outstanding.** Report deadline (June 26) confirmed; course is
  credit/no-credit for Zaki (IMS) so grading weights are moot. The only remaining
  dependency is the maintainer merge of PR #430.

### Resolved June 14
- Report deadline → June 26 confirmed (Erin Dickie announcement).
- Sole deliverable → the gallery PR (no separate report document).
- Grading weights → moot (credit/no-credit for Zaki via IMS).

### Resolved this session (June 4) — moved out of open questions
- Correction method → FDR q<0.05 primary (see decision log).
- How to handle the confound → QC headline + PCC control + sensitivity.
- High-motion subject 013S6768 → removed in sensitivity, null unchanged.
- Scanner-vendor / site confound → quantified (site 168) and tied to the QC
  finding; PCC control + site-exclusion sensitivity address it directly.
