#!/usr/bin/env python
"""
Run LBFGSBPC for PETRIC

Usage:
  run_LBFGSBPC.py <data_set> [--help | options]

Arguments:
  <data_set>     path to data files as well as prefix to use (e.g. Siemens_mMR_NEMA_IQ)
Options:
  --updates=<u>               number of updates to run [default: 500]
  --initial_image=<filename>  optional initial image, normally the OSEM_image from get_data.

  --interval=<i>              interval to save [default: 3]
  --outreldir=<relpath>       optional relative path to override
                              (defaults to 'LBFGSBPC' or 'LBFGSBPC_cont' if initial_image is set)
  --beta=<u>                  penalisation factor [default: 1]
"""
# Copyright 2024 Rutherford Appleton Laboratory STFC
# Copyright 2024-2025 University College London
# Licence: Apache-2.0
__version__ = '0.2.0'

import csv
import os
from pathlib import Path

import matplotlib.pyplot as plt
from docopt import docopt

import sirf.STIR as STIR
from petric import OUTDIR, SRCDIR, MetricsWithTimeout, get_data
from sirf.contrib.partitioner import partitioner
from SIRF_data_preparation import data_QC
from SIRF_data_preparation.dataset_settings import get_settings
from SIRF_data_preparation.preferred_scaling import preferred_scaling

import numpy
# from LBFGSBPC import LBFGSBPC
from PETRIC_MaGeZ.main import Submission as MaGeZ 
# %%

STIR.AcquisitionData.set_storage_scheme('memory')
_ = STIR.MessageRedirector('info.txt', 'warnings.txt', 'errors.txt')
STIR.set_verbosity(0)


# %%
args = docopt(__doc__, argv=None, version=__version__)
# logging.basicConfig(level=logging.INFO)

scanID = args['<data_set>']
num_updates = int(args['--updates'])
initial_image = args['--initial_image']
interval = int(args['--interval'])
outreldir = args['--outreldir']
_beta = args['--beta']
sfs = float(preferred_scaling[scanID])
betas = _beta.split(',')
# Override petric's default
# OUTDIR = Path("../output")

print(f"{SRCDIR}", SRCDIR.is_dir())
print(f"{OUTDIR}", OUTDIR.is_dir())

if not all((SRCDIR.is_dir(), OUTDIR.is_dir())):
    PETRICDIR = Path('~/workdir/PETRIC2').expanduser()
    SRCDIR = PETRICDIR / 'data'
    SRCDIR = Path("/data/wip/petric2")
    OUTDIR = PETRICDIR / 'output'
    # Override petric's default
    # OUTDIR = Path("/output")
    print(f"Adjusted SRCDIR to {SRCDIR}")

outdir = OUTDIR / scanID
srcdir = SRCDIR / scanID
# log.info("Finding files in %s", srcdir)
print (f"outdir {outdir}")
print (f"srcdir {srcdir}")

settings = get_settings(scanID)

print(settings)

data = get_data(srcdir=srcdir, outdir=outdir)
if initial_image is None:
    initial_image_name = "OSEM"
    initial_image = data.OSEM_image
    outdir = outdir / ("MaGeZ" if outreldir is None else outreldir)
else:
    initial_image_name = initial_image
    initial_image = STIR.ImageData(initial_image)
    outdir = outdir / ("MaGeZ_cont" if outreldir is None else outreldir)


from cil.optimisation.utilities import callbacks
class SaveNpyCallback(callbacks.Callback):
    def __init__(self, outdir, interval):
        self.outdir = outdir
        self.interval = interval

    def __call__(self, algorithm):
        if algorithm.iteration % self.interval == 0:
            iter_num = algorithm.iteration
            array = algorithm.get_output().asarray(copy=False)
            npy_path = self.outdir / f"MaGeZ_iter{iter_num:04d}.npy"
            numpy.save(npy_path, array)
            print(f"Saved numpy array to {npy_path}")
# create output directory if not there
os.makedirs(outdir, exist_ok=True)

petric1_beta = data.prior.get_penalisation_factor()

print("Original Penalisation factor:", petric1_beta, flush=True)

for beta in betas:

    b_outdir = outdir / beta
    os.makedirs(b_outdir, exist_ok=True)

    print("num_updates:", num_updates, flush=True)
    print("initial_image:", initial_image_name, flush=True)
    print("outdir:", b_outdir, flush=True)
    print("interval:", interval, flush=True)
    print("Penalisation factor:", data.prior.get_penalisation_factor(), flush=True)
    data.prior.set_penalisation_factor(float(beta) * petric1_beta)
    print("Rescaled penalisation factor:", data.prior.get_penalisation_factor(), flush=True)


    algo = MaGeZ(data, update_objective_interval=interval,)
    # %%
    

    cb = SaveNpyCallback(b_outdir, interval)
    algo.run(iterations=num_updates+1, callbacks=[cb, 
                                                callbacks.TextProgressCallback()])
    # %%

    algo.get_output().write(str(b_outdir / "MaGeZ.hv"))
    # %%
    writer = csv.writer((b_outdir / 'objectives.csv').open("w", buffering=1))
    writer.writerow(("iter", "objective"))
    for i,l in zip(algo.iterations, algo.loss):
        writer.writerow((i,l))

    # %%
    fig = plt.figure()
    data_QC.plot_image(algo.get_output(), **settings.slices)
    fig.savefig(b_outdir / "MaGeZ_slices.png")
    # plt.show()
    # %%
    print(algo.iterations)
    print(algo.loss)
    fig = plt.figure()
    plt.plot(algo.iterations, algo.loss)
    fig.savefig(outdir / "MaGeZ_objective.png")
