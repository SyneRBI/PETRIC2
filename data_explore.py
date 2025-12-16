#%%
import matplotlib.pyplot as plt
import os
import numpy as np
from extract_data_slices import extract_data_slices
# from SIRF_data_preparation.preferred_scaling import preferred_scaling
from SIRF_data_preparation.dataset_settings import get_settings, preferred_scaling

def read_interfile_header(fname):
    """"""""
    import re
    # assuming:
    #  3D, float32, little-endian

    shape = [0,0,0]
    with open(fname, 'r') as f:
        for line in f:
            match = re.search(r'!matrix size \[(\d+)\] := (\d+)', line)
            if match:
                index = int(match.group(1))  # 3
                size = int(match.group(2))   # 127
                print(f"Index: {index}, Size: {size}")
                shape[index-1] = size
    return tuple(shape[::-1])



iter = 400
num_phantom = 2
beta = 1
phantoms = ['Siemens_mMR_ACR', 'Siemens_mMR_NEMA_IQ', 'GE_D690_NEMA_IQ', 'Siemens_Vision600_Hoffman']
shapes = [(127, 285, 285), (127, 200, 200), (127, 344, 344), (127, 344, 344)]
# phantom = phantoms[num_phantom]
phantom = "Siemens_mMR_ACR"

# algo = 'LBFGSBPC'
algo = 'MaGeZ'
dirname = f'output/{phantom}/{algo}/{beta}/'
fname = f'{dirname}/{algo}'

def read_reconstructed_image(fname):
    arr = np.fromfile(fname+".v", dtype=np.float32)
    arr.shape = read_interfile_header(fname+".hv")
    return arr

# fname = f'{dirname}/LBFGSBPC_iter{iter:04d}'


# one off to visualise the PETRIC1 reference image
# phantom = "Siemens_Vision600_ZrNEMAIQ"
# fname = "/mnt/share-public/petric/Siemens_Vision600_ZrNEMAIQ/PETRIC/reference_image"

# #%%
# import stir
# from stirextra import *
# image = to_numpy(stir.FloatVoxelsOnCartesianGrid.read_from_file(fname+".hv"))
# print (image.shape)
# plt.imshow(image[64,:,:], cmap='gray')
# plt.title(f'LBFGSBPC Iteration {iter}')
# plt.axis('off')
# plt.show()
# %%
recons = {}
up = 0
sup = np.inf

betas = ["0.5", "0.1", "0.05"]
# betas = ["0.5", "1", "2"]
for b in betas:
    dirname = f'output/{phantom}/{algo}/{b}/'
    if b == 1.75:
        print("WTF")
        fname = f'{dirname}/{algo}'
        fname += '_iter0400.npy'
        arr = np.load(fname)
    else:
        fname = f'{dirname}/{algo}'
        arr = read_reconstructed_image(fname)
    print (fname)
    recons[b] = arr

    lp = 0
    nnp = np.percentile(arr, 97.5)
    up = nnp if nnp > up else up
    sup = nnp if nnp < sup else sup
    print (fname, arr.shape, arr.min(), arr.max(), nnp)
    
    print("------------------------------------")
# up = 0.0027166688
print(f"lp {lp}, up {up}, sup {sup}")
#%% 
# read OSEM
OSEM_dir = f"/mnt/share-public/petric/wip/petric2/{phantom}/"
OSEM_fname = f"{OSEM_dir}/OSEM_image"
osem_arr = read_reconstructed_image(OSEM_fname)
print (OSEM_fname, osem_arr.shape, osem_arr.min(), osem_arr.max())
# nnp = np.percentile(arr, 99.)
# up = nnp if nnp > up else up
# sup = nnp if nnp < sup else sup


#%%
ncol = 2
nrow = int(np.ceil((len(betas)+1)/ncol))

fig, other = plt.subplots(nrow, ncol, figsize=(4*ncol,4*nrow))
DATA_SLICES = extract_data_slices()
# slices = 18
slices = get_settings(phantom).slices['transverse_slice']
# up = 0.9e-5
top = get_settings(phantom).vmax
sfs = preferred_scaling[phantom]
plt.suptitle(f'{algo}/{phantom}: slice={slices} sfs={sfs} up={top:.1e}')
cmap = "magma"
# cmap = "Greys"

for i, b in enumerate(betas):
     ax = plt.subplot(nrow,ncol,i+1)
     f = ax.imshow(recons[b][slices,:,:], cmap=cmap, vmax=top, vmin=lp)
     ax.set_title(f'Beta: {b}')
    #  plt.colorbar(
    #      f, 
    #      ax=ax)
     ax.axis('off')

ax = plt.subplot(nrow,ncol,i+2)
# diff = (recons[2][slices,:,:]-recons[1][slices,:,:])
# clim = np.max(np.abs(diff))
# f = ax.imshow(diff, cmap="seismic", vmin=-clim, vmax=clim)
# ax.set_title(f'diff Beta {betas[2]} - Beta {betas[1]}')

ax.imshow(osem_arr[slices,:,:], cmap=cmap, vmax=top, vmin=lp)
ax.set_title(f'OSEM')
# plt.colorbar(ax.imshow(osem_arr[slices,:,:], cmap=cmap, vmax=top, vmin=lp), ax=ax)
ax.axis('off')
# ax = plt.subplot(2,2,i+3)
# ax.axis('off')

cax = plt.axes([0.915, 0.02, 0.02, 0.907])  # Adjust the position of the colorbar
fig.colorbar(f, orientation='vertical', 
            #  use_gridspec=True,
             cax=cax)
# Remove tight_layout and use subplots_adjust to control spacing precisely
plt.subplots_adjust(wspace=0.3, hspace=0.02, 
                    left=0.02, right=0.91, 
                    top=0.9, bottom=0.02)
plt.show()
# #%%

# ncol = 2
# nrow = int(np.ceil((len(betas)+1)/ncol))

# fig, other = plt.subplots(nrow, ncol, figsize=(4*ncol,4*nrow))
# DATA_SLICES = extract_data_slices()
# slices = 72
# # slices = DATA_SLICES[phantom]['transverse_slice']
# slices = get_settings(phantom).slices['transverse_slice']
# # up = 0.9e-5
# top = get_settings(phantom).vmax
# # top = 0.3
# sfs = preferred_scaling[phantom]
# plt.suptitle(f'{algo}/{phantom}: slice={slices} sfs={sfs} up={top:.1e}')
# cmap = "magma"

# from glob import glob
# dirname = f'output/{phantom}/{algo}/{b}/'
# fname = f'{dirname}/{algo}'
# iterates = glob(dirname + "/*_iter*.npy")

# # plot iterations
# for i, b in enumerate(iterates):
#     ax = plt.subplot(nrow,ncol,i+1)
#     arr = np.load(b)
#     f = ax.imshow(arr[slices,:,:], cmap=cmap, vmax=top, vmin=lp)
#     ax.set_title(f'{b}')
#     ax.axis('off')


# # cax = plt.axes([0.915, 0.02, 0.02, 0.907])  # Adjust the position of the colorbar
# # fig.colorbar(f, orientation='vertical', 
# #             #  use_gridspec=True,
# #              cax=cax)
# # Remove tight_layout and use subplots_adjust to control spacing precisely
# # plt.subplots_adjust(wspace=0.3, hspace=0.02, 
# #                     left=0.02, right=0.91, 
# #                     top=0.9, bottom=0.02)
# plt.show()
# # %%
# import csv

# iterations = []
# objectives = []
# with open(f"{dirname}/objectives.csv", 'r') as f:
#     reader = csv.reader(f)
#     for i,row in enumerate(reader):
#         if i > 0:
#             iterations.append(int(row[0]))
#             objectives.append(float(row[1]))

# plt.plot(iterations, -np.array(objectives), '-o')
# # %%

# %%
import matplotlib.pyplot as plt
import matplotlib.cm as cm

N = 4
colors = cm.get_cmap('tab20c', N)  # or 'tab20', 'Set1', 'Set2', 'Set3', 'Paired'
cc = [0.2,0.5,0.7]
# Use in a plot
for i in range(N):
    plt.scatter(i, i, c=[el/(i+1) for i,el in enumerate(cc)] +[1], s=100)
plt.show()
# %%
