# skeleton file for preparing the NeuroLF data
tmpPETRIC_SRCDIR=/mnt/share-public/petric/wip/petric2/orgdata/
dataset=NeuroLF_Esser2
python -m SIRF_data_preparation.${dataset}.prepare
# MANUAL: copy energy window info from list-mode randoms.hs to in processing/prompts*hs and re-run
python -m SIRF_data_preparation.${dataset}.prepare

fullcounts_DIR=${tmpPETRIC_SRCDIR}/${dataset}/fullcounts
cd ${fullcounts_DIR}
ln -s ../VOIs PETRIC
cd ..
PETRIC_SRCDIR=${tmpPETRIC_SRCDIR} python -m SIRF_data_preparation.create_initial_images ${fullcounts_DIR}/
list_image_info ${tmpPETRIC_SRCDIR}/fullcounts/OSEM_image.hv
# MANUAL: edit dataset_settings.py and petric.py, limits on based on max above, set preferred_scaling to 1 to get descent images
PETRIC_SRCDIR=${tmpPETRIC_SRCDIR} python -m SIRF_data_preparation.data_QC --dataset ${dataset} --srcdir ${fullcounts_DIR} --VOIdir ${fullcounts_DIR}/PETRIC
# MANUAL: edit dataset_settings.py preferred_scaling to ratio of total counts in ${fullcounts_DIR}/prompts.hs and $PETRIC_SRCDIR/NeuroLF_Hoffman_Dataset/prompts.hs
