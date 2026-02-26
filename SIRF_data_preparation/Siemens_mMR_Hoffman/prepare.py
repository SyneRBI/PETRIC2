# %%
# %load_ext autoreload
# %autoreload 2
# %%
import os

import sirf.Reg as Reg
import sirf.STIR as STIR
import SIRF_data_preparation.create_initial_images as create_initial_images
import SIRF_data_preparation.data_QC as data_QC
from SIRF_data_preparation.data_utilities import (
    prepare_challenge_Siemens_data,
    prepare_challenge_STIR_data,
    the_data_path,
    the_orgdata_path,
)

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
# vendor_recon = STIR.ImageData(os.path.join(orgdata_path,'dicom', '30003__Head_F18_FDG_Hirn_AC_Images',
#             'PI.1.3.12.2.1107.5.2.38.51008.2023092015124313549300490'))
# %%
f_template = os.path.join(STIR.get_STIR_examples_dir(), 'Siemens-mMR', 'template_span11.hs')
f_norm = '1.3.12.2.1107.5.2.38.51008.30000023092004393989000000002.n'
f_listmode = '1.3.12.2.1107.5.2.38.51008.30000023092004393989000000003.l.hdr'
f_attn_image = 'reg_mumap.hv'
# %% first run first without mu-map for NAC reconstruction
prepare_challenge_Siemens_data(extracted_data_path, fullcounts_data_path, intermediate_data_path, '', f_listmode,
                               'nonexistent', 'reg_mumap.hv', f_norm, f_template, 'prompts', 'mult_factors',
                               'additive_term', None, 'attenuation_factor', 'attenuation_correction_factor', 'scatter')
# %% do NAC recon
f_prompts = os.path.join(fullcounts_data_path, 'prompts.hs')
acquired_data = STIR.AcquisitionData(f_prompts)
additive_term = STIR.AcquisitionData(os.path.join(fullcounts_data_path, 'additive_term.hs'))
mult_factors = STIR.AcquisitionData(os.path.join(fullcounts_data_path, 'mult_factors.hs'))
create_initial_images.run(outdir=intermediate_data_path, acquired_data=acquired_data, additive_term=additive_term,
                          mult_factors=mult_factors, template_image=acquired_data.create_uniform_image(0),
                          write_kappa=False)
# %% Run registration
# This code is made much more complicated as I save images to Nifti via STIR,
# as opposed to relying on the SIRF conversion from/to Reg.ImageData and STIR.ImageData,
# as this is likely still buggy at this point.
# write current NAC OSEM image as Nifti
NAC_image = STIR.ImageData(os.path.join(intermediate_data_path, 'OSEM_image.hv'))
NAC_image_filename_stem = os.path.join(intermediate_data_path, 'NAC_image')
NAC_image_filename = NAC_image_filename_stem + '.nii'
NAC_image.write_par(NAC_image_filename,
                    os.path.join(STIR.get_STIR_examples_dir(), 'samples', 'stir_math_ITK_output_file_format.par'))
# read as Reg.ImageData
NAC_image_nii = Reg.ImageData(NAC_image_filename)

# %% read in PET/CT scan
petct_dir = the_orgdata_path('Siemens_Vision600_Hoffman2')
petct_pet = STIR.ImageData(os.path.join(petct_dir, '23_UMCG_Hoff_STIRRecon_10.hv'))
petct_mumap = STIR.ImageData(os.path.join(petct_dir, '23_UMCG_Hoff_mu_map.hv'))
# convert to nifti
petct_mumap_image_filename = os.path.join(intermediate_data_path, 'petct_pet.nii')
petct_mumap.write_par(petct_mumap_image_filename,
                      os.path.join(STIR.get_STIR_examples_dir(), 'samples', 'stir_math_ITK_output_file_format.par'))
# read as Reg.ImageData
petct_mumap = Reg.ImageData(petct_mumap_image_filename)
# %% run registration of petct_pet to NAC
reg = Reg.NiftyAladinSym()
reg.set_reference_image(NAC_image_nii)
reg.add_floating_image(petct_pet)
reg.process()
transf_matrix = reg.get_transformation_matrix_forward()
# %% resample petct_mumap according to the transformation
resampler = Reg.NiftyResampler()
# Set the image we want to resample
resampler.set_reference_image(NAC_image_nii)
# the floating image is set so we know the domain of the resampled image.
resampler.set_floating_image(petct_mumap)
# 0 is nearest neighbour
resampler.set_interpolation_type(0)
resampler.set_padding_value(0)
resampler.add_transformation(transf_matrix)
resampler.process()
reg_mumap_nii = resampler.get_output()
# %% write as Nifti
reg_petct_pet_filename = os.path.join(intermediate_data_path, 'reg_petct_pet')
reg_petct_pet_filename_nii = reg_petct_pet_filename + '.nii'
reg.get_output(0).write(reg_petct_pet_filename_nii)
reg_mumap_filename_stem = os.path.join(intermediate_data_path, 'reg_mumap')
reg_mumap_filename_nii = reg_mumap_filename_stem + '.nii'
reg_mumap_nii.write(reg_mumap_filename_nii)
# %% write as Interfile
reg_mumap_filename = reg_mumap_filename_stem + '.hv'
reg_mumap = STIR.ImageData(reg_mumap_filename_nii)
reg_mumap.write(reg_mumap_filename)
# %% plot for manual verification
data_QC.plot_image(NAC_image, save_name=NAC_image_filename_stem, vmax=NAC_image.max() / 2)
# %%
data_QC.plot_image(reg_mumap, save_name=reg_mumap_filename_stem)
# %% re-run the list-mode processing, now with mu-map, such that we get proper AC and scatter correction
f_stir_norm_header = os.path.join(intermediate_data_path, f_norm + '_convertEOL.hdr')
prepare_challenge_STIR_data(fullcounts_data_path, intermediate_data_path, os.path.join(extracted_data_path, f_listmode),
                            reg_mumap_filename, f_stir_norm_header, f_template=f_prompts, f_randoms=None)

# %% create final images. Use zoom=2 in x,y to get close to vendor voxel-size, and crop some air
acquired_data = STIR.AcquisitionData(f_prompts)
additive_term = STIR.AcquisitionData(os.path.join(fullcounts_data_path, 'additive_term.hs'))
mult_factors = STIR.AcquisitionData(os.path.join(fullcounts_data_path, 'mult_factors.hs'))
template_image = acquired_data.create_uniform_image(0)
template_image = template_image.zoom_image(zooms=(1, 2, 2), size=(127, 255, 255))
create_initial_images.run(outdir=fullcounts_data_path, acquired_data=acquired_data, additive_term=additive_term,
                          mult_factors=mult_factors, template_image=template_image)
# %%
OSEM_image = STIR.ImageData(os.path.join(fullcounts_data_path, 'OSEM_image.hv'))
print(OSEM_image.max())
data_QC.plot_image(OSEM_image)
