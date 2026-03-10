#! /bin/bash
export PETRIC_SRCDIR=data
export PETRIC_OUTDIR=output
export dataset=GE_DMI3_Torso2
export template_dataset=GE_DMI3_Torso
export fullcounts_DIR=/mnt/share-public/petric/1/$template_dataset
export sf=1
export noise_sf=$(python -c "from SIRF_data_preparation.dataset_settings import preferred_scaling as s; print(s['$dataset'], end='')")
SIRF_data_preparation/generate_dataset_with_bootstrapping.sh

#pushd data
#mv ${dataset} /mnt/share-public/petric/2/
#ln -s /mnt/share-public/petric/2/${dataset}
#popd
