preferred_scaling = {
    'GE_D690_NEMA_IQ': "1e-1",
    'GE_DMI3_Torso': "1e-1",
    'GE_DMI4_NEMA_IQ': "1e-1",
    'Mediso_NEMA_IQ': "1e-2",
    'NeuroLF_Esser_Dataset': "1e-1", # could be even smaller; 1e-2 too much
    'NeuroLF_Hoffman_Dataset': "1e-2", # a lot of artifacts
    'Siemens_mMR_ACR': "1e-1", # might already be too noisy
    'Siemens_mMR_NEMAIQ': "1e-1", # might already be too noisy
    'Siemens_Vision600_Hoffman': "1e-2", # happy with that one
    'Siemens_Vision600_thorax': "1e-2", # could be even smaller; 1e-3 too much
    'Siemens_Vision600_ZrNEMAIQ': "1" # original scaling
    }