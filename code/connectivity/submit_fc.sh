#!/bin/bash
cd ~/adni/code
for S in $(ls ~/adni/bids | sed -n 's/^sub-//p'); do
  OUT=~/derivatives/adni/fmriprep/25.2.4/sub-$S/func/sub-${S}_task-rest_space-MNI152NLin6Asym_res-2_desc-sgaccFCz.nii.gz
  [ -f "$OUT" ] && { echo "skip $S"; continue; }
  until sbatch fc_one.sh "$S"; do echo "queue full, waiting ($S)"; sleep 60; done
  sleep 3
done
echo "all submitted"
