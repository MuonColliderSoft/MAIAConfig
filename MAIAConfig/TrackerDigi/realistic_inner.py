from GaudiKernel.Constants import INFO
from Configurables import MuonCVXDDigitiser

from Common.overlay_utils import overlay_input


_INNER_TRACKER_LAYER_IDS = [0, 1, 2]


def _inner_tracker_digitiser(name, input_collection, sim_local_collection, hit_collection, relation_collection, raw_relation_collection):
    return MuonCVXDDigitiser(
        name,
        CollectionName = input_collection,
        EventHeader = ["EventHeader"],
        SimHitLocCollectionName = [sim_local_collection],
        OutputCollectionName = [hit_collection],
        RelationColName = [relation_collection],
        RawHitsLinkColName = [raw_relation_collection],
        SubDetectorName = sim_local_collection,
        LayerIDs = _INNER_TRACKER_LAYER_IDS,
        OutputLevel = INFO,
    )


def ITBarrel_cfg(args):
    """
    Create a new inner barrel digitiser instance with the MuonCVXDDigitiser.
    """
    inputHitCollections = overlay_input("InnerTrackerBarrelCollection", args)
    return _inner_tracker_digitiser(
        "InnerBarrelDigitiser",
        inputHitCollections,
        "InnerTrackerBarrel",
        "ITBarrelHits",
        "ITBarrelHitsRelations",
        "ITBarrelRawHitRelations",
    )


def ITEndcap_cfg(args):
    """
    Create a new inner endcap digitiser instance with the MuonCVXDDigitiser.
    """
    inputHitCollections = overlay_input("InnerTrackerEndcapCollection", args)
    return _inner_tracker_digitiser(
        "InnerEndcapDigitiser",
        inputHitCollections,
        "InnerTrackerEndcap",
        "ITEndcapHits",
        "ITEndcapHitsRelations",
        "ITEndcapRawHitRelations",
    )
