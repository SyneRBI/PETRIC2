# Files for preparing Siemens_mMR_Hoffman data

This uses an acquisition of the Hoffman phantom on the mMR from Leipzig.

The problem is that the MRAC is not useful for most phantoms, including the Hoffman.
Here we get round this by using a PET/CT scan of the Hoffman:
1. reconstruct mMR without AC
2. register the PET/CT PET to the mMR NAC
3. transform the PET/CT mu-map accordingly

This strategy is mostly ok, however it ignores problems with the bed.
Ideally, we'd remove the bed from the PET/CT mu-map, transform, and then
put the mMR bed in again. This is not yet implemented here, whcih will lead
to some artefacts in the reconstructed images.
Those are not so relevant for PETRIC though.
