# %%
# %load_ext autoreload
# %autoreload 2
# %%
import os

from SIRF_data_preparation.data_utilities import prepare_challenge_STIR_data, the_data_path, the_orgdata_path

# %% set paths filenames
scanID = 'NeuroLF_Esser2'
orgdata_path = the_orgdata_path(scanID)
data_path = the_data_path(scanID)
fullcounts_data_path = os.path.join(orgdata_path, 'fullcounts')
intermediate_data_path = os.path.join(orgdata_path, 'processing')
os.makedirs(data_path, exist_ok=True)
os.makedirs(fullcounts_data_path, exist_ok=True)
os.makedirs(intermediate_data_path, exist_ok=True)
# %%
f_stir_norm = os.path.join(orgdata_path, 'Calibration', 'normalization.hs')
f_randoms = os.path.join(orgdata_path, 'list-mode', 'randoms.hs')
f_listmode = os.path.join(orgdata_path, 'list-mode', 'listmode_file.par')
f_attn_image = os.path.join(orgdata_path, 'AC', 'attenuation_map.hv')

# %% avoid https://github.com/UCL/STIR/issues/1680
cur_dir = os.getcwd()
os.chdir(os.path.join(orgdata_path, 'list-mode'))
f_listmode = 'listmode_file.par'

# %%
prepare_challenge_STIR_data(fullcounts_data_path, intermediate_data_path, f_listmode, f_attn_image, f_stir_norm,
                            f_template=f_randoms, f_randoms=f_randoms, scatter_min_max_scale=(1.2, 1.2))
