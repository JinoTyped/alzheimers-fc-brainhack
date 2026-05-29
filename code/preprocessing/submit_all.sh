#!/bin/bash
cd ~/adni/code/fmriprep
for SUBJ in $(ls ~/adni/bids | sed -n 's/^sub-//p'); do
  [ "$SUBJ" = "003S6264" ] && continue
  until sbatch run2_fmri.sh "$SUBJ"; do
    echo "$(date) queue full — waiting to submit $SUBJ"
    sleep 120
  done
  echo "$(date) submitted $SUBJ"
  sleep 10
done
echo "$(date) ALL SUBMITTED"
