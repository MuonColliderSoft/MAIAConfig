from GaudiKernel.Constants import INFO, WARNING, DEBUG
from Configurables import CollectionMerger

def _coned(name, args):
    """Append "Coned" to a collection name when tracker coning is enabled."""
    return name + "Coned" if getattr(args, "doTrackerConing", False) else name

def mergehits_cfg(args):
    """
    Create a new CollectionMerger instance for merging hits.
    """
    bases = ["VBTrackerHitsConed", "IBTrackerHitsConed", "OBTrackerHitsConed",
             "VETrackerHitsConed", "IETrackerHitsConed", "OETrackerHitsConed"]
    return CollectionMerger(
        "MergeHits",
        InputCollections = [_coned(b, args) for b in bases],
        OutputCollection = "MergedTrackerHits",
        OutputLevel = INFO
    )

def mergehitsrelations_cfg(args):
    """
    Create a new CollectionMerger instance for merging hits relations.
    """
    bases = ["VBTrackerHitsRelationsConed", "IBTrackerHitsRelationsConed", "OBTrackerHitsRelationsConed",
             "VETrackerHitsRelationsConed", "IETrackerHitsRelationsConed", "OETrackerHitsRelationsConed"]
    return CollectionMerger(
        "MergeHitsRelations",
        InputCollections = [_coned(b, args) for b in bases],
        OutputCollection = "MergedTrackerHitsRelations",
        OutputLevel = INFO
    )
