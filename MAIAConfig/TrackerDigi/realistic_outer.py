from GaudiKernel.Constants import INFO
from Configurables import MuonCVXDDigitiser

from Common.overlay_utils import overlay_input


_OUTER_TRACKER_BARREL_LAYER_IDS = [0, 1, 2]
_OUTER_TRACKER_ENDCAP_LAYER_IDS = [0, 1, 2, 3]


def _outer_tracker_digitiser(name, input_collection, sim_local_collection, hit_collection, relation_collection, raw_relation_collection, layer_ids):
    return MuonCVXDDigitiser(
        name,
        CollectionName = input_collection,
        EventHeader = ["EventHeader"],
        SimHitLocCollectionName = [sim_local_collection],
        OutputCollectionName = [hit_collection],
        RelationColName = [relation_collection],
        RawHitsLinkColName = [raw_relation_collection],
        SubDetectorName = sim_local_collection,
        LayerIDs = layer_ids,
        OutputLevel = INFO,
    )


def OTBarrel_cfg(args):
    """
    Create a new outer barrel digitiser instance with the MuonCVXDDigitiser.
    """
    inputHitCollections = overlay_input("OuterTrackerBarrelCollection", args)
    return _outer_tracker_digitiser(
        "OTBarrelDigitiser",
        inputHitCollections,
        "OuterTrackerBarrel",
        "OTBarrelHits",
        "OTBarrelHitsRelations",
        "OTBarrelRawHitRelations",
        _OUTER_TRACKER_BARREL_LAYER_IDS,
    )


def OTEndcap_cfg(args):
    """
    Create a new outer endcap digitiser instance with the MuonCVXDDigitiser.
    """
    inputHitCollections = overlay_input("OuterTrackerEndcapCollection", args)
    return _outer_tracker_digitiser(
        "OTEndcapDigitiser",
        inputHitCollections,
        "OuterTrackerEndcap",
        "OTEndcapHits",
        "OTEndcapHitsRelations",
        "OTEndcapRawHitRelations",
        _OUTER_TRACKER_ENDCAP_LAYER_IDS,
    )
