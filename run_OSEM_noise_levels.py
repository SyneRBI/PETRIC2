"""Run OSEM with different noise levels for PETRIC

Usage:
  run_OSEM_noise_levels.py [--help | options]

Options:
  --updates=<u>  number of updates to run [default: 400]
"""
# Copyright 2024 Rutherford Appleton Laboratory STFC
# Copyright 2024 University College London
# Licence: Apache-2.0
__version__ = '0.2.0'
from pathlib import Path

import matplotlib.pyplot as plt
from docopt import docopt

import main_OSEM_no_gpu
from petric import OUTDIR, SRCDIR, MetricsWithTimeout, get_data_with_noise_level
from SIRF_data_preparation import data_QC
from SIRF_data_preparation.dataset_settings import get_settings

# %%
args = docopt(__doc__, argv=None, version=__version__)
# logging.basicConfig(level=logging.INFO)

num_updates = int(args['--updates'])

if not all((SRCDIR.is_dir(), OUTDIR.is_dir())):
    PETRICDIR = Path('~/devel/PETRIC').expanduser()
    SRCDIR = PETRICDIR / 'data'
    OUTDIR = PETRICDIR / 'output'

datasets = [
    'Siemens_mMR_NEMA_IQ', 'Siemens_mMR_NEMA_IQ_lowcounts', 'Siemens_mMR_ACR', 'NeuroLF_Hoffman_Dataset',
    'Mediso_NEMA_IQ', 'Siemens_Vision600_thorax', 'GE_DMI3_Torso', 'Siemens_Vision600_Hoffman',
    'NeuroLF_Esser_Dataset', 'Siemens_Vision600_ZrNEMAIQ', 'GE_D690_NEMA_IQ', 'Mediso_NEMA_IQ_lowcounts',
    'GE_DMI4_NEMA_IQ']
datasets = ['Siemens_mMR_NEMA_IQ', 'NeuroLF_Hoffman_Dataset', 'Siemens_Vision600_ZrNEMAIQ', 'Mediso_NEMA_IQ']

for scanID in datasets:
  print(f"--------------{scanID}----------")
  srcdir = SRCDIR / scanID
  # log.info("Finding files in %s", srcdir)

  settings = get_settings(scanID)

  for noise_level in [1,2]:
    outdir = OUTDIR / scanID / f"OSEM_nl_{noise_level}"

    data = get_data_with_noise_level(srcdir=srcdir, outdir=outdir, noise_level=noise_level)
    print("noise level:", noise_level)
    print("num_subsets:", settings.num_subsets)
    print("num_updates:", num_updates)
    # %%
    algo = main_OSEM_no_gpu.Submission(data, settings.num_subsets, update_objective_interval=20)
    algo.run(num_updates, callbacks=[MetricsWithTimeout(**settings.slices, seconds=5000, interval=20, outdir=outdir)])
    # %%
    #fig = plt.figure()
    #data_QC.plot_image(algo.get_output(), **settings.slices)
    #fig.savefig(outdir / "OSEM_slices.png")
  # plt.show()
