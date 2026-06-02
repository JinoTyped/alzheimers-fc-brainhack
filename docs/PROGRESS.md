# Progress Tracker

_Last updated: June 2, 2026 (Week 4 — control seed + sensitivity analyses run;
null is robust; team meeting done. Next: GitHub re-upload of corrected files +
deck for June 5.)_

## Pipeline status

| # | Step | Status | Owner |
|---|------|--------|-------|
| 1 | Select subjects (25 AD + 25 CN) | DONE | Zaki |
| 2 | Download DICOMs from ADNI | DONE | Zaki |
| 3 | DICOM -> BIDS conversion (dcm2bids) | DONE | Zaki |
| 4 | fMRIprep preprocessing on SciNet | DONE | Zaki |
| 5 | Seed-based FC analysis (Nilearn) + seed QC | DONE | Michael (code) / Zaki (run) |
| 6 | Group analysis AD vs CN + sensitivity analyses | DONE (robust null — see KEY FINDING) | Zaki |
| 7 | Figures, presentation, report | IN PROGRESS | All |

## Side tasks

- [x] Lock sgACC seed coordinate + citation — Fox et al. 2012, (6,16,-10), 5 mm
- [x] Confirm SciNet job limit (12 in the queue)
- [x] Push connectivity code to GitHub (`code/connectivity/`) — code-only, .gitignore now also excludes `*.tsv`
- [ ] **Re-upload corrected `fc_utilities.py` (5 mm) + `seed_qc.py` (CLI version) + sensitivity scripts** so GitHub matches what was run
- [ ] Michael: GitHub push access (got the invite email — "should be working"; confirm)
- [ ] Fix pitch slide: "task-based fMRI" -> "resting-state fMRI"
- [ ] Confirm grading weights + deadline dates against the syllabus (UNCONFIRMED — do not present ~20/30/30/20 or June 5/26 as fact until checked)

## What's done in detail

**Steps 1-4 (selection, download, BIDS, preprocessing).** Complete — see
`DATA_SELECTION.md` and `PIPELINE.md`. All 50 subjects through fMRIprep
(MNI152NLin6Asym res-2; `--use-syn-sdc`, `--fs-no-reconall`), verified.

**Step 5 — Seed-based FC + QC (complete).**
- Working `fc_utilities.py` (`first_level` per subject, `second_level` group),
  debugged from Michael's draft.
- Seed: Fox et al. 2012, MNI (6,16,-10), **5 mm** sphere. `SEED_RADIUS` in the
  code was reconciled to 5 (it had drifted to 6); sgACC QC re-run at 5 mm —
  numbers unchanged, confirming robustness to radius.
- Per-subject Fisher-z maps; batched one short job per subject.
- Seed coverage/tSNR QC done — see KEY FINDING.

**Step 6 — Group analysis + sensitivity (run; robust null).**
- Primary: `SecondLevelModel`, AD vs CN, covariates age (centered) + sex +
  mean FD. **FDR q<0.05: no voxels survive** (max |z| ~5.2). Uncorrected
  p<0.001: scattered, incoherent voxels.
- **Sensitivity 1 — exclude scanner site 168** (n=42; AD 18 / CN 24). Matching
  HOLDS after exclusion: sex Fisher exact p=1.000 (9M/9F vs 12M/12F), age
  73.1 vs 74.7 (t=-0.50, p=0.62). FDR still empty. (`results_no168/`)
- **Sensitivity 2 — motion outlier rejection (2-SD, twice)** (n=45; drops
  013S6768 + 168S6142 on pass 1, then 011S4827 / 003S4350 / 014S6437 on pass 2).
  FDR still empty. (`results_motion2sd/`)
- Both sensitivity models return threshold=inf / empty mask -> the null is
  stable across every reasonable subsetting.

## KEY FINDING — seed signal-quality confound (the headline)

- **AD has systematically worse signal at the sgACC seed than CN:** mean seed
  tSNR AD 30.2 / CN 42.5; coverage AD 0.91 / CN 0.98. **17/50 flagged**
  (tSNR<20 or coverage<0.9): **12 AD, 5 CN**, with **7 of the AD flags from
  scanner site 168** (site x group confound). Robust to seed radius (5≈6 mm).
- **POSITIVE CONTROL — PCC / DMN seed (0,-52,26), 5 mm:** mean tSNR AD 65.8 /
  CN 72.3, coverage 1.0 / 1.0, **0 subjects flagged.** The same AD/site-168
  scans that crater to 7-13 tSNR at the sgACC sit at 50-84 at the PCC. =>
  the deficit is **location-specific (susceptibility dropout at the sgACC),
  not a global AD data-quality problem and not subject-specific.**
- Honest nuance to keep in the talk: a small global AD<CN tSNR gap remains at
  PCC (~9%, 66 vs 72) but the sgACC gap is ~3x larger (~29%, 30 vs 43) and is
  the only place coverage drops / subjects flag.
- Implication: the AD-vs-CN sgACC FC comparison is confounded by seed-region
  signal quality / scanner site and cannot be read as a disease effect.
  **Anchor the presentation on the QC + the sgACC-vs-PCC contrast.**
  (Tables: `seed_qc.tsv`, `seed_qc_pcc.tsv`.)

## What's next (immediate)

1. **GitHub:** re-upload corrected `fc_utilities.py` (5 mm) + `seed_qc.py`
   (CLI) + `motion_outlier.py` + `exclude_site168.py` to `code/connectivity/`.
2. **Figures + deck (June 5):** lead with QC. Money figures: per-group seed
   tSNR/coverage (`seed_qc.tsv`); the sgACC-vs-PCC tSNR comparison
   (`seed_qc.tsv` vs `seed_qc_pcc.tsv`); glass-brain from `results_unc/`.
   Assign slides across Zaki / Michael / Jino; loop Lyanne in Thursday.
3. **Report — June 26.**
4. (Optional) add mean seed-tSNR as a covariate in `second_level` as a third
   sensitivity check — almost certainly also null, rounds out the set.

## Decision log (additions June 2)

- **Correction method LOCKED: FDR q<0.05.** Cluster-level and TFCE discussed
  and set aside (FDR is sufficient; team familiar with it; no blob to chase).
- **Presentation framing LOCKED: lead with the QC confound; do not fish for a
  blob.** "If there's no blob, there's no blob" (team consensus).
- **Control seed added (positive control): PCC (0,-52,26), 5 mm.** Confirms the
  sgACC signal deficit is location-specific (see KEY FINDING).
- **Seed radius reconciled to 5 mm in code** (`SEED_RADIUS` had drifted to 6);
  sgACC QC regenerated at 5 mm, numbers unchanged.
- **Sensitivity analyses run; null is robust** — exclude-site-168 (matching
  holds, p=1.0 / p=0.62) and motion 2-SD-twice both stay empty at FDR.
- **Motion handling:** primary model keeps all 50 (motion is already a
  covariate); 2-SD-twice reported as a sensitivity check. 013S6768 (mean FD
  ~0.80) kept in primary, dropped in the motion-sensitivity model.

## Open questions / to confirm

- Grading weights + deadline dates — confirm against the syllabus (~20/30/30/20
  and June 5 / June 26 still UNCONFIRMED).
- Lyanne's separate rsfMRI analysis — get an update Thursday; decide if/how it
  features in the deck.
- (Optional) seed-tSNR-as-covariate sensitivity model — run or not.
