#! /bin/sh

. /opt/SIRF-SuperBuild/INSTALL/bin/env_sirf.sh
cd 
cd PETRIC2
phantom="Siemens_Vision600_ZrNEMAIQ"
for beta in 10 100 1000; do
# for beta in 1; do
  python run_LBFGSBPC.py $phantom --updates 400 --interval 100 --beta $beta > output_${phantom}_LBFGSBPC_beta_${beta}.log 2>&1
done