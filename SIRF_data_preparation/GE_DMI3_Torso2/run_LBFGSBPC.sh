datasrc=/mnt/share/petric/wip/petric2/orgdata
export PETRIC_SRCDIR=data
export PETRIC_OUTDIR=output
dataset=GE_DMI3_Torso2
template_dataset=GE_DMI3_Torso
noise_sf=$(python -c "from SIRF_data_preparation.dataset_settings import preferred_scaling as s; print(s['$dataset'], end='')")
sf=1
fullcounts_DIR=/mnt/share/petric/1/$template_dataset
bash -vx SIRF_data_preparation/run_bootstrap_OSEM.sh $dataset ${noise_sf} 1 $fullcounts_DIR
# python -m SIRF_data_preparation.create_initial_images data/$dataset
rm -rf data/${dataset}
mv output/${dataset}_${noise_sf}_1 data/${dataset}

cp -rp "${fullcounts_DIR}/"PETRIC data/${dataset}/
rm data/${dataset}/PETRIC/reference*

cp $PETRIC_SRCDIR/${template_dataset}/penalisation_factor.txt data/${dataset}/
python -m SIRF_data_preparation.run_LBFGSBPC --penalisation_factor_multiplier=$sf --outreldir=LBFGSBPC${sf} --initial_FWHM=5 --interval=20 --updates=80 ${dataset}
python -m SIRF_data_preparation.run_LBFGSBPC --penalisation_factor_multiplier=$sf --outreldir=LBFGSBPC${sf}_cont1 --initial_image=output/${dataset}/LBFGSBPC${sf}/iter_final.hv --interval=2 --updates=80 ${dataset}
python -m SIRF_data_preparation.plot_iterations --dataset=${dataset} --algo_name=LBFGSBPC1 --continuation_suffix=_cont1

pushd data/${dataset}
rm -rf *ahv *txt orgkappa PETRIC/*ahv
popd
cp output/${dataset}/LBFGSBPC${sf}/penalisation_factor.txt data/${dataset}

ref_image="data/${dataset}/PETRIC/reference_image.hv"
stir_math "$ref_image" output/${dataset}/LBFGSBPC${sf}_cont1/iter_final.hv

# verify
python -m SIRF_data_preparation.run_LBFGSBPC --penalisation_factor_multiplier=1 --outreldir=LBFGSBPC_final --initial_image="$ref_image" --interval=1 --updates=10 ${dataset}
compare_image output/${dataset}/LBFGSBPC_final/iter_final.hv "$ref_image"

python -m SIRF_data_preparation.data_QC --dataset=${dataset}

pushd data
mv ${dataset} /mnt/share-public/petric/2/
ln -s /mnt/share-public/petric/2/${dataset}
popd
