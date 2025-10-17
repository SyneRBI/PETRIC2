"""Basic QC plots
Reads data and makes various plots (saved as .png),
and computes VOI values (saved as .csv)

Usage:
  data_QC.py [options]

Options:
  -h, --help
  --dataset=<name>       dataset name. if set, it is used to override default slices
  --srcdir=<path>        pathname. Will default to current directory unless dataset is set
  --VOIdir=<VOIpath>     pathname. Will default to current directory/PETRIC unless dataset is set
  --skip_sino_profiles   do not plot the sinogram profiles (and skip checks)
  --skip_VOI_plots       do not plot the VOI images (and skip checks)
  --transverse_slice=<i>  idx [default: -1]
  --coronal_slice=<c>    idx [default: -1]
  --sagittal_slice=<s>   idx [default: -1]

Note that a slice index of -1 one means to use the dataset settings, and if those do not exist,
use the middle of image.
"""
# Copyright 2024-2025 University College London
# Licence: Apache-2.0
__version__ = '0.5.0'

import csv
import os
import os.path
from ast import literal_eval
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from docopt import docopt
from scipy import ndimage

import sirf.STIR as STIR
from SIRF_data_preparation.data_utilities import the_data_path
from SIRF_data_preparation.dataset_settings import get_settings

STIR.AcquisitionData.set_storage_scheme('memory')


def check_values_non_negative(arr: npt.NDArray[np.float32], desc: str):
    min = np.min(arr)
    max = np.max(arr)
    if np.isnan(min) or min < 0:
        raise ValueError(f"{desc}: minimum should be non-negative but is {min} (max={max})")
    if not np.isfinite(max):
        raise ValueError(f"{desc}: maximum should be finite")


def plot_sinogram_profile(prompts, background, sumaxis=(0, 1), select=0, srcdir='./'):
    """
    Plot a profile through sirf.STIR.AcquisitionData

    sumaxis: axes to sum over (passed to numpy.sum(..., axis))
    select: element to select after summing
    """
    # we will average over all sinograms to reduce noise
    plt.figure()
    ax = plt.subplot(111)
    plt.plot(np.sum(prompts.as_array(), axis=sumaxis)[select, :], label='prompts')
    plt.plot(np.sum(background.as_array(), axis=sumaxis)[select, :], label='background')
    ax.legend()
    plt.savefig(os.path.join(srcdir, 'prompts_background_profiles.png'))


def plot_image(image, save_name=None, transverse_slice=-1, coronal_slice=-1, sagittal_slice=-1, vmin=0, vmax=None,
               alpha=None, **kwargs):
    """
    Plot transverse/coronal/sagital slices through sirf.STIR.ImageData
    """
    if transverse_slice < 0:
        transverse_slice = image.dimensions()[0] // 2
    if coronal_slice < 0:
        coronal_slice = image.dimensions()[1] // 2
    if sagittal_slice < 0:
        sagittal_slice = image.dimensions()[2] // 2
    arr = image.as_array()
    if vmax is None:
        vmax = np.percentile(arr, 99.995)

    alpha_trans = None
    alpha_cor = None
    alpha_sag = None
    if alpha is not None:
        alpha_arr = alpha.as_array()
        alpha_trans = alpha_arr[transverse_slice, :, :]
        alpha_cor = alpha_arr[:, coronal_slice, :]
        alpha_sag = alpha_arr[:, :, sagittal_slice]

    ax = plt.subplot(131)
    plt.imshow(arr[transverse_slice, :, :], vmin=vmin, vmax=vmax, alpha=alpha_trans, **kwargs)
    ax.set_title(f"T={transverse_slice}")
    ax = plt.subplot(132)
    plt.imshow(arr[:, coronal_slice, :], vmin=vmin, vmax=vmax, alpha=alpha_cor, **kwargs)
    ax.set_title(f"C={coronal_slice}")
    ax = plt.subplot(133)
    plt.imshow(arr[:, :, sagittal_slice], vmin=vmin, vmax=vmax, alpha=alpha_sag, **kwargs)
    ax.set_title(f"S={sagittal_slice}")
    plt.colorbar(shrink=.6)
    if save_name is not None:
        plt.savefig(save_name + '_slices.png')
        plt.suptitle(os.path.basename(save_name))


def plot_image_if_exists(prefix, **kwargs):
    if os.path.isfile(prefix + '.hv'):
        im = STIR.ImageData(prefix + '.hv')
        plt.figure()
        plot_image(im, prefix, **kwargs)
        return im
    else:
        print(f"Image {prefix}.hv does not exist")
        return None


def check_and_plot_image_if_exists(prefix, **kwargs):
    im = plot_image_if_exists(prefix, **kwargs)
    if im is not None:
        check_values_non_negative(im.as_array(), prefix)
    return im


def VOI_mean(image, VOI):
    return float((image * VOI).sum() / VOI.sum())


def VOI_stddev(image, VOI):
    m = VOI_mean(image, VOI)
    d = image - m
    return float(np.sqrt((d * d * VOI).sum() / VOI.sum()))


def VOI_checks(allVOInames, OSEM_image=None, reference_image=None, VOIdir=None, outdir=None, skip_VOI_plots=False, **kwargs):
    """Save VOI images, mean and stddev values

    outdir defaults to VOIdir
    """
    if len(allVOInames) == 0:
        return
    if outdir is None:
        outdir = VOIdir
    OSEM_VOI_mean_values = []
    OSEM_VOI_stddev_values = []
    ref_VOI_mean_values = []
    ref_VOI_stddev_values = []
    allVOIs = None
    VOIkwargs = kwargs.copy()
    VOIkwargs['vmax'] = 1
    VOIkwargs['vmin'] = 0
    for VOIname in allVOInames:
        prefix = os.path.join(outdir, VOIname)
        filename = os.path.join(VOIdir, VOIname + '.hv')
        if not os.path.isfile(filename):
            print(f"VOI {VOIname} does not exist")
            continue
        VOI = STIR.ImageData(filename)
        VOI_arr = VOI.as_array()
        if not skip_VOI_plots:
            check_values_non_negative(VOI_arr, VOIname)
            COM = np.rint(ndimage.center_of_mass(VOI_arr))
            num_voxels = VOI_arr.sum()
            print(f"VOI: {VOIname}: COM (in indices): {COM} voxels {num_voxels} = {num_voxels * np.prod(VOI.spacing)} mm^3")
            plt.figure()
            plot_image(VOI, save_name=prefix, vmin=0, vmax=1, transverse_slice=int(COM[0]), coronal_slice=int(COM[1]),
                       sagittal_slice=int(COM[2]))
        if OSEM_image is not None and not skip_VOI_plots:
            plt.figure()
            plot_image(OSEM_image, alpha=(VOI+.5) / 1.5, save_name=prefix + "_and_OSEM", transverse_slice=int(COM[0]),
                       coronal_slice=int(COM[1]), sagittal_slice=int(COM[2]))

            # construct transparency image
            if VOIname == 'VOI_whole_object':
                VOI /= 2
            if allVOIs is None:
                allVOIs = VOI.clone()
            else:
                allVOIs += VOI

        if OSEM_image is not None:
            OSEM_VOI_mean_values.append(VOI_mean(OSEM_image, VOI))
            OSEM_VOI_stddev_values.append(VOI_stddev(OSEM_image, VOI))

        if reference_image:
            ref_VOI_mean_values.append(VOI_mean(reference_image, VOI))
            ref_VOI_stddev_values.append(VOI_stddev(reference_image, VOI))

    if OSEM_image is not None and not skip_VOI_plots:
        allVOIs /= allVOIs.max()
        plt.figure()
        plot_image(OSEM_image, alpha=allVOIs, save_name=os.path.join(outdir, "OSEM_image_and_VOIs"), **kwargs)

    # unformatted print of VOI values for now
    print(allVOInames)
    print(OSEM_VOI_mean_values)
    print(OSEM_VOI_stddev_values)
    print(ref_VOI_mean_values)
    print(ref_VOI_stddev_values)
    if len(allVOInames) > 0:
        with open(os.path.join(outdir, 'VOI_labels.csv'), 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows([allVOInames])
    if len(OSEM_VOI_mean_values) > 0:
        with open(os.path.join(outdir, 'OSEM_VOI_means.csv'), 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows([OSEM_VOI_mean_values])
        with open(os.path.join(outdir, 'OSEM_VOI_stddevs.csv'), 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows([OSEM_VOI_stddev_values])
    if len(ref_VOI_mean_values) > 0:
        with open(os.path.join(outdir, 'ref_VOI_means.csv'), 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows([ref_VOI_mean_values])
        with open(os.path.join(outdir, 'ref_VOI_stddevs.csv'), 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows([ref_VOI_stddev_values])


def main(argv=None):
    args = docopt(__doc__, argv=argv, version=__version__)
    dataset = args['--dataset']
    srcdir = args['--srcdir']
    VOIdir = args['--VOIdir']
    skip_sino_profiles = args['--skip_sino_profiles']
    skip_VOI_plots = args['--skip_VOI_plots']
    slices = {}
    slices["transverse_slice"] = literal_eval(args['--transverse_slice'])
    slices["coronal_slice"] = literal_eval(args['--coronal_slice'])
    slices["sagittal_slice"] = literal_eval(args['--sagittal_slice'])

    if (dataset):
        if srcdir is None:
            srcdir = the_data_path(dataset)
        settings = get_settings(dataset)
        for key in slices.keys():
            if slices[key] == -1 and key in settings.slices:
                slices[key] = settings.slices[key]
        if VOIdir is None:
            VOIdir = os.path.join(the_data_path(dataset), 'PETRIC')
    else:
        if srcdir is None:
            srcdir = os.getcwd()
        if VOIdir is None:
            VOIdir = os.path.join(srcdir, 'PETRIC')

    if not skip_sino_profiles:
        acquired_data = STIR.AcquisitionData(os.path.join(srcdir, 'prompts.hs'))
        additive_term = STIR.AcquisitionData(os.path.join(srcdir, 'additive_term.hs'))
        mult_factors = STIR.AcquisitionData(os.path.join(srcdir, 'mult_factors.hs'))
        background = additive_term * mult_factors
        plot_sinogram_profile(acquired_data, background, srcdir=srcdir)
        check_values_non_negative(acquired_data.as_array(), "prompts")
        check_values_non_negative(additive_term.as_array(), "additive_term")
        check_values_non_negative(mult_factors.as_array(), "mult_factors")
        check_values_non_negative(background.as_array(), "background")

    OSEM_image = check_and_plot_image_if_exists(os.path.join(srcdir, 'OSEM_image'), **slices)
    check_and_plot_image_if_exists(os.path.join(srcdir, 'kappa'), **slices)
    reference_image = check_and_plot_image_if_exists(os.path.join(srcdir, 'PETRIC/reference_image'), **slices)

    allVOInames = [os.path.basename(str(voi)[:-3]) for voi in Path(VOIdir).glob("VOI_*.hv")]
    VOIoutdir = os.path.join(srcdir, 'PETRIC')
    os.makedirs(VOIoutdir, exist_ok=True)
    VOI_checks(allVOInames, OSEM_image, reference_image, VOIdir=VOIdir, outdir=VOIoutdir, skip_VOI_plots=skip_VOI_plots, **slices)
    plt.show()


if __name__ == '__main__':
    main()
