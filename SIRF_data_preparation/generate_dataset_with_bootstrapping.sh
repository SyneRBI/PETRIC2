#!/bin/bash
bash -vx SIRF_data_preparation/run_bootstrap_OSEM.sh $dataset ${noise_sf} 1 $fullcounts_DIR
rm -rf ${PETRIC_SRCDIR}/${dataset}
mv ${PETRIC_OUTDIR}/${dataset}_${noise_sf}_1 ${PETRIC_SRCDIR}/${dataset}

cp -rp "${fullcounts_DIR}/"PETRIC ${PETRIC_SRCDIR}/${dataset}/
rm ${PETRIC_SRCDIR}/${dataset}/PETRIC/reference*

cp $PETRIC_SRCDIR/${template_dataset}/penalisation_factor.txt ${PETRIC_SRCDIR}/${dataset}/
python -m SIRF_data_preparation.run_LBFGSBPC --penalisation_factor_multiplier=$sf --outreldir=LBFGSBPC${sf} --initial_FWHM=5 --interval=20 --updates=80 ${dataset}
python -m SIRF_data_preparation.run_LBFGSBPC --penalisation_factor_multiplier=$sf --outreldir=LBFGSBPC${sf}_cont1 --initial_image=${PETRIC_OUTDIR}/${dataset}/LBFGSBPC${sf}/iter_final.hv --interval=2 --updates=80 ${dataset}
python -m SIRF_data_preparation.plot_iterations --dataset=${dataset} --algo_name=LBFGSBPC1 --continuation_suffix=_cont1

pushd ${PETRIC_SRCDIR}/${dataset}
rm -rf *ahv *txt orgkappa PETRIC/*ahv
popd
cp ${PETRIC_OUTDIR}/${dataset}/LBFGSBPC${sf}/penalisation_factor.txt ${PETRIC_SRCDIR}/${dataset}

ref_image="${PETRIC_SRCDIR}/${dataset}/PETRIC/reference_image.hv"
stir_math "$ref_image" ${PETRIC_OUTDIR}/${dataset}/LBFGSBPC${sf}_cont1/iter_final.hv

python -m SIRF_data_preparation.data_QC --dataset=${dataset}

# verify
python -m SIRF_data_preparation.run_LBFGSBPC --penalisation_factor_multiplier=1 --outreldir=LBFGSBPC_final --initial_image="$ref_image" --interval=1 --updates=10 ${dataset}
compare_image ${PETRIC_OUTDIR}/${dataset}/LBFGSBPC_final/iter_final.hv "$ref_image"
