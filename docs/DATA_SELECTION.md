# Data Selection

## Source

ADNI (Alzheimer's Disease Neuroimaging Initiative), accessed through the
LONI Image & Data Archive (IDA). Phase: **ADNI3**.

## Selection criteria

- **Modality:** resting-state fMRI + a T1-weighted structural (MPRAGE),
  both required per subject (fMRIprep needs the T1).
- **Image type:** Original (raw DICOM), not pre/post-processed.
- **fMRI protocol:** single-band only — descriptions like
  `Axial rsfMRI (Eyes Open)` and `Axial fcMRI (Eyes Open)`. Multiband
  (`MB`) scans excluded to keep the acquisition protocol consistent.
- **T1:** `Accelerated Sagittal MPRAGE` / `Sagittal 3D Accelerated MPRAGE`.
  `_ND` (non-distortion-corrected) variants excluded.
- **Pairing:** the T1 and fMRI for each subject are from the same scan date.
- **Excluded entirely:** MoCoSeries, ASL/perfusion (relCBF,
  Perfusion_Weighted, pCASL, PASL), DTI, 3-plane localizers.

## Matching

The raw ADNI pools are imbalanced — AD skews male, CN skews female. To stop
sex and age from confounding the group comparison, the final sample was
built to be:

- **Sex-balanced:** 13 M / 12 F in each group.
- **Age-matched:** AD mean age 74.1 (range 55-91), CN mean age 74.6
  (range 56-95). Age difference between groups is not significant.

No subject appears in both groups.

## Selection process (what happened)

1. Searched ADNI3 by Research Group (AD, then CN), Modality = fMRI.
2. Found the searches returned non-resting-state scans mixed in (ASL, DTI,
   MoCo) — filtered to single-band rs-fMRI only.
3. Discovered many subjects had an fMRI scan but **no T1** in ADNI —
   fMRIprep can't run on those.
4. Re-ran advanced searches, identified subjects with confirmed T1 + fMRI,
   and replaced every incomplete subject.
5. Validated both final collections: each subject has exactly one T1 + one
   fMRI, single date, no multiband, no `_ND`.

## Final sample

### AD group (n = 25, 13 M / 12 F, mean age 74.1)

```
003_S_6264  M  55      035_S_6927  F  60      168_S_6735  F  79
011_S_4827  M  76      036_S_6179  M  79      168_S_6754  M  78
011_S_6303  M  70      100_S_6713  F  71      168_S_6827  M  68
013_S_6768  F  78      114_S_6039  M  56      168_S_6828  M  81
019_S_6585  F  63      114_S_6368  M  83      168_S_6843  F  68
019_S_6712  M  91      114_S_6595  M  80      168_S_6921  M  77
032_S_6600  F  71      123_S_6825  F  73      305_S_6810  M  73
035_S_6660  F  85      130_S_6072  F  89      305_S_6881  F  62
                       168_S_6142  F  86
```

### CN group (n = 25, 13 M / 12 F, mean age 74.6)

```
003_S_4350  M  81      035_S_4785  F  71      094_S_6419  M  76
011_S_7112  M  57      037_S_0303  M  95      109_S_6218  F  63
014_S_4401  F  73      037_S_0454  F  93      116_S_0382  F  88
014_S_6148  F  79      037_S_6031  F  67      116_S_4453  M  72
014_S_6366  M  59      041_S_6314  M  74      168_S_6321  M  73
014_S_6437  M  77      041_S_6447  F  71      177_S_6448  M  68
020_S_5140  F  75      068_S_0473  M  84      941_S_4292  M  77
032_S_4429  M  83      070_S_6191  F  56      941_S_6058  F  68
032_S_6293  F  86
```

## Notes for the methods section of the report

- State the data source (ADNI3), modalities, single-band-only criterion,
  and the sex/age matching — these are deliberate design choices worth
  describing.
- The sample is a deliberately matched subset, not a random draw — mention
  the matching procedure.
- The groups are AD and CN only — no MCI or SCD subjects. State this
  explicitly so the design reads as a clean two-group comparison.
- Limitation to acknowledge: ADNI is demographically narrow — the cohort is
  roughly 88% white and skews highly educated — so findings may not
  generalize to the broader population.
- Keep the two ADNI collection CSVs (the validated v2 exports) as the
  authoritative subject manifest.
