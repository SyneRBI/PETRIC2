#!/usr/bin/env python
"""Generate new noise realisation based on sinogram bootstrapping and reconstructs new OSEM image

Usage:
  noise_bootstrap.py [--help | options] --dataset=<name>

Options:
  -h, --help
  --dataset=<name>             dataset name
  --srcdir=<name>              location of dataset (defaults to petric's SRCDIR / dataset)
  --scale_factor=<float>       multiplicative factor to multiply the prompts with, before
                               generating new Poisson data [default: 1]
  --outname=<name>             name for new dataset (defaults to {dataset_name}_{scale_factor})

"""
# Copyright 2025 University College London
# Licence: Apache-2.0
__version__ = '0.1.0'

import os

import numpy as np
from docopt import docopt

import sirf.STIR as STIR
import SIRF_data_preparation.create_initial_images
from petric import OUTDIR, Dataset, get_data
from SIRF_data_preparation.data_utilities import the_data_path

STIR.AcquisitionData.set_storage_scheme('memory')


def bootstrap(input: STIR.AcquisitionData, scale_factor: float = 1) -> STIR.AcquisitionData:
    noisy_array = np.random.poisson(input.as_array() * scale_factor).astype('float64')
    noisy_data = input.clone()
    noisy_data.fill(noisy_array)
    return noisy_data


def run(outdir, dataset: Dataset, scale_factor: float = 1):
    os.makedirs(outdir, exist_ok=True)
    acquired_data = bootstrap(dataset.acquired_data, scale_factor)
    additive_term = dataset.additive_term * scale_factor
    acquired_data.write(os.path.join(outdir, "prompts.hs"))
    additive_term.write(os.path.join(outdir, "additive_term.hs"))
    dataset.mult_factors.write(os.path.join(outdir, "mult_factors.hs"))
    SIRF_data_preparation.create_initial_images.run(outdir, acquired_data, additive_term, dataset.mult_factors,
                                                    dataset.OSEM_image)


def main(argv=None):
    args = docopt(__doc__, argv=argv, version=__version__)
    dataset = args['--dataset']
    srcdir = args['--srcdir']
    outname = args['--outname']
    scale_factor = float(args['--scale_factor'])
    if outname is None:
        outname = f"{dataset}_{scale_factor}"

    if srcdir is None:
        srcdir = the_data_path(dataset)
        # settings = get_settings(dataset)

    outdir = OUTDIR / outname
    print(f"Output in {outdir}")

    dataset = get_data(srcdir=srcdir)
    run(outdir, dataset, scale_factor)


if __name__ == '__main__':
    main()
