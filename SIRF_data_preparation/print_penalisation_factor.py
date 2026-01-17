#!/usr/bin/env python
r"""Print penalisation factor for one dataset

Usage:
  print_penalisation_factor [--help | options]

Options:
  -h, --help
  --dataset=<name>                 dataset name (required)
"""

# Copyright 2024, 2026 University College London
# Licence: Apache-2.0

from pathlib import Path

from docopt import docopt

# %% imports
from petric import get_data
from SIRF_data_preparation.data_utilities import the_data_path

# %%
__version__ = "0.1.0"

args = docopt(__doc__, argv=None, version=__version__)

dataset = args["--dataset"]
if dataset is None:
    print("Need to set the --dataset arguments")
    exit(1)

datadir = Path(the_data_path(dataset))
data = get_data(datadir, outdir=None, read_sinos=False)
penalisation_factor = data.prior.get_penalisation_factor()
print(penalisation_factor)
