#!/bin/bash
#SBATCH --job-name=fmriprep_fmri
#SBATCH --output=logs/%x_%j.out
#SBATCH --nodes=1
#SBATCH --cpus-per-task=40
#SBATCH --time=3:59:00
export BIDS_DIR=${HOME}/adni/bids
export SUBJECT=$1
export FMRIPREP_HOME=${HOME}/templates
export SING_CONTAINER=${HOME}/links/common/fmriprep-25.2.4.simg
export FS_LICENSE=${HOME}/links/common/fs_license.txt
export OUTPUT_DIR=${HOME}/derivatives/adni/fmriprep/25.2.4
export WORK_DIR=${HOME}/work/adni/fmriprep
mkdir -vp ${OUTPUT_DIR} ${WORK_DIR}
function cleanup_ramdisk {
    echo -n "Cleaning up ramdisk directory /$SLURM_TMPDIR/ on "
    date
    rm -rf /$SLURM_TMPDIR
    echo -n "done at "
    date
}
trap "cleanup_ramdisk" TERM
apptainer run --cleanenv \
    -B ${FMRIPREP_HOME}:/home/fmriprep --home /home/fmriprep \
    -B ${BIDS_DIR}:/bids \
    -B ${OUTPUT_DIR}:/derived \
    -B ${WORK_DIR}:/work \
    -B ${FS_LICENSE}:/li \
    ${SING_CONTAINER} \
    /bids /derived participant \
    --participant_label ${SUBJECT} \
    -w /work \
    --skip-bids-validation \
    --omp-nthreads 40 \
    --nthreads 40 \
    --mem-mb 60000 \
    --output-space MNI152NLin6Asym:res-2 \
    --notrack \
    --fs-no-reconall \
    --ignore fieldmaps slicetiming \
    --fs-license-file /li

if [ "$?" -eq 0 ]; then rm -rf "${WORK_DIR}/fmriprep_25_2_wf/sub_${SUBJECT}_wf"; fi
