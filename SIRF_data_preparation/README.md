# Functions/classes for PETRIC2

## Utility functions to prepare data for the Challenge

Participants should never have to use these (unless you want to create your own dataset).

- `create_initial_images.py`: functions+script to run OSEM and compute the "kappa" image from existing data
- `data_QC.py`: generates plots for QC
- `plot_iterations.py`: plot objective functions/metrics after a run (needs editing before running)
- `run_BSREM.py`, `run_LBFGSBPC.py` and `run_OSEM.py`: scripts to run these algorithms for a dataset
- `run_bootstrap_OSEM.sh`: script to generate a new data-set using (sinogram) bootstrapping
- `compute_objective_value.py`: compute objective values for multiple images for one dataset
- `run_beta_search.py`: script to find a suitable penalisation factor for a new data-set
  - uses `MaGeZ` (the winner of the first PETRIC) [with some zerocopy tweaks](https://github.com/SyneRBI/SIRF-Contribs/pull/28)

## Helpers

- `data_utilities.py`: functions to use sirf.STIR to output prompts/mult_factors and additive_term
  and handle Siemens data
- `evaluation_utilities.py`: reading/plotting helpers for values of the objective function and metrics
- `PET_plot_functions.py`: plotting helpers
- `dataset_settings.py`: settings for display of good slices, subsets etc
- `create_Hoffman_VOIs.py`: create VOIs registered to the OSEM image for a dataset

## Sub-folders per data-set

These contain files specific to the data-set, e.g. for downloading, VOI conversion, settings used for recon, etc.
Warning: this will be messy, and might be specific to whoever prepared this data-set. For instance,
for the Siemens mMR NEMA IQ data (on Zenodo):
- `download_Siemens_mMR_NEMA_IQ.py`: download and extract
- `prepare_mMR_NEMA_IQ_data.py`: prepare the data (prompts etc)
- `BSREM_*.py`: functions with specific settings for a particular data-set

# Steps to follow to prepare data
If starting from Siemens mMR list-mode data and letting SIRF take care of scatter etc, check for instance [steps for Siemens mMR ACR](Siemens_mMR_ACR/README.md). If pre-prepared data are given, check that naming of all files is correct. KT normally puts all data
in `~/devel/PETRIC2/data/<datasetname>` with `datasetname` following convention of `scanner_phantom-name` as others (instructions below and indeed some scripts might assume this location). Change working directory to where data sits and add PETRIC2 to your python-path, and go to correct directory, e.g.
```
PYTHONPATH=~/devel/PETRIC2:$PYTHONPATH`
cd ~/devel/PETRIC2
```
Install extra software if you don't have it yet:
```
conda install scikit-image
pip install git+https://github.com/TomographicImaging/Hackathon-000-Stochastic-QualityMetrics
```
*Warning*: some of the scripts use `stir_math`, which is a STIR utility, for copying of images and thresholding.
If you don't have that in your image, you could either install it (in principle, `conda -c conda_forge install stir` should work),
or create a Python equivalent.

1. For existing PETRIC data, `run_bootstrap_OSEM.sh` to reduce count level
2. Run initial [data_QC.py](data_QC.py)
   ```
   python -m SIRF_data_preparation.data_QC --dataset <datasetname>
   ```
3. Run [create_initial_images.py](create_initial_images.py).
   ```
   python -m SIRF_data_preparation.create_initial_images data/<datasetname>
   ```
   Optionally add argument `--template_image=<some_image>`, this defaults to `PETRIC/VOI_whole_object.hv`.
   (If you need to create VOIs yourself, you can use `None` or the vendor image).
4. Edit `OSEM_image.hv` to add modality, radionuclide and duration info which got lost (copy from `prompts.hs`)
5. Edit [dataset_settings.py](dataset_settings.py) for subsets (used by our BSREM reference reconstructions only, *not* by participants), `PETRIC1_clims` for hand-tuned colour-scale max, and `preferred_scaling` for the scale factor used in the bootstrapping.
6. If not PETRIC1 data, edit [petric.py](../petric.py) for slices to use for creating figures (`DATA_SLICES`). Note that `data_QC` outputs centre-of-mass of the VOIs, which can be helpful for this.
7. If not available yet, make VOIs, e.g.
   ```
   python -m SIRF_data_preparation.create_Hoffman_VOIs --dataset=<datasetname>
   ```
8. Run [data_QC.py](data_QC.py) which should now make more plots. Check VOI alignment etc.
   ```
   python -m SIRF_data_preparation.data_QC --dataset=<datasetname>
   ```
9. Get penalisation factor by comparing to a dataset from the ***same*** scanner as a starting point, e.g.
   ```
   python -m SIRF_data_preparation.get_penalisation_factor --dataset=NeuroLF_Esser_Dataset --ref_dataset=NeuroLF_Hoffman_Dataset -w
   ```
10. `python -m SIRF_data_preparation.run_OSEM <datasetname>`
11. Run LBFGSBPC (with restart) to generate reference solution. You probably want to monitor how these images look like (see next bullet). For instance, if you want to be able to run different penalty factors:
    ```sh
    sf=<penalty_scale_factor_wrt_PETRIC1>
    dataset=<datasetname>
    python -m SIRF_data_preparation.run_LBFGSBPC --penalisation_factor_multiplier=$sf --outreldir=LBFGSBPC${sf}  --initial_FWHM=5  --interval=20 --updates=100 ${dataset}
    python -m SIRF_data_preparation.run_LBFGSBPC --penalisation_factor_multiplier=$sf --outreldir=LBFGSBPC${sf}_cont1  --initial_image=output/${dataset}/LBFGSBPC${sf}/iter_final.hv   --interval=1 --updates=200 ${dataset}
    ```
12. Run [plot_iterations.py](plot_iterations.py) to check results. (If running interactively, set `manual_settings=True` and adjust the `<datasetname>`).
13. Copy the  ` iter_final` to `data/<datasetname>/PETRIC/reference_image`, e.g.
    ```
    stir_math data/<datasetname>/PETRIC/reference_image.hv output/<datasetname>/LBFGSBPC${sf}_cont1/iter_final.hv
    ```
14. `cd data/<datasetname>; rm -rf *ahv PETRIC/*ahv output info.txt warnings.txt`, check its `README.md` etc
15. Transfer to web-server

For most training data sets, there should be `run_LBFGSBPC.sh` in `SIRF_data_preparation/<datasetname>` with (most of) these steps.
