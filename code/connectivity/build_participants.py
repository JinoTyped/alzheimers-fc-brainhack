"""
Build participants.tsv for the AD-vs-CN second-level model.

- group/age/sex are taken from DATA_SELECTION.md (the locked sample).
    group: AD = 1, CN = 0
    sex:   M  = 1, F  = 0
- mean_fd is computed per subject from the fMRIprep confounds file
  (mean framewise displacement; the NaN first frame is skipped).

Run on the cluster from ~/adni/code (after the FC batch, or anytime the
fMRIprep derivatives exist):

    source ~/venv_nilearn/bin/activate
    cd ~/adni/code
    python build_participants.py

Writes ~/adni/code/participants.tsv, which second_level() reads.
"""

import os
import pandas as pd
from fc_utilities import mean_fd

DERIV = os.path.expanduser("~/derivatives/adni/fmriprep/25.2.4")

# (participant_id, group, age, sex)  -- group AD=1/CN=0, sex M=1/F=0
ROWS = [
    # --- AD (group = 1) ---
    ("003S6264", 1, 55, 1), ("011S4827", 1, 76, 1), ("011S6303", 1, 70, 1),
    ("013S6768", 1, 78, 0), ("019S6585", 1, 63, 0), ("019S6712", 1, 91, 1),
    ("032S6600", 1, 71, 0), ("035S6660", 1, 85, 0), ("035S6927", 1, 60, 0),
    ("036S6179", 1, 79, 1), ("100S6713", 1, 71, 0), ("114S6039", 1, 56, 1),
    ("114S6368", 1, 83, 1), ("114S6595", 1, 80, 1), ("123S6825", 1, 73, 0),
    ("130S6072", 1, 89, 0), ("168S6142", 1, 86, 0), ("168S6735", 1, 79, 0),
    ("168S6754", 1, 78, 1), ("168S6827", 1, 68, 1), ("168S6828", 1, 81, 1),
    ("168S6843", 1, 68, 0), ("168S6921", 1, 77, 1), ("305S6810", 1, 73, 1),
    ("305S6881", 1, 62, 0),
    # --- CN (group = 0) ---
    ("003S4350", 0, 81, 1), ("011S7112", 0, 57, 1), ("014S4401", 0, 73, 0),
    ("014S6148", 0, 79, 0), ("014S6366", 0, 59, 1), ("014S6437", 0, 77, 1),
    ("020S5140", 0, 75, 0), ("032S4429", 0, 83, 1), ("032S6293", 0, 86, 0),
    ("035S4785", 0, 71, 0), ("037S0303", 0, 95, 1), ("037S0454", 0, 93, 0),
    ("037S6031", 0, 67, 0), ("041S6314", 0, 74, 1), ("041S6447", 0, 71, 0),
    ("068S0473", 0, 84, 1), ("070S6191", 0, 56, 0), ("094S6419", 0, 76, 1),
    ("109S6218", 0, 63, 0), ("116S0382", 0, 88, 0), ("116S4453", 0, 72, 1),
    ("168S6321", 0, 73, 1), ("177S6448", 0, 68, 1), ("941S4292", 0, 77, 1),
    ("941S6058", 0, 68, 0),
]

records = []
missing = []
for pid, group, age, sex in ROWS:
    try:
        fd = mean_fd(DERIV, pid)
    except Exception as e:
        missing.append((pid, str(e)))
        fd = float("nan")
    records.append({"participant_id": pid, "group": group,
                    "age": age, "sex": sex, "mean_fd": fd})

df = pd.DataFrame(records)
out = os.path.join(os.path.dirname(__file__) or ".", "participants.tsv")
df.to_csv(out, sep="\t", index=False)

print(df.to_string(index=False))
print(f"\nwrote {out}  ({len(df)} subjects)")
if missing:
    print("\nCOULD NOT READ mean_fd for:")
    for pid, err in missing:
        print(f"  {pid}: {err}")
    print("(re-run after the FC batch finishes — confounds files must exist)")
