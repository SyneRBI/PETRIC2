# STFC hard-wired location
datasrc=/mnt/share-public/petric
export PETRIC_SRCDIR=data
export PETRIC_OUTDIR=output
dataset=Mediso_NEMA_IQ
noise_sf=0.01
sf=0.06

bash -vx SIRF_data_preparation/run_bootstrap_OSEM.sh $dataset ${noise_sf} 1 $datasrc/1/$dataset
# python -m SIRF_data_preparation.create_initial_images data/$dataset
rm -rf data/${dataset}
mv output/${dataset}_${noise_sf}_1 data/${dataset}

cp -rp "${datasrc}/1/$dataset/PETRIC" data/${dataset}/
rm data/${dataset}/PETRIC/reference*
# threshold any (very small) negatives in OSEM
pushd data/${dataset}
mkdir tmp && mv OSEM_image.*v tmp && stir_math --min-threshold 0 --including-first OSEM_image tmp/OSEM_image.hv && rm -rf tmp
popd

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
