# %%
#%load_ext autoreload
#%autoreload 2
# %%
import os

import sirf.Reg as Reg
import sirf.STIR as STIR
import SIRF_data_preparation.data_QC as data_QC
from SIRF_data_preparation.data_utilities import prepare_challenge_Siemens_data, the_data_path, the_orgdata_path

# %% set paths filenames
scanID = 'Siemens_mMR_Hoffman'
orgdata_path = the_orgdata_path(scanID)
data_path = the_data_path(scanID)
fullcounts_data_path = os.path.join(orgdata_path, 'fullcounts')
intermediate_data_path = os.path.join(orgdata_path, 'processing')
extracted_data_path = os.path.join(orgdata_path, 'extracted')
os.makedirs(data_path, exist_ok=True)
os.makedirs(fullcounts_data_path, exist_ok=True)
os.makedirs(intermediate_data_path, exist_ok=True)
# %%
f_template = os.path.join(STIR.get_STIR_examples_dir(), 'Siemens-mMR', 'template_span11.hs')
f_norm = '1.3.12.2.1107.5.2.38.51008.30000023092004393989000000002.n'
f_listmode = '1.3.12.2.1107.5.2.38.51008.30000023092004393989000000003.l.hdr'
f_attn_image = 'reg_mumap.hv'
# %% first run NAC reconstruction
prepare_challenge_Siemens_data(extracted_data_path, fullcounts_data_path, intermediate_data_path, '', f_listmode,
                               'nonexistent', 'reg_mumap.hv', f_norm, f_template, 'prompts', 'mult_factors',
                               'additive_term', None, 'attenuation_factor', 'attenuation_correction_factor', 'scatter')
# %% write current NAC OSEM image as Nifti
NAC_image = STIR.ImageData(os.path.join(intermediate_data_path, 'OSEM_image.hv'))
NAC_image_filename = os.path.join(intermediate_data_path, 'NAC_image.nii')
NAC_image.write_par(NAC_image_filename,
                    os.path.join(STIR.get_STIR_examples_dir(), 'samples', 'stir_math_ITK_output_file_format.par'))
# %% read as Reg.ImageData
NAC_image = Reg.ImageData(NAC_image_filename)

# %% register PET/CT scan to NAC
petct_dir = the_orgdata_path('Siemens_Vision600_Hoffman2')
petct_pet = STIR.ImageData(os.path.join(petct_dir, '23_UMCG_Hoff_STIRRecon_10.hv'))
petct_mumap = STIR.ImageData(os.path.join(petct_dir, '23_UMCG_Hoff_mu_map.hv'))

reg = Reg.NiftyAladinSym()
reg.set_reference_image(NAC_image)
reg.add_floating_image(petct_pet)
reg.process()
transf_matrix = reg.get_transformation_matrix_forward(0)

resampler = Reg.NiftyResampler()
# Set the image we want to resample
resampler.set_reference_image(petct_mumap)
# the floating image is set so we know the domain of the resampled image.
resampler.set_floating_image(NAC_image)
# 0 is nearest neighbour
resampler.set_interpolation_type(0)
resampler.set_padding_value(0)
resampler.add_transformation(transf_matrix)
resampler.process()
reg_mumap = resampler.get_output()
# %% write as Nifti
reg_petct_pet_filename = os.path.join(intermediate_data_path, 'reg_petct_pet')
reg_petct_pet_filename_nii = reg_petct_pet_filename + '.nii'
reg.get_output(0).write(reg_petct_pet_filename_nii)
reg_mumap_filename = os.path.join(intermediate_data_path, 'reg_mumap')
reg_mumap_filename_nii = reg_mumap_filename + '.nii'
reg_mumap.write(reg_mumap_filename_nii)
# %% write as Interfile
reg_mumap = STIR.ImageData(reg_mumap_filename_nii)
reg_mumap.write(reg_mumap_filename + '.hv')

# %%
#umap = STIR.ImageData(os.path.join(orgdata_path,'dicom', '9_Head_MRAC_UTE_UMAP', 'MR.1.3.12.2.1107.5.2.38.51008.202309201458559904611155'))
#vendor_recon = STIR.ImageData(os.path.join(orgdata_path,'dicom', '30003__Head_F18_FDG_Hirn_AC_Images', 'PI.1.3.12.2.1107.5.2.38.51008.2023092015124313549300490'))
# %%
#zoomed_umap = umap.zoom_image_as_template(vendor_recon, 'preserve_values')
# %%
#data_QC.plot_image(vendor_recon)
# %%
