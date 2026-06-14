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
- **Seed:** sgACC, MNI (6, 16, -10), 5 mm sphere (Fox et al. 2012)
- **Sample:** 25 AD + 25 CN, sex-balanced and age-matched

## Knowledge base index

| File | What's in it |
|------|--------------|
| `README.md` | This file — project overview and index |
| `PROJECT_PLAN.md` | Goals, team roles, timeline, deadlines, deliverables |
| `PROGRESS.md` | Status tracker — what's done, what's not, decision log |
| `DATA_SELECTION.md` | How the 50 subjects were chosen + the final subject lists |
| `PIPELINE.md` | Step-by-step technical record (commands, paths, code) |
| `CONTEXT_FOR_AI.md` | Paste into a fresh AI chat to continue planning anywhere |

## Where things stand (short version)

**The whole pipeline is built and run end-to-end.** Preprocessing is complete
on all 50 subjects; the seed-to-voxel FC ran on everyone at the Fox 2012 sgACC
seed (5 mm); the AD-vs-CN second-level model is done.

**Result + key finding:** there is no significant AD-vs-CN difference at FDR
q<0.05. A seed coverage/tSNR QC revealed *why* — the sgACC seed carries
systematically worse signal in AD than CN (mean tSNR ~30 vs ~43), driven
largely by one scanner site (168) that is concentrated in the AD group. So the
comparison is confounded by seed-region signal quality / scanner site and can't
be read as a disease effect. **This QC finding is the project's headline** and
anchors the presentation. See `PROGRESS.md` for the full status + decision log.

Remaining work: **none blocking.** The June 5 presentation is done and the
gallery report (the sole graded deliverable) was submitted as **PR #430** to the
BrainHack website on June 14 — now awaiting maintainer merge. The IMS
peer-assessment form is in. Figures are pulled locally ahead of the June 21
cluster cutoff. See `PROGRESS.md` for the full status + decision log.

## Key deadlines

- **June 5** — completed-project presentation (done)
- **June 26** — final report = gallery PR (CONFIRMED; submitted as PR #430, awaiting merge)

(Deadline confirmed via Erin Dickie's June 8 announcement. Course is
credit/no-credit for Zaki via IMS.)
