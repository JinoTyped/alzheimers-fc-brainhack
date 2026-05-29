# Context for Continuing in a New Chat

Paste this into a new AI chat to bring it up to speed instantly. Then attach
whichever other knowledge base files are relevant, plus your current data files.

---

I'm working on a group project for BrainHack School 2026 (a neuroimaging
summer school in Toronto). I'm the project lead. Here's the full context.

**The project:** a seed-based resting-state functional connectivity (FC)
analysis of the subgenual anterior cingulate cortex (sgACC), comparing
Alzheimer's disease (AD) patients vs cognitively normal (CN) controls.

**Data:** ADNI, phase ADNI3. Resting-state fMRI + T1 structural (MPRAGE),
DICOM format. Final sample is 25 AD + 25 CN, sex-balanced (13 M / 12 F per
group) and age-matched (~74 mean age both groups). Single-band rs-fMRI only
(no multiband). The data is multi-vendor (Siemens + Philips, possibly GE).

**Tools/plan:** convert DICOM to BIDS with dcm2bids, preprocess with
fMRIprep on the SciNet Teach cluster, run seed-based FC in Nilearn, then a
group comparison (AD vs CN) with age/sex/motion as covariates.

**Team:** effective working team is me (Zaki), Jino, and Michael. Two other
members aren't contributing — plan around them.

**Timeline:** Week 3 (May 26-28) — get data downloaded, converted to BIDS,
and preprocessed. Completed-project presentation ~June 5, final report
~June 26 (dates unconfirmed — verify against the syllabus).

**Where I am right now (May 28, Week 3 Day 3):** Subject selection, the ADNI
download, and DICOM-to-BIDS conversion are DONE — all 50 subjects are in BIDS
on the SciNet Teach cluster at `~/adni/bids`. **fMRIprep preprocessing is now
working and batching.** The full pipeline is PROVEN end-to-end on one subject
(`sub-003S6264`: anat ~21 min + func ~22 min, both clean), and the remaining
49 are running via a throttled background submitter. Key things that got
solved to make it work:

- **Offline templates:** Teach compute nodes have no internet, so TemplateFlow
  was pre-staged on the login node into `~/templates/.cache/templateflow`
  (MNI152NLin2009cAsym, MNI152NLin6Asym, OASIS30ANTs) via a `templateflow` pip
  venv. The school's scripts bind `~/templates` as the container `$HOME`, so
  the offline jobs read templates from disk.
- **`--fs-no-reconall`:** we skip FreeSurfer surfaces (our FC is volumetric
  seed-to-voxel), which drops a full run to ~42 min — so we run the whole
  anat+func pipeline in ONE job per subject (no two-stage split). `--cifti-output`
  dropped accordingly.
- **SciNet "12-job" limit is 12 jobs in the QUEUE total** (running + pending),
  not 12 running. So batching uses a throttled submitter
  (`~/adni/code/fmriprep/submit_all.sh`, run under `nohup`) that retries until
  there's room. Each func script auto-deletes its scratch on success.
- **`dataset_description.json`** had to be added to `~/adni/bids` (dcm2bids
  didn't scaffold it; fMRIprep's indexer requires it).

Scripts live in `~/adni/code/fmriprep/` (`run1_anat.sh`, `run2_fmri.sh`,
`submit_all.sh`); outputs in `~/derivatives/adni/fmriprep/25.2.4/`.
**Immediate next steps:** (1) let the batch finish, then verify all 50 have
their final BOLD and re-run any missing (see `PROGRESS.md` "What's next" +
`PIPELINE.md` step 4d); (2) sgACC seed-region coverage / tSNR QC before
trusting FC; (3) Michael: lock the sgACC seed coordinate + Nilearn seed-to-voxel
FC; then AD-vs-CN group analysis with age/sex/motion covariates. See
`PROGRESS.md` and `PIPELINE.md` for full detail (cluster paths, scripts,
decision log).

**What I need help with:** [DESCRIBE YOUR CURRENT QUESTION HERE]

---

## How to keep this knowledge base current

After any significant work session, update:

- `PROGRESS.md` — move steps from NOT STARTED to DONE, add to the decision log
- `PROJECT_PLAN.md` — if roles, timeline, or scope change
- `DATA_SELECTION.md` — if the sample changes
- `PIPELINE.md` — fill in the specifics (config files, commands, coordinates)
  once each step is actually run

Update the "Last updated" date in `PROGRESS.md` each time.
