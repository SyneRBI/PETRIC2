dataset=Siemens_Vision600_Hoffman
# STFC hard-wired location
datasrc=/mnt/share-public/petric

pushd data/$dataset;mkdir orgkappa;mv kappa* orgkappa;popd
python -m SIRF_data_preparation.create_initial_images data/$dataset

sf=0.2;
python -m SIRF_data_preparation.run_LBFGSBPC --penalisation_factor_multiplier=$sf --outreldir=LBFGSBPC${sf} --initial_FWHM=5 --interval=20 --updates=80 ${dataset}
python -m SIRF_data_preparation.run_LBFGSBPC --penalisation_factor_multiplier=$sf --outreldir=LBFGSBPC${sf}_cont1 --initial_image=output/${dataset}/LBFGSBPC${sf}/iter_final.hv --interval=2 --updates=80 ${dataset}

stir_math data/${dataset}/PETRIC/reference_image.hv output/${dataset}/LBFGSBPC${sf}_cont1/iter_final.hv
pushd data/${dataset}
# threshold any (very small) negatives
mkdir tmp; mv OSEM_image.*v tmp;stir_math --min-threshold 0 --including-first OSEM_image tmp/OSEM_image.hv; rm -rf tmp
beta=$(cat ${datasrc}/1/${dataset}/penalisation_factor.txt)
rm -rf *ahv *txt orgkappa PETRIC/*ahv
echo "print($beta * $sf)"| python -q - > penalisation_factor.txt
popd
python -m SIRF_data_preparation.data_QC --dataset=${dataset}
pushd data
mv ${dataset} ${datasrc}/2/
ln -s ${datasrc}/2/${dataset}
popd
