#! /bin/sh

. /opt/SIRF-SuperBuild/INSTALL/bin/env_sirf.sh


# for beta in 1 10 100 1000; do
for beta in 10; do
  python run_LBFGSBPC.py Siemens_Vision600_ZrNEMAIQ --updates 4 --interval 2 --beta $beta
done