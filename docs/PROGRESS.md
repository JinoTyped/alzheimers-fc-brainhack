# Progress Tracker

_Last updated: May 28, 2026 (Week 3, Day 3 — SciNet, fMRIprep COMPLETE, all 50/50)_

## Pipeline status

| # | Step | Status | Owner |
|---|------|--------|-------|
| 1 | Select subjects (25 AD + 25 CN) | DONE | Zaki |
| 2 | Download DICOMs from ADNI | DONE | Zaki |
| 3 | DICOM -> BIDS conversion (dcm2bids) | DONE | Zaki |
| 4 | fMRIprep preprocessing on SciNet | DONE (50/50) | Zaki |
| 5 | Seed-based FC analysis (Nilearn) | NOT STARTED | Michael |
| 6 | Group analysis AD vs CN | NOT STARTED | Michael |
| 7 | Figures, presentation, report | NOT STARTED | All |

## Side tasks (not on critical path, do anytime)

- [ ] Set up GitHub repo + folder structure + `.gitignore` (no MRI data committed) — Jino, at the May 26 evening meeting
- [ ] Lock sgACC seed coordinate + citation (no data needed — Michael)
- [ ] Fix pitch slide: "task-based fMRI" -> "resting-state fMRI"
- [x] Test SciNet teach cluster login (done May 26)
- [x] Confirm SciNet job limit (done — 12 jobs in the QUEUE, not 12 running; see decision log)
- [ ] @Ju-Chi on Discord that preprocessing is COMPLETE, 50/50 (Erin/Ju-Chi asked) — ready to send (May 28)

## What's done in detail

**Subject selection (complete).**
- Final sample: 25 AD + 25 CN, all from ADNI3.
- Each subject has exactly one T1 (MPRAGE) and one single-band
  resting-state fMRI scan, both from the same scan date.
- Groups are sex-balanced (13 M / 12 F each) and age-matched
  (AD mean 74.1, CN mean 74.6).
- Both ADNI image collections validated clean — see `DATA_SELECTION.md`.

**Week 3 Day 1 — SciNet access, data on cluster, BIDS conversion (May 26).**
- SciNet Teach cluster account active (userid `lcl_uotmsc1127s1935`);
  login confirmed via `ssh lcl_uotmsc1127s1935@teach.scinet.utoronto.ca`.
- fMRIprep container and FreeSurfer license confirmed at `~/links/common`
  (`fmriprep-25.2.4.simg`, `fs_license.txt`); XCP-D container also present
  (`xcp_d-0.7.3.simg`) — useful for the step-5 coverage check.
- ADNI data: 4 zips downloaded from the IDA, transferred to the cluster
  with `scp` into `~/adni/`, and unzipped under `~/adni/{ad,cn}_dicom/`.
- dcm2bids 3.2.0 + dcm2niix installed in a venv (`~/venv_dcm2bids`).
- DICOM -> BIDS conversion COMPLETE: all 50 subjects converted, each with a
  `T1w` and a `task-rest_bold`, in `~/adni/bids`. One subject
  (`114_S_6039`) had blank series descriptions and needed a fallback
  config — see decision log. Details in `PIPELINE.md` step 3.
- TA confirmed the SciNet job concurrency limit: 12 jobs running at once,
  40 cores each (see decision log + `PIPELINE.md` step 4).

**Week 3 Day 3 — fMRIprep running on SciNet (May 28).**
- fMRIprep preprocessing started. The big blocker — no internet on the Teach
  compute nodes — is solved: TemplateFlow templates were pre-staged on the
  login node (which does have internet) into `~/templates/.cache/templateflow`,
  the path the school's example scripts bind in as the container `$HOME`, so
  the offline compute job reads them from disk. Staged MNI152NLin2009cAsym,
  MNI152NLin6Asym, OASIS30ANTs (via a `templateflow` pip venv +
  `templateflow.api.get`). Details in `PIPELINE.md` step 4.
- Adapted the school's two example scripts to our dataset. Anat script lives
  at `~/adni/code/fmriprep/run1_anat.sh`. Two deliberate changes from the
  examples: added `--fs-no-reconall` and dropped `--cifti-output 91k` (see
  decision log). `--participant_label` takes the BIDS label minus the `sub-`
  prefix (`003S6264`).
- Hit and fixed: `~/adni/bids` was missing the top-level
  `dataset_description.json` (dcm2bids didn't scaffold it); fMRIprep's pybids
  indexer hard-requires it even with `--skip-bids-validation`. Added a minimal
  one.
- Anat-only test on sub-003S6264 (job 4409) RUNNING. Workflow graph built
  (149 nodes), offline templates picked up, FreeSurfer surface stages skipped
  as intended. Awaiting `fMRIPrep finished successfully`.
- Full pipeline PROVEN end-to-end on sub-003S6264: anat stage finished in
  ~21 min (job 4409), functional stage in ~22 min (job 4410), both far under
  the 4-hour cap. Offline templates picked up, FreeSurfer surface stages
  skipped, `--use-syn-sdc` ran. Outputs confirmed in
  `~/derivatives/adni/fmriprep/25.2.4/sub-003S6264/{anat,func}/`, including the
  preprocessed BOLD (`..._space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz`)
  and the confounds TSV (`..._desc-confounds_timeseries.tsv`).
- Key batching realization: because `--fs-no-reconall` makes the WHOLE run
  ~42 min (well under 4h), there's no need for the two-stage split —
  `run2_fmri.sh` (no `--anat-only`) runs the full anat+func pipeline in ONE
  job per subject. Also the SciNet "12-job" limit is 12 jobs TOTAL in the
  queue (running + pending), NOT 12 running at once (corrected — see decision
  log; a dependency-chained batch overflowed it instantly).
- Remaining 49 subjects launched via a throttled background submitter,
  `~/adni/code/fmriprep/submit_all.sh` (run under `nohup`, logging to
  `submit_all.log`): it submits `run2_fmri.sh` per subject and retries until
  the queue has room, so it never exceeds 12. `run2_fmri.sh` ends with a line
  that deletes that subject's work dir on success, keeping disk to ~1 GB
  derivatives/subject (per-subject footprint ~3 GB: 2.1 work + 1 derivatives).
- Michael + Jino nudged (May 28) to start their parallel tracks.

**Week 3 Day 3 (evening) — fMRIprep COMPLETE: all 50/50 (May 28).**
- The throttled batch finished; verified with the missing-BOLD check (for every
  `sub-` in `~/adni/bids`, the final
  `..._space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz` exists). Check
  prints nothing → all 50 present. Step 4 DONE, well inside the Week 3 target.
- **9 subjects failed `--use-syn-sdc` and were re-run without distortion
  correction.** These 9 — 019S6585, 019S6712, 100S6713, 114S6039, 123S6825,
  130S6072, 177S6448, 305S6810, 305S6881 — errored with
  `Fieldmap-less (SyN) estimation was requested, but PhaseEncodingDirection
  information appears to be absent`. Their BOLD JSON sidecars lack
  `PhaseEncodingDirection`, so SyN-SDC can't run. Fix: for these 9, `run2_fmri.sh`
  was switched from `--use-syn-sdc` to `--ignore fieldmaps slicetiming`, then
  resubmitted — all completed. See decision log + Open questions. NOTE: these are
  exactly the subjects to scrutinize first in the sgACC coverage QC (step 5 #2),
  since the seed region is dropout-prone and these 9 have NO distortion
  correction.
- Final pipeline split: 41 subjects ran with `--use-syn-sdc`; 9 ran with
  `--ignore fieldmaps`. Worth a methods/limitations line.

## What's next (immediate)

1. **Step 4 is DONE** — all 50 preprocessed. (Optional final tidiness: failure scan
   `sacct -X --starttime today --format=JobID,JobName%18,State,ExitCode | grep fmriprep_fmri | grep -v COMPLETED`.)
2. **sgACC seed-region coverage / tSNR QC** (the gate flagged at the proposal;
   `PIPELINE.md` step 5 #2) — confirm the seed carries usable BOLD across all 50
   before trusting FC. Needs the seed coordinate from Michael. **Check the 9
   no-distortion-correction subjects first** (listed above) — most at risk.
3. **Michael — now unblocked:** lock the sgACC seed coordinate + citation, then
   write the Nilearn seed-to-voxel FC code; it runs directly on
   `~/derivatives/adni/fmriprep/25.2.4/`.
4. **Jino:** GitHub repo + folder structure + `.gitignore` (no MRI data) and the
   presentation deck scaffold.
5. @Ju-Chi on Discord that preprocessing is complete (Erin/Ju-Chi asked).
6. Tally the scanner-vendor split per group for the group-analysis covariate
   decision (open question below).

## Decision log

- **Phase = ADNI3, not ADNI4.** ADNI3 has the most consistent single-band
  resting-state fMRI protocol. ADNI4 was discussed at the pitch stage but
  not adopted. Note: whether ADNI distributes preprocessed scans is moot —
  we pull Original raw DICOM and run our own fMRIprep regardless.
- **Groups are AD vs CN only.** No MCI or SCD subjects — the comparison is
  pure Alzheimer's disease vs cognitively normal. An earlier idea (raised
  at the proposal meeting) of lumping MCI in with AD was dropped; the locked
  sample in `DATA_SELECTION.md` contains neither MCI nor SCD.
- **Single-band rs-fMRI only.** ADNI has single-band and multiband (MB)
  resting-state protocols with different TRs/volume counts. Mixing them is
  an acquisition confound, so multiband scans were excluded.
- **Excluded scan types:** multiband (MB) rs-fMRI, MoCoSeries (a derivative),
  ASL/perfusion (relCBF, Perfusion_Weighted, pCASL, PASL), DTI, localizers,
  and `_ND` T1 variants (non-distortion-corrected — plain MPRAGE used instead).
- **Sample size 25/group.** Adequate for a 2-week summer-school project.
  Could scale up later if preprocessing goes smoothly, but 25/group is the
  committed baseline.
- **Sex + age matching.** ADNI's AD pool skews male and the CN pool skews
  female; subjects were matched so sex/age don't confound the group
  comparison.
- **Several subjects dropped for missing T1s.** fMRIprep requires a T1
  anatomical. Many initially-picked subjects had no MPRAGE in ADNI and were
  replaced with complete subjects. Final sample is fully verified.
- **Covariates for group analysis:** age, sex, head motion (motion comes
  out of fMRIprep confounds).
- **No fieldmaps in the dataset.** (May 26.) Confirmed at BIDS conversion:
  every one of the 50 subjects has exactly one T1 + one functional series,
  nothing else. The two "phase"-named series (`MPRAGE Phase A-P`,
  `rsfMRI (Eyes Open) -phase P to A`) are each a single subject's only scan
  of that type — not separate fieldmap acquisitions. fMRIprep will do
  distortion correction with `--use-syn-sdc` (fieldmap-less SyN), which the
  school's example `run1fMRI` script already uses.
- **Data is multi-vendor (Siemens + Philips, possibly GE).** (May 26.)
  Discovered at conversion — some subjects are Philips (SENSE in series
  names, per-slice DICOMs rather than Siemens mosaics). Normal for ADNI's
  multi-site design, and conversion handles it (the single-band protocol is
  consistent: 197 volumes across vendors). Scanner/vendor is a known
  nuisance variable for FC — DECISION PENDING for the group analysis (see
  Open questions).
- **BIDS subject labels.** (May 26.) ADNI IDs like `003_S_6264` can't be
  used directly as BIDS `sub-` labels (underscores aren't allowed). Scheme:
  strip the underscores — `003_S_6264` -> `sub-003S6264`.
- **SciNet job limit = 12 jobs in the QUEUE, not 12 running.** (May 26 TA
  note; CORRECTED May 28.) The Teach cap is 12 jobs *submitted* at once
  (running + pending combined), 40 cores each, 4-hour walltime. Found May 28
  when a batch of anat+func dependency pairs overflowed it immediately
  (`SBATCH ERROR: Too many jobs in the queue (limit=12)`). Implication: do NOT
  pre-queue dependency chains — batch with a throttled submitter that keeps
  <=12 jobs in the queue at a time (see the batching decision below).
- **`114_S_6039` blank series descriptions.** (May 26.) This subject's
  DICOMs had empty `ProtocolName`/`SeriesDescription` fields, so the main
  dcm2bids config (which matches on `SeriesDescription`) could not classify
  its scans. Fixed with a one-subject fallback config
  (`~/adni/dcm2bids_config_114S6039.json`) matching `MRAcquisitionType`
  (`3D` -> T1w, `2D` -> task-rest bold). Worth a line in the methods
  section; keep that config in the repo alongside the main one.
- **`--fs-no-reconall` (skip FreeSurfer surfaces).** (May 28.) Our analysis
  is volumetric seed-to-voxel FC in MNI space; we never use cortical
  surfaces. Full FreeSurfer recon-all (~6-10h/subject) would blow past the
  4-hour walltime cap and force resume-juggling across 50 subjects. So
  fMRIprep runs with `--fs-no-reconall`, and `--cifti-output 91k` is dropped
  (CIFTI needs surfaces). This cuts the anat stage to ~30-90 min and fits the
  cap. Tradeoff: no surface/CIFTI outputs (unused) and slightly less precise
  BOLD-to-T1 coregistration. Worth a line in the methods section.
- **Offline TemplateFlow staging.** (May 28.) Teach compute nodes have no
  internet, so fMRIprep cannot fetch TemplateFlow templates at runtime — it
  hangs/fails. Pre-staged them on the login node into
  `~/templates/.cache/templateflow` (the school's scripts bind `~/templates`
  as the container `$HOME`, so the offline job reads templates from disk).
  Templates: MNI152NLin2009cAsym, MNI152NLin6Asym, OASIS30ANTs (the three
  needed once FreeSurfer is skipped). See `PIPELINE.md` step 4 for the
  commands.
- **`dataset_description.json` added to BIDS root.** (May 28.) dcm2bids left
  `~/adni/bids` without the required top-level `dataset_description.json`;
  fMRIprep's pybids indexer needs it even with `--skip-bids-validation`.
  Added a minimal one (Name, BIDSVersion 1.8.0, DatasetType raw). It's part
  of the dataset now and belongs in the repo's BIDS docs.
- **Single-job-per-subject batching + throttled submitter.** (May 28.) Since
  `--fs-no-reconall` makes a full anat+func run ~42 min (< 4h cap), we run the
  complete pipeline in ONE job per subject (`run2_fmri.sh`, which has no
  `--anat-only`) instead of the two-stage split. Both scripts were
  parameterized to take the BIDS label as `$1` (`export SUBJECT=$1`), so
  e.g. `sbatch run2_fmri.sh 011S4827`. The 49 remaining subjects are fed in by
  `~/adni/code/fmriprep/submit_all.sh` (run under `nohup`): a per-subject
  `until sbatch run2_fmri.sh "$SUBJ"; do sleep 120; done` loop that retries
  until the queue has room, never exceeding the 12-job cap. `run2_fmri.sh`
  ends with `if [ "$?" -eq 0 ]; then rm -rf <WORK_DIR>/fmriprep_25_2_wf/sub_<L>_wf; fi`
  to delete each subject's scratch on success. fMRIprep scripts (`run1_anat.sh`,
  `run2_fmri.sh`, `submit_all.sh`) + `dataset_description.json` all belong in
  the repo.
- **9 subjects preprocessed WITHOUT distortion correction.** (May 28.) Nine
  subjects (019S6585, 019S6712, 100S6713, 114S6039, 123S6825, 130S6072,
  177S6448, 305S6810, 305S6881) failed at workflow-build with
  `Fieldmap-less (SyN) estimation was requested, but PhaseEncodingDirection
  information appears to be absent` — their BOLD JSON sidecars have no
  `PhaseEncodingDirection`, which `--use-syn-sdc` requires. Re-ran these 9 with
  `--ignore fieldmaps slicetiming` (in place of `--use-syn-sdc`); all completed.
  RESULT: 41/50 ran with SyN distortion correction, 9/50 with none. Implication:
  the sgACC is dropout-prone, so the 9 uncorrected subjects are the highest risk
  in the step-5 coverage/tSNR QC — check them first. Methods/limitations line
  required. (Why only these 9 lack PE direction: likely a vendor/export quirk —
  several are Philips; not yet pinned down, and not worth pinning down unless
  the QC flags them.)

## Open questions / to confirm

- **Scanner-vendor confound.** Tally the Siemens/Philips/GE split per group
  (it's in the BIDS JSON `Manufacturer` field). Decide whether to add
  scanner/site as a group-analysis covariate or acknowledge it as a
  limitation.
- Exact grading weights and deadline dates — confirm against the syllabus
  (the ~20/30/30/20 split and June 5 / June 26 dates are unconfirmed).
- Final sgACC seed coordinate — to be chosen with a citation (Michael).
- sgACC signal coverage — confirm the seed region carries usable BOLD
  signal (tSNR / coverage check post-fMRIprep). See `PIPELINE.md` step 5.
  **Check the 9 no-distortion-correction subjects first** (listed in the
  decision log) — they have no SyN-SDC and the sgACC is dropout-prone.
