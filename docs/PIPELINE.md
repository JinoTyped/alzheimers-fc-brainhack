# Pipeline — Technical Steps

Step-by-step guide for the remaining work. Steps 1-3 are done; step 4
(fMRIprep) is next. Cluster paths below are on the SciNet Teach cluster
(`teach.scinet.utoronto.ca`, userid `lcl_uotmsc1127s1935`).

---

## Step 2 — Download DICOMs from ADNI  [DONE]

Downloaded both IDA Data Collections (AD, CN) as DICOM zips: 2 imaging
zips (~1.6 GB AD, ~1.4 GB CN) plus 2 IDA metadata zips. Transferred to
the SciNet Teach cluster with `scp` into `~/adni/`, then unzipped. The
DICOM layout is:

```
~/adni/ad_dicom/ADNI/<SUBJECT>/<SERIES>/<SCAN_DATETIME>/<IMAGE_UID>/*.dcm
~/adni/cn_dicom/ADNI/<SUBJECT>/<SERIES>/<SCAN_DATETIME>/<IMAGE_UID>/*.dcm
```

All 25 AD + 25 CN subjects present; each has exactly one T1 series and
one functional series — no extras, no fieldmaps. The data is multi-vendor
(Siemens + Philips, possibly GE) — see the `PROGRESS.md` decision log.

The original IDA metadata CSVs are unzipped under `~/adni/ad_metadata`
and `~/adni/cn_metadata` — keep these as the authoritative subject
manifest.

Note (Teach cluster): there is no `$SCRATCH` on Teach — all work lives in
`$HOME`, which is writable from compute nodes.

---

## Step 3 — DICOM to BIDS conversion  [DONE]

Tool: `dcm2bids` 3.2.0 (wraps `dcm2niix`).

Setup on the cluster:
```
module load python dcm2niix
python -m venv ~/venv_dcm2bids
source ~/venv_dcm2bids/bin/activate
pip install dcm2bids
```
`dcm2niix` comes from the cluster module; `dcm2bids` from pip. A later
session needs `module load python dcm2niix` and
`source ~/venv_dcm2bids/bin/activate` again.

Config: `~/adni/dcm2bids_config.json` — three rules, matched against the
JSON `SeriesDescription`:
- `*MPRAGE*`  -> `anat` / `T1w`   (catches all four MPRAGE name variants)
- `*rsfMRI*`  -> `func` / `bold`, `task-rest`
- `*fcMRI*`   -> `func` / `bold`, `task-rest`

The func rules add `TaskName: rest` via `sidecar_changes` (BIDS requires
it). Validated with `dcm2bids_helper` and test conversions before the
full run.

BIDS subject labels: the ADNI ID with underscores removed
(`003_S_6264` -> `sub-003S6264`).

Conversion: a resumable per-subject loop in `~/adni/run_dcm2bids_all.sh`
(skips subjects already converted), run with `nohup`, logging to
`~/adni/convert_all.log`. Output BIDS dataset: `~/adni/bids`.

RESULT: all 50 subjects converted, each with a `T1w` and a
`task-rest_bold` in `~/adni/bids`. One subject, `114_S_6039`, had blank
series-description metadata so the main config could not classify it; it
was converted separately with a fallback config
`~/adni/dcm2bids_config_114S6039.json` matching `MRAcquisitionType`
(`3D` -> T1w, `2D` -> bold). Both config files and the loop script belong
in the GitHub repo.

Optional before fMRIprep: run the BIDS Validator on `~/adni/bids`.

---

## Step 4 — fMRIprep preprocessing on SciNet  [IN PROGRESS]

The school provides the SciNet Teach cluster for this.

- fMRIprep container: `~/links/common/fmriprep-25.2.4.simg` (run via
  `apptainer`). FreeSurfer license: `~/links/common/fs_license.txt`.
- Access: `ondemand-teach.scinet.utoronto.ca` (web portal) or ssh.
- Job limits (CONFIRMED with a TA, May 26): 12 jobs may run at once,
  `--cpus-per-task=40` each, 4 hours max walltime per job. So the 50
  subjects can be batched in ~5 waves of 12.

The school's example scripts at `~/links/common/code_fmriprep_example/`
(`fmriprprep_run1anat_example.sh`, `fmriprprep_run1fMRI_example.sh`) split
the work into an anat stage and a functional stage. They bind `~/templates`
as the container `$HOME` (`-B ${FMRIPREP_HOME}:/home/fmriprep --home
/home/fmriprep`) and run with `--cleanenv` — that detail is what makes the
offline-template fix below work.

### 4a — Offline TemplateFlow staging (REQUIRED FIRST)

Teach compute nodes have NO internet, so fMRIprep cannot fetch TemplateFlow
templates at runtime — the job hangs/fails. Pre-download them on the login
node (which does have internet) into the directory the container reads from.
Because the container `$HOME` is `~/templates`, fMRIprep looks for templates
at `~/templates/.cache/templateflow`. Done May 28:

```
module load python
python3 -m venv ~/venv_templateflow
source ~/venv_templateflow/bin/activate
pip install templateflow
export TEMPLATEFLOW_HOME=~/templates/.cache/templateflow
python -c "import templateflow.api as t; [t.get(x) for x in ['MNI152NLin2009cAsym','MNI152NLin6Asym','OASIS30ANTs']]"
```

Those three templates are all that's needed once FreeSurfer is skipped (no
fsaverage/fsLR). If a job ever errors on a missing template, the log names
it — fetch that one on the login node and resubmit. (If `pip install` prints
"Defaulting to user installation", the venv's own pip isn't being used —
usually a half-created venv; `rm -rf` it, recreate, and check `which pip`
points inside the venv.)

### 4b — BIDS dataset fix

`~/adni/bids` was missing the required top-level `dataset_description.json`
(dcm2bids didn't scaffold it). fMRIprep's pybids indexer hard-requires it
even with `--skip-bids-validation`. Added a minimal one:

```
{"Name": "ADNI3 sgACC functional connectivity", "BIDSVersion": "1.8.0", "DatasetType": "raw"}
```

### 4c — Adapted run scripts

Adapted from the school's two example scripts. Two deliberate changes from
the examples (see PROGRESS decision log):
- added `--fs-no-reconall` — we do volumetric seed-to-voxel FC, no surfaces;
  skipping FreeSurfer drops a full run to ~42 min total
- dropped `--cifti-output 91k` — CIFTI needs surfaces

Other substitutions from the `ds003768` placeholders: `BIDS_DIR=~/adni/bids`,
output `~/derivatives/adni/fmriprep/25.2.4`, work `~/work/adni/fmriprep`.
Both scripts were parameterized to take the BIDS label (WITHOUT the `sub-`
prefix) as `$1`: `export SUBJECT=$1`, so `sbatch run2_fmri.sh 011S4827`.

- `~/adni/code/fmriprep/run1_anat.sh` — adds `--anat-only` (only needed if you
  ever want to split the stages; for batching we don't use it).
- `~/adni/code/fmriprep/run2_fmri.sh` — the FULL pipeline: no `--anat-only`,
  plus `--use-syn-sdc` (fieldmap-less distortion correction — matters for the
  sgACC) and `--ignore slicetiming`. On a fresh subject this does anat+func in
  one ~42-min job. It ends with a line that deletes that subject's scratch on
  success: `if [ "$?" -eq 0 ]; then rm -rf <WORK_DIR>/fmriprep_25_2_wf/sub_<L>_wf; fi`.
- `~/adni/code/fmriprep/submit_all.sh` — the throttled batch submitter (below).

Single-subject test (proven on sub-003S6264): submit from the script folder
(the `#SBATCH --output=logs/%x_%j.out` path is relative, so `logs/` must
already exist there):

```
cd ~/adni/code/fmriprep
sbatch run2_fmri.sh 003S6264
squeue -u $USER                       # PD = queued, R = running
tail -40 logs/fmriprep_fmri_<JOBID>.out   # plain tail; -f follows and won't return until Ctrl+C
```

Success = the log ends with `fMRIPrep finished successfully` and the `func/`
folder has `..._space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz` and
`..._desc-confounds_timeseries.tsv`.

### 4d — Batching all 50 (the SciNet queue cap)

The Teach limit is **12 jobs in the QUEUE total** (running + pending), not 12
running — a dependency-chained batch overflows it instantly. So: ONE full job
per subject (`run2_fmri.sh`), fed in by a throttled submitter that retries
until there's room. `~/adni/code/fmriprep/submit_all.sh`:

```
#!/bin/bash
cd ~/adni/code/fmriprep
for SUBJ in $(ls ~/adni/bids | sed -n 's/^sub-//p'); do
  [ "$SUBJ" = "003S6264" ] && continue
  until sbatch run2_fmri.sh "$SUBJ"; do
    echo "$(date) queue full — waiting to submit $SUBJ"; sleep 120
  done
  echo "$(date) submitted $SUBJ"; sleep 10
done
echo "$(date) ALL SUBMITTED"
```

Launch it in the background so it survives disconnecting:
```
chmod +x ~/adni/code/fmriprep/submit_all.sh
nohup ~/adni/code/fmriprep/submit_all.sh > ~/adni/code/fmriprep/submit_all.log 2>&1 &
```

Monitor: `tail ~/adni/code/fmriprep/submit_all.log`, `squeue -u $USER`,
`ls ~/derivatives/adni/fmriprep/25.2.4/ | grep -c '^sub-'` (climbs to 50).

**Verify + re-run** once the queue is empty. List subjects missing the final
BOLD (read-only):
```
for SUBJ in $(ls ~/adni/bids | sed -n 's/^sub-//p'); do
  f=~/derivatives/adni/fmriprep/25.2.4/sub-$SUBJ/func/sub-${SUBJ}_task-rest_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz
  [ -f "$f" ] || echo "MISSING: $SUBJ"
done
```
For any `MISSING`, resubmit (same loop but `[ -f "$f" ] && continue` before
the `until sbatch ...`); fMRIprep resumes leftover work. Repeat until the
check prints nothing. Failure scan:
`sacct -X --starttime today --format=JobID,JobName%18,State,ExitCode | grep -v COMPLETED`.

### Status (May 28)

- Full pipeline PROVEN end-to-end on sub-003S6264 (anat ~21 min, func ~22 min,
  both `0:0`). All offline/template/BIDS issues resolved.
- Remaining 49 subjects launched via `submit_all.sh` under `nohup` — running.
- Outputs: preprocessed BOLD in MNI152NLin6Asym:res-2 + a `confounds` TSV per
  subject (head-motion covariate comes from the TSV). Per-subject disk ~3 GB
  (work auto-deleted on success → ~1 GB derivatives kept).

Target: all preprocessing done by end of Week 3.

---

## Step 5 — Seed-based functional connectivity (Nilearn)

Per subject, on the fMRIprep output:

1. Define the **sgACC seed** — a sphere (commonly 6 mm radius) at a chosen
   MNI coordinate. Pick the coordinate from a published paper and cite it.
2. **Check seed signal coverage.** The sgACC sits in the ventromedial /
   orbitofrontal region prone to susceptibility-induced signal dropout in
   EPI — voxels there can carry little usable BOLD signal. Before trusting
   any FC value, inspect tSNR / coverage in the seed region per subject
   (fMRIprep outputs a tSNR map; XCP-D produces an explicit coverage map).
   Set a tSNR/coverage threshold, then confirm all 50 subjects pass or flag
   the ones that don't. Raised at the proposal meeting — do not skip it.
3. Extract the mean BOLD time series from the seed
   (`NiftiSpheresMasker`), with confound regression (motion, etc. from the
   fMRIprep confounds file).
4. Compute correlation between the seed time series and every voxel ->
   a seed-to-voxel FC map.
5. Apply a **Fisher z-transform** to the correlation maps so they're
   suitable for group statistics.

This code can be written and debugged NOW on a test subject or public
dataset, in parallel with steps 3-4.

---

## Step 6 — Group analysis (AD vs CN)

1. Collect the per-subject Fisher-z FC maps into two groups.
2. Run a second-level (group) model comparing AD vs CN, with **age, sex,
   and head motion** as covariates (Nilearn's `SecondLevelModel`).
   Consider adding scanner/vendor as an additional covariate — the sample
   is multi-vendor (see `PROGRESS.md` decision log + open questions).
3. Apply multiple-comparison correction (e.g. cluster-level thresholding).
4. Report where sgACC connectivity differs between groups.

---

## Step 7 — Figures, presentation, report

- Brain figures of the group difference maps (Nilearn plotting).
- Presentation for **June 5** (confirm date against the syllabus).
- Final report by **June 26** (confirm date) — include the methods detail
  from `DATA_SELECTION.md`.

---

## GitHub repo structure (set up now)

```
alzheimers-fc-brainhack/
  code/
    01_organize_bids.py
    preprocessing/        # fMRIprep scripts
    03_connectivity.py    # Nilearn seed-to-voxel FC
    04_group_analysis.py  # AD vs CN second-level
  docs/                   # subject manifests, this knowledge base
  data/                   # local only — gitignored
  results/                # local only — gitignored
  README.md
  requirements.txt
  .gitignore
```

For BIDS organization (`01_organize_bids.py` above), the actual artifacts
are `dcm2bids_config.json`, `dcm2bids_config_114S6039.json`, and
`run_dcm2bids_all.sh` from step 3 — these belong in the repo.

`.gitignore` MUST exclude `data/`, `results/`, and all imaging files
(`*.nii`, `*.nii.gz`, `*.dcm`). ADNI data must never be committed — it's
against the data use agreement and would blow past size limits. The repo
holds code only.
