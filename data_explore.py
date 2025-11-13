#%%
import stir
from stirextra import *
import matplotlib.pyplot as plt
import os
import numpy as np


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
num_phantom = 0
beta = 10
phantoms = ['Siemens_mMR_ACR', 'Siemens_mMR_NEMA_IQ', 'GE_D690_NEMA_IQ']
shapes = [(127, 285, 285), (127, 200, 200), (127, 344, 344)]
phantom = phantoms[num_phantom]

dirname = f'output/{phantom}/LBFGSBPC/{beta}/'
fname = f'{dirname}/LBFGSBPC'

def read_reconstructed_image(fname):
    arr = np.fromfile(fname+".v", dtype=np.float32)
    arr.shape = read_interfile_header(fname+".hv")
    return arr

# fname = f'{dirname}/LBFGSBPC_iter{iter:04d}'


# one off to visualise the PETRIC1 reference image
# phantom = "Siemens_Vision600_ZrNEMAIQ"
# fname = "/mnt/share-public/petric/Siemens_Vision600_ZrNEMAIQ/PETRIC/reference_image"

# #%%
# image = to_numpy(stir.FloatVoxelsOnCartesianGrid.read_from_file(fname+".hv"))
# print (image.shape)
# plt.imshow(image[64,:,:], cmap='gray')
# plt.title(f'LBFGSBPC Iteration {iter}')
# plt.axis('off')
# plt.show()
# %%
recons = {}
up = 0
betas = [1,10,100,1000]
for b in betas:
    dirname = f'output/{phantom}/LBFGSBPC/{b}/'
    fname = f'{dirname}/LBFGSBPC'

    arr = read_reconstructed_image(fname)
    print (arr.shape, arr.min(), arr.max())
    recons[b] = arr

    lp = 0
    up = np.percentile(arr, 99.) if np.percentile(arr, 99.) > up else up
# up = 0.0027166688
print(lp, up)
# %%
# %%
plt.subplots(2,2)
slices = 96
plt.suptitle(f'{phantom}: slice={slices} sfs=1e-1 {os.path.basename(fname)}')
cmap = "magma"
up = 0.3e-5
for i, b in enumerate(betas):
     ax = plt.subplot(2,2,i+1)
     ax.imshow(recons[b][slices,:,:], cmap=cmap, vmax=up, vmin=lp)
     ax.set_title(f'Beta: {b}')
     plt.colorbar(ax.imshow(recons[b][slices,:,:], cmap=cmap, vmax=up, vmin=lp), ax=ax)
     ax.axis('off')
plt.show()
#%%

# plt.subplots(2,2)
# plt.suptitle(f'{phantom}: beta={beta} {os.path.basename(fname)}')
# cmap = "gray_r"
# for i, slices in enumerate([32, 64, 96, 120]):
#      ax = plt.subplot(2,2,i+1)
#      ax.imshow(arr[slices,:,:], cmap=cmap, vmax=up, vmin=lp)
#      ax.set_title(f'Slice {slices}')
#      plt.colorbar(ax.imshow(arr[slices,:,:], cmap=cmap, vmax=up, vmin=lp), ax=ax)
#      ax.axis('off')
# plt.show()
# %%
import csv

iterations = []
objectives = []
with open(f"{dirname}/objectives.csv", 'r') as f:
    reader = csv.reader(f)
    for i,row in enumerate(reader):
        if i > 0:
            iterations.append(int(row[0]))
            objectives.append(float(row[1]))

plt.plot(iterations, -np.array(objectives), '-o')
# %%
