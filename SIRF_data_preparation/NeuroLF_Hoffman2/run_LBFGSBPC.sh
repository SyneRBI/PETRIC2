datasrc=/mnt/share/petric/wip/petric2/orgdata
export PETRIC_SRCDIR=data
export PETRIC_OUTDIR=output
dataset=NeuroLF_Hoffman2
noise_sf=$(python -c "from SIRF_data_preparation.dataset_settings import preferred_scaling as s; print(s['$dataset'], end='')")
sf=1

bash -vx SIRF_data_preparation/run_bootstrap_OSEM.sh $dataset ${noise_sf} 1 $datasrc/$dataset/fullcounts
# python -m SIRF_data_preparation.create_initial_images data/$dataset
rm -rf data/${dataset}
mv output/${dataset}_${noise_sf}_1 data/${dataset}

cp -rp "${datasrc}/$dataset/fullcounts/PETRIC/" data/${dataset}/
rm data/${dataset}/PETRIC/reference*
# threshold any (very small) negatives in OSEM
pushd data/${dataset}
mkdir tmp && mv OSEM_image.*v tmp && stir_math --min-threshold 0 --including-first OSEM_image tmp/OSEM_image.hv && rm -rf tmp
popd

cp $PETRIC_SRCDIR/NeuroLF_Hoffman_Dataset/penalisation_factor.txt data/${dataset}/
python -m SIRF_data_preparation.run_LBFGSBPC --penalisation_factor_multiplier=$sf --outreldir=LBFGSBPC${sf} --initial_FWHM=5 --interval=20 --updates=80 ${dataset}
python -m SIRF_data_preparation.run_LBFGSBPC --penalisation_factor_multiplier=$sf --outreldir=LBFGSBPC${sf}_cont1 --initial_image=output/${dataset}/LBFGSBPC${sf}/iter_final.hv --interval=2 --updates=80 ${dataset}

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
mv ${dataset} ${datasrc}/2/
ln -s ${datasrc}/2/${dataset}
popd
