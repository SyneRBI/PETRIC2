#!/usr/bin/env python
r"""
Preliminary file to check evolution of metrics as well as pass_index

Usage:
  plot_iterations [options]

Options:
  -h, --help
  -h, --help
  --dataset=<name>    dataset name
  --algo_name=<a>    name of algorithm/subfolder with iter*.hv
"""
# Copyright 2024-2025 University College London
# Licence: Apache-2.0
__version__ = '0.5.0'

# %%
# %load_ext autoreload
# %autoreload 2
# %%
from pathlib import Path

import matplotlib.pyplot as plt
import numpy
from docopt import docopt

import sirf.STIR as STIR
from petric import OUTDIR, SRCDIR, QualityMetrics, get_data
from SIRF_data_preparation import data_QC
from SIRF_data_preparation.data_utilities import the_data_path
from SIRF_data_preparation.dataset_settings import get_settings
from SIRF_data_preparation.evaluation_utilities import get_metrics, plot_metrics, read_objectives

# %%
if not all((SRCDIR.is_dir(), OUTDIR.is_dir())):
    PETRICDIR = Path('~/devel/PETRIC2').expanduser()
    OUTDIR = PETRICDIR / 'output'
STIR.AcquisitionData.set_storage_scheme('memory')
STIR.set_verbosity(0)
# %%
if __name__ == '__main__':
    args = docopt(__doc__, version=__version__)
    scanID = args['--dataset']
    algoname = args['--algo_name']
else:
    algoname = 'LBFGSBPC0.5'
    # scanID = 'Siemens_Vision600_thorax'
    # scanID = 'NeuroLF_Hoffman_Dataset'
    scanID = 'Siemens_mMR_NEMA_IQ'
    # scanID = 'Mediso_NEMA_IQ'
    # scanID = 'Siemens_Vision600_Hoffman'
    # scanID = 'NeuroLF_Esser_Dataset'
    # scanID = 'Siemens_Vision600_ZrNEMAIQ'
    # scanID = 'GE_D690_NEMA_IQ'
# %%
srcdir = the_data_path(scanID)
outdir = OUTDIR / scanID
OSEMdir = outdir / 'OSEM'
datadir = outdir / algoname
# we will check for images obtained after restarting BSREM (with new settings)
datadir1 = outdir / (algoname+'_cont')
# datadir = Path('/opt/runner/logs/2/Casper/BSREM/') / scanID

settings = get_settings(scanID)
slices = settings.slices
cmax = settings.vmax
# %%
data = get_data(srcdir=srcdir, outdir=None, read_sinos=False)
# %%
if data.reference_image is not None:
    reference_image = data.reference_image
elif datadir1.is_dir():
    reference_image = STIR.ImageData(str(datadir1 / 'iter_final.hv'))
else:
    reference_image = STIR.ImageData(str(datadir / 'iter_final.hv'))
# OSEM_image = STIR.ImageData(str(datadir / 'iter_0000.hv'))
OSEM_image = data.OSEM_image
# image2=STIR.ImageData(datadir+'iter_14000.hv')
# %%
image2 = OSEM_image
diff = image2 - reference_image
print("relative l1-norm diff final-OSEM:", diff.abs().max() / reference_image.max())
data_QC.plot_image(diff, **slices, vmin=-cmax / 100, vmax=cmax / 100)
# %%
objs = read_objectives(datadir)
if datadir1.is_dir():
    objs0 = objs.copy()
    objs1 = read_objectives(datadir1)
    tmp = objs1.copy()
    tmp[:, 0] += objs[-1, 0]
    objs = numpy.concatenate((objs, tmp))
fig = plt.figure()
plt.plot(objs[2:, 0], objs[2:, 1])
# %%
fig.savefig(outdir / f'{scanID}_{algoname}_objectives.png')
# %% plot last 50 values
# fig = plt.figure()
# plt.plot(objs[50:, 0], objs[50:, 1])
# fig.savefig(outdir / f'{scanID}_{algoname}_objectives_last.png')

# %%
qm = QualityMetrics(reference_image, data.whole_object_mask, data.background_mask, tb_summary_writer=None,
                    voi_mask_dict=data.voi_masks)
# %% get update ("iteration") numbers from objective functions
last_iteration = int(objs[-1, 0] + .5)
# find interval(don't use last value, as that interval can be smaller)
iteration_interval = int(objs[-2, 0] - objs[-3, 0] + .5)
if datadir1.is_dir():
    last_iteration = int(objs0[-1, 0] + .5)
    iteration_interval = int(objs0[-1, 0] - objs0[-2, 0] + .5) * 2
# %%
iters = range(0, last_iteration, iteration_interval)
print('GETMETRICS')
m = get_metrics(qm, iters, srcdir=datadir)
print('DONE')
# %%
if False:
    OSEMobjs = read_objectives(OSEMdir)
    OSEMiters = OSEMobjs[:, 0].astype(int)
    OSEMm = get_metrics(qm, OSEMiters, srcdir=OSEMdir)
# %%
fig = plt.figure()
plot_metrics(iters, m, qm.keys(), f'_{algoname}')
# plot_metrics(OSEMiters, OSEMm, qm.keys(), '_OSEM')
# [ax.set_xlim(0, 400) for ax in fig.axes]
# %%
fig.savefig(outdir / f'{scanID}_metrics_{algoname}_fullrange.png')
# %%
fig = plt.figure()
plot_metrics(iters, m, qm.keys(), f'_{algoname}')
fig.axes[0].set_ylim(0, .04)
fig.axes[1].set_ylim(0, .02)
fig.savefig(outdir / f'{scanID}_metrics_{algoname}.png')
# %%
m1 = None
if datadir1.is_dir():
    last_iteration1 = int(objs1[-1, 0] + .5)
    iteration_interval1 = int(objs1[-1, 0] - objs1[-2, 0] + .5) * 2
    iters1 = range(0, last_iteration1, iteration_interval1)
    m1 = get_metrics(qm, iters1, srcdir=datadir1)
# %%
if m1 is not None:
    fig = plt.figure()
    plot_metrics(iters, m, qm.keys(), '_{algoname}')
    plot_metrics(objs0[-1, 0] + iters1, m1, qm.keys(), '_{algoname}_cont')
    fig.axes[0].set_ylim(0, .04)
    fig.axes[1].set_ylim(0, .02)
    fig.savefig(outdir / f'{scanID}_metrics_{algoname}_cont.png')

# %%
try:
    idx = QualityMetrics.pass_index(m, numpy.array([.01, .01] + [.005 for i in range(len(data.voi_masks))]),
                                    max(10 // iteration_interval, 2))
    iter = iters[idx]
    print('pass index: ', iter)
except BaseException:
    print('Not yet passed, using last')
    iter = iters[-1]

image = STIR.ImageData(str(datadir / f"iter_{iter:04d}.hv"))
plt.figure()
data_QC.plot_image(image, **slices, vmax=cmax)
plt.savefig(outdir / f'{scanID}_{algoname}_{iter}.png')

plt.figure()
data_QC.plot_image(image - data.OSEM_image, **slices, vmin=-cmax / 50, vmax=cmax / 50)
plt.savefig(outdir / f'{scanID}_OSEM_diff_image_{algoname}_{iter}.png')
plt.figure()
data_QC.plot_image(image - reference_image, **slices, vmin=-cmax / 100, vmax=cmax / 100)
plt.savefig(outdir / f'{scanID}_ref_diff_image_{algoname}_{iter}.png')

# %%
