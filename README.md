# sgACC Functional Connectivity in Alzheimer's Disease

BrainHack School 2026 (Toronto) group project.

## What this project is

A seed-based resting-state functional connectivity (FC) analysis of the
**subgenual anterior cingulate cortex (sgACC)**, comparing **Alzheimer's
disease (AD)** patients against **cognitively normal (CN)** controls.

- **Data:** ADNI (ADNI3 phase), resting-state fMRI + T1 structural
- **Preprocessing:** fMRIprep, run on the SciNet Teach cluster
- **Analysis:** seed-based seed-to-voxel FC in Nilearn, then a group
  comparison (AD vs CN)
- **Sample:** 25 AD + 25 CN, sex-balanced and age-matched

## Knowledge base index

| File | What's in it |
|------|--------------|
| `README.md` | This file — project overview and index |
| `PROJECT_PLAN.md` | Goals, team roles, timeline, deadlines, deliverables |
| `PROGRESS.md` | Status tracker — what's done, what's not, decision log |
| `DATA_SELECTION.md` | How the 50 subjects were chosen + the final subject lists |
| `PIPELINE.md` | Step-by-step technical guide for the remaining work |
| `CONTEXT_FOR_AI.md` | Paste this into a fresh AI chat to continue planning anywhere |

## Where things stand (short version)

Subjects are **selected**, the ADNI DICOMs are **downloaded**, and
**DICOM-to-BIDS conversion is complete** — all 50 subjects (25 AD + 25 CN)
are in BIDS on the SciNet Teach cluster at `~/adni/bids`. **fMRIprep
preprocessing is working and batching:** the full pipeline is proven
end-to-end on one subject and the remaining 49 are running on SciNet. Next:
verify all 50 outputs, then the sgACC seed coordinate + coverage check and
the Nilearn seed-to-voxel FC. See `PROGRESS.md` for the full checklist.

## Key deadlines

- **June 5** — completed-project presentation
- **June 26** — final report

(Confirm exact dates/weights against the BrainHack syllabus.)
