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

  --initial_FWHM=<f>          optional FWHM of 3D Gaussian filter, [default: 0]
  --interval=<i>              interval to save [default: 3]
  --outreldir=<relpath>       optional relative path to override
                              (defaults to 'LBFGSBPC' or 'LBFGSBPC_cont' if initial_image is set)
  --penalisation_factor_multiplier=<f> factor to multiply the default penalisation factor with [default: 1]
                              (use with caution: You will likely want to specify outreldir)
"""
# Copyright 2024 Rutherford Appleton Laboratory STFC
# Copyright 2024-2025 University College London
# Licence: Apache-2.0
__version__ = '0.1.0'

import csv

import matplotlib.pyplot as plt
import stir  # stir Python interface # yapf: disable
from docopt import docopt

import sirf.STIR as STIR  # SIRF python interface to STIR # yapf: disable
from petric import OUTDIR, SRCDIR, get_data
from sirf.contrib.LBFGSBPC.LBFGSBPC import LBFGSBPC
from sirf.contrib.partitioner import partitioner
from SIRF_data_preparation import data_QC
from SIRF_data_preparation.dataset_settings import get_settings

# %%

STIR.AcquisitionData.set_storage_scheme('memory')
_ = STIR.MessageRedirector('info.txt', 'warnings.txt', 'errors.txt')
STIR.set_verbosity(0)


# %% STIR functions for functionality still missing in SIRF
# the sirf.STIR.RelativeDifferencePrior does not yet expose all functions available in STIR 6.3
# In particular, we need the diagonal of the Hessian of the prior.
# The following contains some ugly/unsafe work-arounds
def sirf_to_stir(image: STIR.ImageData) -> stir.FloatVoxelsOnCartesianGrid:
    r"""Convert sirf.STIR.ImageData to a stir object

    Warning: writes to tmp.* in current directory (could be done better)
    """
    image.write('tmp.hv')
    return stir.FloatVoxelsOnCartesianGrid.read_from_file('tmp.hv')


def stir_to_sirf(image: stir.FloatVoxelsOnCartesianGrid) -> STIR.ImageData:
    r"""Convert stir image to sirf.STIR.ImageData

    Warning: writes to tmp.* in current directory (could be done better)
    """
    image.write_to_file('tmp.hv')
    return STIR.ImageData('tmp.hv')


def construct_stir_RDP(sirf_prior: STIR.RelativeDifferencePrior, initial_image: STIR.ImageData):
    '''
    Construct a stir smoothed Relative Difference Prior (RDP), given input from a sirf.STIR one

    `initial_image` is used to determine a smoothing factor (epsilon).
    `kappa` is used to pass voxel-dependent weights.
    '''
    prior = stir.GibbsRelativeDifferencePenalty3DFloat()
    # need to make it differentiable
    prior.set_epsilon(sirf_prior.get_epsilon())
    prior.set_penalisation_factor(sirf_prior.get_penalisation_factor())
    prior.set_gamma(sirf_prior.get_gamma())
    if sirf_prior.get_kappa() is not None:
        prior.set_kappa_sptr(sirf_to_stir(sirf_prior.get_kappa()))
    prior.set_up(sirf_to_stir(initial_image))
    return prior


def construct_preconditioner(initial: STIR.ImageData, obj_fun: STIR.ObjectiveFunction,
                             sirf_prior: STIR.RelativeDifferencePrior) -> STIR.ImageData:
    r"""Construct a preconditioner for LBFGSB-PC

    Tsai's paper uses (-H.1). However, for the RDP, this does not work very well. We have better
    results when using (-H_loglikelihood.1 + diag(H_prior)).
    In addition, H.1 is sensitive to noise once data gets very noisy, so we'll use
    the "kappa" of the prior (see create_initial_images).
    WARNING: this latter modification is NOT a general strategy and we didn't test if it
    works better than H.1 or not.
    """
    stir_initial = sirf_to_stir(initial)
    # sirf_prior = obj_fun.get_prior() # returns object of type Prior, which isn't good enough
    stir_prior = construct_stir_RDP(sirf_prior, initial)
    diag = stir_initial.clone()
    stir_prior.compute_Hessian_diagonal(diag, stir_initial)
    diag = stir_to_sirf(diag)
    # sirf_prior.set_penalisation_factor(0)
    # ll_precon = obj_fun.multiply_with_Hessian(initial, initial.get_uniform_copy(1)) * -1
    # sirf_prior.set_penalisation_factor(stir_prior.get_penalisation_factor())
    ll_precon = sirf_prior.get_kappa().power(2)
    return ll_precon + diag


# %%
args = docopt(__doc__, argv=None, version=__version__)
# logging.basicConfig(level=logging.INFO)

scanID = args['<data_set>']
num_updates = int(args['--updates'])
initial_image = args['--initial_image']
interval = int(args['--interval'])
outreldir = args['--outreldir']
beta_factor = float(args['--penalisation_factor_multiplier'])
FWHM = float(args['--initial_FWHM'])
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

if FWHM > 0:
    filter = STIR.SeparableGaussianImageFilter()
    filter.set_fwhms((FWHM, FWHM, FWHM))
    filter.apply(initial_image)

org_beta = data.prior.get_penalisation_factor()
new_beta = org_beta * beta_factor
data.prior.set_penalisation_factor(new_beta)
outdir.mkdir(parents=True, exist_ok=True)
(outdir / "penalisation_factor.txt").write_text(str(new_beta))

print("Penalisation factor:", data.prior.get_penalisation_factor(), ' = ', org_beta, '*', beta_factor)
print("num_updates:", num_updates)
print("initial_image:", initial_image_name)
print("FWHM of Gaussian filter:", FWHM)
print("outdir:", outdir)
print("interval:", interval)

num_subsets = 1
initial = data.OSEM_image
_, _, obj_funs = partitioner.data_partition(data.acquired_data, data.additive_term, data.mult_factors, num_subsets,
                                            initial_image=initial)
obj_fun = obj_funs[0]
data.prior.set_up(initial)
# acq_model = acq_models[0]
obj_fun.set_prior(data.prior)

precond = construct_preconditioner(initial, obj_fun, data.prior)
algo = LBFGSBPC(obj_fun, initial=initial_image, update_objective_interval=interval,
                save_intermediate_results_path=str(outdir))
algo.set_preconditioner(precond)
# %%
algo.run(iterations=num_updates)
# %%
algo.get_output().write(str(outdir / "iter_final.hv"))
# %%
cvswriter = csv.writer((outdir / 'objectives.csv').open("w", buffering=1))
cvswriter.writerow(("iter", "objective"))
for i, l in zip(algo.iterations, algo.loss):
    cvswriter.writerow((i, l))

# %%
fig = plt.figure()
data_QC.plot_image(algo.get_output(), **settings.slices, vmax=settings.vmax)
fig.savefig(outdir / "LBFGSBPC_slices.png")
# plt.show()
# %%
print(algo.iterations)
print(algo.loss)
fig = plt.figure()
plt.plot(algo.iterations, algo.loss)
fig.savefig(outdir / "LBFGSBPC_objective.png")
