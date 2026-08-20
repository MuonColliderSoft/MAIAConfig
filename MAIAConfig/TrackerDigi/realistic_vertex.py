from GaudiKernel.Constants import INFO
from Configurables import MuonCVXDDigitiser

from Common.overlay_utils import overlay_input


_VERTEX_BARREL_LAYER_IDS = [0, 1, 2, 4, 6]
_VERTEX_ENDCAP_LAYER_IDS = [0, 1, 2, 3, 4, 5, 6, 7]


def _vertex_digitiser(name, input_collection, sim_local_collection, hit_collection, relation_collection, raw_relation_collection, layer_ids):
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


def VXDBarrel_cfg(args):
    """
    Create a new vertex barrel digitiser instance with the MuonCVXDDigitiser.
    """
    inputHitCollections = overlay_input("VertexBarrelCollection", args)
    return _vertex_digitiser(
        "VXDBarrelDigitiser",
        inputHitCollections,
        "VertexBarrel",
        "VXDBarrelHits",
        "VXDBarrelHitsRelations",
        "VXDBarrelRawHitRelations",
        _VERTEX_BARREL_LAYER_IDS,
    )


def VXDEndcap_cfg(args):
    """
    Create a new vertex endcap digitiser instance with the MuonCVXDDigitiser.
    """
    inputHitCollections = overlay_input("VertexEndcapCollection", args)
    return _vertex_digitiser(
        "VXDEndcapDigitiser",
        inputHitCollections,
        "VertexEndcap",
        "VXDEndcapHits",
        "VXDEndcapHitsRelations",
        "VXDEndcapRawHitRelations",
        _VERTEX_ENDCAP_LAYER_IDS,
    )