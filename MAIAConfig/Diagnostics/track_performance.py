from GaudiKernel.Constants import INFO, WARNING, DEBUG
from Configurables import TrackTruthAlg


def track_truth_cfg(args, name = "TruthMatcher", input = "SiTracks", output = "SiTrackRelations"):
    """
    Create a new TrackTruth instance for track truth matching.
    The names are parameters so a second instance can be run over the
    GNN-seeded tracks; the defaults are the standard CKF chain.
    """
    return TrackTruthAlg(
        name,
        NumThreads = args.TrackingThreads,
        InputTrackCollectionName = [input],
        InputTrackerHit2SimTrackerHitRelationName = ["MergedTrackerHitsRelations"],
        OutputParticle2TrackRelationName = [output],
        OutputLevel = INFO
    )
