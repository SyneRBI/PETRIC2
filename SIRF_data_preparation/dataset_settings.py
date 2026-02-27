"""Settings for recon and display used in the data preparation"""
# flake8: noqa: E501
from dataclasses import dataclass

# yapf: disable
DATA = {
    'GE_D690_NEMA_IQ': {'subsets': 16, 'name': "D690_NEMA", 'slices': {'transverse': 23}, 'clim': 1, 'scale': 1e-1},
    'GE_DMI3_Torso': {'subsets': 8, 'name': "DMI3_Torso", 'slices': {'transverse': 10}, 'clim': 3.5, 'scale': 1e-1},
    'GE_DMI4_NEMA_IQ': {'subsets': 8, 'name': "DMI4_NEMA", 'slices': {'transverse': 27, 'coronal': 109, 'sagittal': 78}, 'clim': 1, 'scale': 1e-1},
    'Mediso_NEMA_IQ_lowcounts': {'subsets': 6, 'name': "Mediso_NEMA-low", 'slices': {'transverse': 22, 'coronal': 74, 'sagittal': 70}},
    'Mediso_NEMA_IQ': {'subsets': 12, 'name': "Mediso_NEMA", 'slices': {'transverse': 22, 'coronal': 89, 'sagittal': 66}, 'clim': 2.5, 'scale': 1e-2},
    'NeuroLF_Esser_Dataset': {'subsets': 8, 'name': "NeuroLF_Esser", 'slices': {'transverse': 20}, 'clim': .5, 'scale': 1e-2},
    'NeuroLF_Esser2': {'subsets': 8, 'slices': {'transverse': 20}, 'clim': .3, 'scale': 2.60139e+06 / 2.08356e+08},
    'NeuroLF_Hoffman_Dataset': {'subsets': 16, 'name': "NeuroLF_Hoffman", 'slices': {'transverse': 72}, 'clim': 2, 'scale': 1e-2},
    'NeuroLF_Hoffman2': {'subsets': 16, 'slices': {'transverse': 72}, 'clim': 1.2, 'scale': 6.87569e+06 / 3.16697e+08},
    'Siemens_mMR_ACR': {'subsets': 7, 'name': "mMR_ACR", 'slices': {'transverse': 99}, 'clim': 3e-2, 'scale': 1e-1},
    'Siemens_mMR_Hoffman': {'subsets': 7, 'name': "mMR_Hoffman", 'clim': 1.4, 'scale': 2.02743e+06 / 3.20694e+06},
    'Siemens_mMR_NEMA_IQ_lowcounts': {'subsets': 7, 'name': "mMR_NEMA-low", 'slices': {'transverse': 72, 'coronal': 109, 'sagittal': 89}},
    'Siemens_mMR_NEMA_IQ': {'subsets': 7, 'name': "mMR_NEMA", 'slices': {'transverse': 72, 'coronal': 109, 'sagittal': 89}, 'clim': 0.2, 'scale': 1e-1},
    'Siemens_Vision600_Hoffman': {'subsets': 5, 'name': "Vision600_Hoffman", 'clim': .4, 'scale': 1e-2},
    'Siemens_Vision600_Hoffman2': {'subsets': 5, 'name': "Vision600_Hoffman2", 'clim': 0.7, 'scale': 4.43249e+06 / 8.85466e+08},
    'Siemens_Vision600_thorax': {'subsets': 5, 'name': "Vision600_thorax", 'clim': 5e-1, 'scale': 1e-2},
    'Siemens_Vision600_ZrNEMAIQ': {'subsets': 5, 'name': "Vision600_ZrNEMA", 'slices': {'transverse': 60}, 'clim': .002},
}
# yapf: enable

DATA_SUBSETS = {k: v['subsets'] for k, v in DATA.items()}
names = {k: v.get('name', k) for k, v in DATA.items()}
DATA_SLICES = {
    k: {f"{axis}_slice": i
        for axis, i in v.get('slices', {}).items()}                 # type: ignore[attr-defined]
    for k, v in DATA.items()}
PETRIC1_clims = {k: v.get('clim', None) for k, v in DATA.items()}   # vmax for full-count images
preferred_scaling = {k: v.get('scale', 1) for k, v in DATA.items()} # default: original scaling


@dataclass
class DatasetSettings:
    num_subsets: int
    slices: dict
    vmax: float | None
    name: str


def get_settings(scanID: str):
    return DatasetSettings(
        DATA_SUBSETS[scanID],                             # type: ignore[arg-type]
        DATA_SLICES[scanID],                              # type: ignore[arg-type]
        PETRIC1_clims[scanID] * preferred_scaling[scanID] # type: ignore[operator]
        if PETRIC1_clims[scanID] is not None else None,
        names[scanID])                                    # type: ignore[arg-type]
