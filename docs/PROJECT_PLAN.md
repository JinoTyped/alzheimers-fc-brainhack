# Project Plan

## Research question

Does resting-state functional connectivity of the subgenual anterior
cingulate cortex (sgACC) differ between Alzheimer's disease patients and
cognitively normal older adults?

## Approach

1. Pull resting-state fMRI + T1 structural data from ADNI3.
2. Convert to BIDS, preprocess with fMRIprep on SciNet.
3. Define an sgACC seed; compute per-subject seed-to-voxel FC maps in
   Nilearn; Fisher z-transform.
4. Second-level group comparison AD vs CN, with age, sex, and head motion
   as covariates.
5. Visualize results, present, write the report.

## Team

| Person | Role |
|--------|------|
| Zaki | Project lead. Data pipeline: download -> BIDS -> fMRIprep. |
| Jino | Repo setup, figures/deck scaffolding, preprocessing support. |
| Michael | Nilearn FC analysis code, sgACC seed coordinate, visualization. |
| Lyanne | Took the course last year — debugging / sanity-check resource; ran a separate rsfMRI analysis. **Not presenting Fri June 5** (her slide was cut); stays on title/thanks as a team member. |
| Rehan | Not contributing — plan around. |
| Gabby | Not contributing — plan around. |

Effective working team is **Zaki, Jino, Michael**. The peer-engagement
portion of the grade depends on *your own* participation in reviewing other
groups' work, not on whether Rehan/Gabby contribute — so their absence
costs nothing grade-wise.

## Timeline

| When | Where | Focus |
|------|-------|-------|
| Done | — | Project pitch presentation |
| Week 3 — Tue May 26, Wed May 27 | SciNet Classroom, Suite 1140, 661 University Ave (arrive before 10am) | Download data, BIDS conversion, run fMRIprep |
| Week 4 — Mon June 1 | TMU Atrium on Bay | Instructor check-in on preprocessing progress; finalize analysis |
| Week 4 — Thu/Fri June 4-5 | Data Sciences Institute, 700 University Ave | Final figures; **present Fri June 5, 3:00–3:20 pm** (confirmed; ~7 min talk, presenters Michael/Zaki/Jino) |
| By June 26 | — | Final report submitted |

**Goal for end of Week 3:** preprocessing finished and the analysis
pipeline running end-to-end. The school explicitly wants preprocessing done
in Week 3 so Week 4 is free for analysis and the presentation. Groups behind
on preprocessing at the June 1 check-in may be told to pivot to
already-preprocessed data.

## Deliverables and grading

- Project pitch — done
- Completed-project presentation — June 5
- Final report — June 26
- Peer engagement — ongoing (reviewing other groups)

(Weights were ~20/30/30/20 per earlier discussion — verify against the
official syllabus.)

## Parallelization strategy

Don't let everyone idle while data downloads and preprocesses. Run three
tracks at once:

- **Zaki:** download -> BIDS -> fMRIprep (the data pipeline).
- **Michael:** write and debug the Nilearn FC code *now* against one test
  subject or a public dataset, so it's ready the moment preprocessed data
  exists. Also lock the sgACC seed coordinate (needs no data).
- **Jino:** set up the GitHub repo today; start the presentation deck
  scaffold; help with preprocessing once data is down.

## Known risks

- **Preprocessing time.** fMRIprep is slow. Mitigation: test on ONE subject
  before batching all 50; use SciNet's parallel jobs.
- **Scan-protocol consistency.** Resolved — sample is single-band rs-fMRI
  only, no multiband mixing.
- **sgACC signal dropout.** The seed region is prone to susceptibility
  artifact / signal loss in EPI, so FC values there can be unreliable.
  Mitigation: tSNR / coverage check on the seed after fMRIprep
  (`PIPELINE.md` step 5); check for fieldmaps at DICOM conversion and use
  distortion correction if available.
- Slide fix in progress: the pitch timeline slide said "task-based fMRI" — the
  project is resting-state. Being corrected in the final deck (slide 3) before
  it reaches the report.
