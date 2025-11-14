#! /bin/sh

. /opt/SIRF-SuperBuild/INSTALL/bin/env_sirf.sh
cd 
cd PETRIC2
# phantoms="Siemens_mMR_ACR GE_D690_NEMA_IQ Siemens_mMR_NEMA_IQ Siemens_Vision600_ZrNEMAIQ"
phantoms="Siemens_mMR_ACR"
for phantom in $phantoms; do
#  for beta in 1 10 100 1000; do
for beta in 1 ; do
  # python run_LBFGSBPC.py $phantom --updates 400 --interval 100 --beta $beta > output/output_${phantom}_LBFGSBPC_beta_${beta}.log 2>&1
  echo -n "Running MaGeZ for phantom $phantom with beta $beta ..."
  python run_MaGeZ.py $phantom --updates 400 --interval 100 --beta $beta > output/output_${phantom}_MaGeZ_beta_${beta}.log 2>&1
  echo " Done"
 done
done