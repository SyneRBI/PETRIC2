# skeleton file for preparing the NeuroLF data
tmpPETRIC_SRCDIR=/mnt/share-public/petric/wip/petric2/orgdata/
dataset=Siemens_mMR_Hoffman

pushd $tmpPETRIC_SRCDIR/$dataset
pushd petraw/Qualitest_PET/30001Head_F18-FDG-Hirn_Raw_Data
for f in *dcm; do nm_extract -i $f -o ../../../extracted; done
cd ../../..
stir_math extracted/umap.hv dicom/9_Head_MRAC_UTE_UMAP/MR.1.3.12.2.1107.5.2.38.51008.202309201458559904611155
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
