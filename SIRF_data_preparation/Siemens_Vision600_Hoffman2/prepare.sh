#!/bin/bash
# starting from data prepared by Nicole Jurjew from UMCG Hoffman2 data-set
# using https://github.com/UCL/STIR/blob/master/examples/python/Vision_files_preprocess.py

tmpPETRIC_SRCDIR=/mnt/share-public/petric/wip/petric2/orgdata/
dataset=Siemens_Vision600_Hoffman2

pushd $tmpPETRIC_SRCDIR/$dataset
fullcounts_DIR=${tmpPETRIC_SRCDIR}/${dataset}/fullcounts
mkdir fullcounts
cd fullcounts
# threshold additive_term to min 0
stir_math -s --including-first --min-threshold 0 additive_term.hs ../*additive_term.hs
# link other files as opposed to copying
# note: header needs to have PETRIC2 name, but data needs to have original name, as that's how it's referred to in the header.
ln -s ../*prompts.hs prompts.hs
ln -s ../*prompts.s
ln -s ../*mult_factors_forSIRF.hs mult_factors.hs
ln -s ../*mult_factors_forSIRF.s

PETRIC_SRCDIR=${tmpPETRIC_SRCDIR} python -m SIRF_data_preparation.create_initial_images ${fullcounts_DIR} -t $tmpPETRIC_SRCDIR/$dataset/23_UMCG_Hoff_STIRRecon_10.hv
list_image_info ${tmpPETRIC_SRCDIR}/fullcounts/OSEM_image.hv
# MANUAL: edit dataset_settings.py and petric.py, limits based on max above, set preferred_scaling to 1 to get descent images from data_QC
mkdir PETRIC
PETRIC_SRCDIR=${tmpPETRIC_SRCDIR} python -m SIRF_data_preparation.create_Hoffman_VOIs --dataset ${dataset} --srcdir ${fullcounts_DIR}
PETRIC_SRCDIR=${tmpPETRIC_SRCDIR} python -m SIRF_data_preparation.data_QC --dataset ${dataset} --srcdir ${fullcounts_DIR} --VOIdir ${fullcounts_DIR}/PETRIC
# MANUAL: edit dataset_settings.py preferred_scaling to ratio of total counts in ${fullcounts_DIR}/prompts.hs and $PETRIC_SRCDIR/Siemens_Vision600_Hoffman/prompts.hs
