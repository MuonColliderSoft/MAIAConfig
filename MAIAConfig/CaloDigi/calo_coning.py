'''-------------------------------------------------------------'''
'''  Calorimeter hit cone filtering and BIB selection            '''
'''-------------------------------------------------------------'''
# Gaudi-native equivalent of the Marlin CaloConer + CaloHitSelector chain in
# steer_reco.py. For each calorimeter region the reconstructed hits are first
# restricted to a cone around the signal MC particles (CaloConer, "...Coned"),
# then thresholded in energy and time to suppress the beam-induced background
# (CaloHitSelector, "...Sel"). Pandora consumes the "...Sel" collections.
from GaudiKernel.Constants import INFO
from Configurables import CaloConer, CaloHitSelector
from Common.calo_thresholds import find_calo_thresholds

# Cone half-opening angle around the MC particles [rad] (same for all regions).
_CONE_WIDTH = 0.6

# Calorimeter regions: (collection prefix, technology). The reco collections come
# from calorimetry_{EM,HAD}.py: "<prefix>CollectionRec" / "<prefix>RelationsSimRec".
_CALO_REGIONS = [
    ("EcalBarrel", "ECAL"),
    ("EcalEndcap", "ECAL"),
    ("HcalBarrel", "HCAL"),
    ("HcalEndcap", "HCAL"),
]


def _coner_cfg(prefix):
    return CaloConer(
        f"{prefix}Coner",
        MCParticleCollectionName = ["MCParticles"],
        CaloHitCollectionName = [f"{prefix}CollectionRec"],
        CaloRelationCollectionName = [f"{prefix}RelationsSimRec"],
        GoodHitCollection = [f"{prefix}CollectionConed"],
        GoodRelationCollection = [f"{prefix}RelationsSimConed"],
        ConeWidth = _CONE_WIDTH,
        OutputLevel = INFO,
    )


def _selector_cfg(prefix, technology):
    selector = CaloHitSelector(
        f"{prefix}Selector",
        CaloHitCollectionName = [f"{prefix}CollectionConed"],
        CaloRelationCollectionName = [f"{prefix}RelationsSimConed"],
        GoodHitCollection = [f"{prefix}CollectionSel"],
        GoodRelationCollection = [f"{prefix}RelationsSimSel"],
        Nsigma = 0,
        TimeWindowMin = -0.3,
        TimeWindowMax = 0.3,
        DoBIBsubtraction = False,
        OutputLevel = INFO,
    )
    if technology == "ECAL":
        # ECAL uses the per-(theta, layer) threshold maps (threshold = mode, Nsigma=0).
        selector.ThresholdsFilePath = find_calo_thresholds("ECAL")
    else:
        # HCAL uses a flat energy threshold instead of the maps.
        selector.FlatThreshold = 5e-05
    return selector


def calo_coner_cfgs():
    """Return the four CaloConer instances (one per calorimeter region)."""
    return [_coner_cfg(prefix) for prefix, _ in _CALO_REGIONS]


def calo_selector_cfgs():
    """Return the four CaloHitSelector instances (one per calorimeter region)."""
    return [_selector_cfg(prefix, tech) for prefix, tech in _CALO_REGIONS]
