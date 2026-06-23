from GaudiKernel.Constants import INFO, WARNING
from Configurables import DDPlanarDigi
from Common.overlay_utils import overlay_input

def OTBarrel_cfg(args):
    """
    Create a new outer barrel digitiser instance with the given parameters.
    """
    inputHitCollections = overlay_input("OuterTrackerBarrelCollection", args)
    return DDPlanarDigi(
        "OTBarrelDigitiser",
        CorrectTimesForPropagation = True,
        IsStrip = False,
        ResolutionT = [0.06],
        ResolutionU = [0.007],
        ResolutionV = [0.09],
        SubDetectorName = "OuterTrackers",
        TimeWindowMax = [0.3],
        TimeWindowMin = [-0.18],
        UseTimeWindow = True,
        SimTrackHitCollectionName = inputHitCollections,
        SimTrkHitRelCollection = ["OTBarrelHitsRelations"],
        TrackerHitCollectionName = ["OTBarrelHits"],
        ForceHitsOntoSurface = True,
        OutputLevel = INFO
    )

def OTEndcap_cfg(args):
    """
    Create a new outer endcap digitiser instance with the given parameters.
    """
    inputHitCollections = overlay_input("OuterTrackerEndcapCollection", args)
    return DDPlanarDigi(
        "OTEndcapDigitiser",
        CorrectTimesForPropagation = True,
        IsStrip = False,
        ResolutionT = [0.06],
        ResolutionU = [0.007],
        ResolutionV = [0.09],
        SubDetectorName = "OuterTrackers",
        TimeWindowMax = [0.3],
        TimeWindowMin = [-0.18],
        UseTimeWindow = True,
        SimTrackHitCollectionName = inputHitCollections,
        SimTrkHitRelCollection = ["OTEndcapHitsRelations"],
        TrackerHitCollectionName = ["OTEndcapHits"],
        ForceHitsOntoSurface = True,
        OutputLevel = INFO
    )
