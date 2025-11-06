#!/usr/bin/env bash
# Script to run Poisson resampling bootstrapping for a dataset, for different scale factors and repetitions
# and zip up all the results

# nohup bash SIRF_data_preparation/run_bootstrap_OSEM.sh 2>&1 > great_sfs_run.log &

export PETRIC_SKIP_DATA=1
# dataset=$1
# datasets="NeuroLF_Hoffman_Dataset"
datasets="GE_D690_NEMA_IQ GE_DMI3_Torso GE_DMI4_NEMA_IQ Mediso_NEMA_IQ NeuroLF_Esser_Dataset NeuroLF_Hoffman_Dataset Siemens_mMR_ACR Siemens_mMR_NEMA_IQ Siemens_Vision600_Hoffman Siemens_Vision600_thorax Siemens_Vision600_ZrNEMAIQ"
# sfs="$2"
sfs="1 1e-1 1e-2 1e-3"
# reps="$3"
reps="1"
for dataset in $datasets; do
 for sf in $sfs; do
  for rep in $reps; do
    # python -m SIRF_data_preparation.noise_bootstrap --srcdir=/data/ --dataset=${dataset}  --scale_factor=${sf} --outname=${dataset}_${sf}_${rep}
    python -m SIRF_data_preparation.data_QC --srcdir=output/${dataset}_${sf}_${rep} --dataset=${dataset} --skip_sino_profiles --skip_VOI_plots --no_plot_wait --VOIdir=/data/${dataset}/PETRIC
  done
 done
 echo "Zipping results for dataset ${dataset}\n\n\n"
 pushd output
 find .  \( -path ./${dataset}'*OSEM_image*' -o -path ./${dataset}'*VOI*csv' \) -exec zip -u bootstrap_results_${dataset}.zip {} +
 popd
done
# cd output

