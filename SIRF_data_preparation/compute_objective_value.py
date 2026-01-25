r"""Compute objective function values

Usage:
  compute_objective_value.py [--beta=<b>] <dataset> <image>... [--help]

Arguments:
  <dataset>    dataset name
  <image>      list of images

Options:
  --beta=<b>   scale factor to multiply default penalisation_factor [default: 1]

Output:
   None (prints filenames and values to stdout)
"""
# Copyright 2024 Rutherford Appleton Laboratory STFC
# Copyright 2024-2026 University College London
# Licence: Apache-2.0
__version__ = '1.0.0'

from typing import Iterable

from docopt import docopt

from petric import SRCDIR, STIR, Dataset, get_data
from sirf.contrib.partitioner import partitioner

STIR.AcquisitionData.set_storage_scheme('memory')


def create_obj_fun(data: Dataset, beta: float = 1) -> STIR.ObjectiveFunction:
    """Create an objective function, corresponding to the given data"""
    # We could construct this by hand here, but instead will just use `partitioner.data_partition`
    # with 1 subset, which will then do the work for us.
    num_subsets = 1
    _, _, obj_funs = partitioner.data_partition(data.acquired_data, data.additive_term, data.mult_factors, num_subsets,
                                                initial_image=data.OSEM_image)
    obj_fun = obj_funs[0]
    data.prior.set_penalisation_factor(data.prior.get_penalisation_factor() * beta)
    data.prior.set_up(data.OSEM_image)
    obj_fun.set_prior(data.prior)
    return obj_fun


def run(data: Dataset, image_filenames: Iterable[str], beta: float = 1) -> list[float]:
    obj_fun = create_obj_fun(data, beta)

    obj_values = []
    for image_filename in image_filenames:
        image = STIR.ImageData(image_filename)
        v = obj_fun(image)
        print(image_filename, v)
        obj_values.append(v)
    return obj_values


def main(argv=None):
    args = docopt(__doc__, argv=argv, version=__version__)
    scanID = args['<dataset>']
    image_filenames = args['<image>']
    beta = float(args['--beta'])

    data = get_data(srcdir=SRCDIR / scanID, outdir=None)
    # engine's messages are surpressed, except error messages, which go to stdout
    _ = STIR.MessageRedirector(None, None)

    run(data, image_filenames, beta)


if __name__ == '__main__':
    main()
