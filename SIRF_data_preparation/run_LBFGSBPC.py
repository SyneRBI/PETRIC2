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
"""
# Copyright 2024 Rutherford Appleton Laboratory STFC
# Copyright 2024-2025 University College London
# Licence: Apache-2.0
__version__ = '0.1.0'

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from docopt import docopt

import sirf.STIR as STIR
from petric import OUTDIR, SRCDIR, MetricsWithTimeout, get_data
from sirf.contrib.partitioner import partitioner
from SIRF_data_preparation import data_QC
from SIRF_data_preparation.dataset_settings import get_settings

import numpy
from sirf.contrib.LBFGSBPC.LBFGSBPC import LBFGSBPC
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

if not all((SRCDIR.is_dir(), OUTDIR.is_dir())):
    PETRICDIR = Path('~/devel/PETRIC2').expanduser()
    SRCDIR = PETRICDIR / 'data'
    OUTDIR = PETRICDIR / 'output'

outdir = OUTDIR / scanID
srcdir = SRCDIR / scanID
# log.info("Finding files in %s", srcdir)

settings = get_settings(scanID)

data = get_data(srcdir=srcdir, outdir=outdir)
if initial_image is None:
    initial_image_name = "OSEM"
    initial_image = data.OSEM_image
    outdir = outdir / ("LBFGSBPC" if outreldir is None else outreldir)
else:
    initial_image_name = initial_image
    initial_image = STIR.ImageData(initial_image)
    outdir = outdir / ("LBFGSBPC_cont" if outreldir is None else outreldir)

print("Penalisation factor:", data.prior.get_penalisation_factor())
print("num_updates:", num_updates)
print("initial_image:", initial_image_name)
print("outdir:", outdir)
print("interval:", interval)

num_subsets=1
_, _, obj_funs = partitioner.data_partition(data.acquired_data, data.additive_term, data.mult_factors,
                                                    num_subsets,
                                                    initial_image=data.OSEM_image)
obj_fun = obj_funs[0]
data.prior.set_up(data.OSEM_image)
# acq_model = acq_models[0]
obj_fun.set_prior(data.prior)

algo = LBFGSBPC(obj_fun, initial=initial_image, update_objective_interval=interval)
# %%
algo.run(iterations=num_updates)
# %%
algo.get_output().write(str(outdir / "LBFGSBPC.hv"))
# %%
csv = csv.writer((self.outdir / 'objectives.csv').open("w", buffering=1))
csv.writerow(("iter", "objective"))
for i,l in zip(algo.iterations, algo.loss):
    csv.writerow((i,l))

# %%
fig = plt.figure()
data_QC.plot_image(algo.get_output(), **settings.slices)
fig.savefig(outdir / "LBFGSBPC_slices.png")
# plt.show()
# %%
print(algo.iterations)
print(algo.loss)
fig = plt.figure()
plt.plot(algo.iterations, recon.loss)
fig.savefig(outdir / "LBFGSBPC_objective.png")
