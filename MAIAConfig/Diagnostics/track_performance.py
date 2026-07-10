from GaudiKernel.Constants import INFO, WARNING, DEBUG
from Configurables import TrackTruthAlg

def trackTruth_cfg():
    """
    Create a new TrackTruthAlg instance for associating tracks with MC particles.
    """
    return TrackTruthAlg(
        "AssociationCreator",
        OutputParticle2TrackRelationName = ["MCParticle_SiTracks"],
        InputTrackCollectionName = ["SiTracks"],
        InputTrackerHit2SimTrackerHitRelationName = ["MergedTrackerHitsRelations"],
        OutputLevel = INFO
    )
