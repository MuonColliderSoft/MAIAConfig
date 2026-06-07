from GaudiKernel.Constants import INFO, WARNING, DEBUG
from Configurables import CollectionMerger

def _coned(name, args):
    """Append "Coned" to a collection name when tracker coning is enabled."""
    return name + "Coned" if getattr(args, "doTrackerConing", False) else name

def mergehits_cfg(args):
    """
    Create a new CollectionMerger instance for merging hits.
    """
    bases = ["VXDBarrelHits", "ITBarrelHits", "OTBarrelHits",
             "VXDEndcapHits", "ITEndcapHits", "OTEndcapHits"]
    return CollectionMerger(
        "MergeHits",
        InputCollections = [_coned(b, args) for b in bases],
        OutputCollection = ["MergedTrackerHits"],
        OutputLevel = INFO
    )

def mergehitsrelations_cfg(args):
    """
    Create a new CollectionMerger instance for merging hits relations.
    """
    bases = ["VXDBarrelHitsRelations", "ITBarrelHitsRelations", "OTBarrelHitsRelations",
             "VXDEndcapHitsRelations", "ITEndcapHitsRelations", "OTEndcapHitsRelations"]
    return CollectionMerger(
        "MergeHitsRelations",
        InputCollections = [_coned(b, args) for b in bases],
        OutputCollection = ["MergedTrackerHitsRelations"],
        OutputLevel = INFO
    )
