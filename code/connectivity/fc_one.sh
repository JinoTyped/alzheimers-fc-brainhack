#!/bin/bash
#SBATCH --cpus-per-task=40
#SBATCH --time=0:40:00
#SBATCH --output=logs/fc_%j.out
module load python
source ~/venv_nilearn/bin/activate
cd ~/adni/code
S="$1"
OUT=~/derivatives/adni/fmriprep/25.2.4/sub-$S/func/sub-${S}_task-rest_space-MNI152NLin6Asym_res-2_desc-sgaccFCz.nii.gz
[ -f "$OUT" ] && { echo "skip $S (exists)"; exit 0; }
python -c "import os; from fc_utilities import first_level; first_level(os.path.expanduser('~/derivatives/adni/fmriprep/25.2.4'), '$S', bids_root=os.path.expanduser('~/adni/bids'))"
