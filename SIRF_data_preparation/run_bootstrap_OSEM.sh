#!/usr/bin/env bash
# Script to run Poisson resampling bootstrapping for a dataset, for different scale factors and repetitions
# and zip up all the results

dataset=$1
sfs="$2"
reps="$3"
srcdir="$4"
for sf in $sfs; do
 for rep in $reps; do
   python -m SIRF_data_preparation.noise_bootstrap --dataset=${dataset} --srcdir="${srcdir}" --scale_factor=${sf} --outname=${dataset}_${sf}_${rep}
   python -m SIRF_data_preparation.data_QC --srcdir=output/${dataset}_${sf}_${rep} --dataset=${dataset} --skip_sino_profiles --skip_VOI_plots --no_plot_wait
 done
done
cd output
find ./  \( -path ./${dataset}'*OSEM_image_slices.png' -o -path ./${dataset}'*VOI*csv' \) -exec zip -u bootstrap_results_${dataset}.zip {} +
