"""Settings for recon and display used in the data preparation"""
from dataclasses import dataclass

from petric import DATA_SLICES

DATA_SUBSETS = {
    'Siemens_mMR_NEMA_IQ': 7, 'Siemens_mMR_NEMA_IQ_lowcounts': 7, 'Siemens_mMR_ACR': 7, 'NeuroLF_Hoffman_Dataset': 16,
    'NeuroLF_Hoffman2': 16, 'Mediso_NEMA_IQ': 12, 'Siemens_Vision600_thorax': 5, 'GE_DMI3_Torso': 8,
    'Siemens_Vision600_Hoffman': 5, 'NeuroLF_Esser_Dataset': 8, 'NeuroLF_Esser2': 8, 'Siemens_Vision600_ZrNEMAIQ': 5,
    'GE_D690_NEMA_IQ': 16, 'Mediso_NEMA_IQ_lowcounts': 6, 'GE_DMI4_NEMA_IQ': 8}

# Note: set to -1 if unknown (will then use percentile of the max)
PETRIC1_clims = {
    'GE_D690_NEMA_IQ': 1, 'GE_DMI3_Torso': 3.5, 'GE_DMI4_NEMA_IQ': 1, 'Mediso_NEMA_IQ': 2.5,
    'NeuroLF_Esser_Dataset': .5, 'NeuroLF_Esser2': .3, 'NeuroLF_Hoffman_Dataset': 2, 'NeuroLF_Hoffman2': 1.2,
    'Siemens_mMR_ACR': 3e-2, 'Siemens_mMR_NEMA_IQ': 0.2, 'Siemens_Vision600_Hoffman': .4,
    'Siemens_Vision600_thorax': 5e-1, 'Siemens_Vision600_ZrNEMAIQ': .002}

preferred_scaling = {
    'GE_D690_NEMA_IQ': 1e-1,
    'GE_DMI3_Torso': 1e-1,
    'GE_DMI4_NEMA_IQ': 1e-1,
    'Mediso_NEMA_IQ': 1e-2,
    'NeuroLF_Esser_Dataset': 1e-2,
    'NeuroLF_Esser2': 2.60139e+06 / 2.08356e+08,
    'NeuroLF_Hoffman_Dataset': 1e-2,
    'NeuroLF_Hoffman2': 6.87569e+06 / 3.16697e+08,
    'Siemens_mMR_ACR': 1e-1,
    'Siemens_mMR_NEMA_IQ': 1e-1,
    'Siemens_Vision600_Hoffman': 1e-2,
    'Siemens_Vision600_thorax': 1e-2,
    'Siemens_Vision600_ZrNEMAIQ': 1                # original scaling
}


@dataclass
class DatasetSettings:
    num_subsets: int
    slices: dict
    vmax: float


def get_settings(scanID: str):
    return DatasetSettings(DATA_SUBSETS[scanID], DATA_SLICES[scanID], PETRIC1_clims[scanID] * preferred_scaling[scanID])
