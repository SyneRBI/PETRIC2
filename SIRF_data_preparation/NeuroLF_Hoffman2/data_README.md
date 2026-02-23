# Overall description

This dataset contains a 15 minute acquisition at 22 MBq of a cylindrical Hoffman brain phantom, that simulates an FDG brain scan by having a structure of many plastic slices, the gaps between which are filled with radioactive water.

# Phantom description

Hoffman brain phantom:

- cylindrical phantom with layered geometry to achieve three levels of activity in brain FDG-like outlines
- filled with F18-FDG solution
- 22 MBq
- 15 minute acquisition
- for purposes of attenuation, the plastic and water were both set to 0.096 cm2/g
- the outside dimensions of the cylinder are 175 mm length and 203 mm diameter and it was approximately centred in the field of view

# Acquisition information

## Institution

Positrigo AG, Zurich, Switzerland

## Scanner model

Positrigo NeuroLF brain scanner

## Acquisition Date

26 NOVEMBER 2025

## Radiopharmaceutical and nuclide information

FDG, F-18

## Preparation protocol

The phantom was filled with 22 MBq of FDG solution and shaken well to distribute the activity as evenly as possible. In the Hoffman phantom,
low activity brain regions like the white matter are created by having two thin activity layers instead of 10 - this leads to some visible transaxial patterns in the reconstructed image.
Also some slivers of activity are left in passive regions, because the plastic slices have gaps in between where water can go in.

## Acquisition protocol

A 15 min PET scan was performed in list-mode.

## Reconstruction settings

- STIR OSMAPOSL with ray tracing
- 30 subiterations
- 4 subsets
- Gaussian filter with 2.5 mm FWHM
- decay, randoms, attenuation and scatter correction

## VOI description

The phantom model (https://depts.washington.edu/petctdro/DROhoffman_main.html) was first averaged axially across corresponding sets of 10 slices and then registered to the reconstruction using NiftyReg. Then, all voxels with activity above 0.9 were assigned to grey matter (value 3), all voxels below 0.05 to ventricles (value 1) or background (value 0) and the voxels in between to white matter (value 2).

### VOI_whole_object: whole phantom

Convex hull of the active part of the phantom

### VOI_background: eroded version of white matter

Central areas of white matter, that should have an intermediate activity.

### VOI_WM: white matter

The white matter area should have an intermediate activity, compared to the ventricles (that should be cold) and the grey matter (that should have 5 times higher activity).

### VOI_GM: grey matter

The grey matter area which has the highest activity.
