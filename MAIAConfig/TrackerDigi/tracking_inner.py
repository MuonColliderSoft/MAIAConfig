from GaudiKernel.Constants import INFO, WARNING
from Configurables import DDPlanarDigi
from Common.overlay_utils import overlay_input

def ITBarrel_cfg(args):
    """
    Create a new inner barrel digitiser instance with the given parameters.
    """
    inputHitCollections = overlay_input("InnerTrackerBarrelCollection", args)
    return DDPlanarDigi(
        "InnerBarrelDigitiser",
        CorrectTimesForPropagation = True,
        IsStrip = True,
        ResolutionT = [0.06],
        ResolutionU = [0.007],
        ResolutionV = [0.09],
        SubDetectorName = "InnerTrackers",
        TimeWindowMax = [0.3],
        TimeWindowMin = [-0.18],
        UseTimeWindow = True,
        SimTrackHitCollectionName = inputHitCollections,
        SimTrkHitRelCollection = ["ITBarrelHitsRelations"],
        TrackerHitCollectionName = ["ITBarrelHits"],
        OutputLevel = INFO
    )

def ITEndcap_cfg(args):
    """
    Create a new inner endcap digitiser instance with the given parameters.
    """
    inputHitCollections = overlay_input("InnerTrackerEndcapCollection", args)
    return DDPlanarDigi(
        "InnerEndcapDigitiser",
        CorrectTimesForPropagation = True,
        IsStrip = False,
        ResolutionT = [0.06],
        ResolutionU = [0.007],
        ResolutionV = [0.09],
        SubDetectorName = "InnerTrackers",
        TimeWindowMax = [0.3],
        TimeWindowMin = [-0.18],
        UseTimeWindow = True,
        SimTrackHitCollectionName = inputHitCollections,
        SimTrkHitRelCollection = ["ITEndcapHitsRelations"],
        TrackerHitCollectionName = ["ITEndcapHits"],
        OutputLevel = INFO
    )
