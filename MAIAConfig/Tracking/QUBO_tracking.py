from GaudiKernel.Constants import INFO, WARNING, DEBUG
from Configurables import (
    CKFTrackingFromSeedsAlg,
    ACTSDuplicateRemoval,
    FilterTracksAlg,
    TrackTruthAlg,
)
from Common.muc_mt import get_mt_args

def CKFFromSeeds_QUBO_cfg(args):
    """
    Create a CKFTrackingFromSeedsAlg instance that runs the CKF using the track
    candidates from ExaTrkGNNTrackFinder as seeds (instead of internal seeding).
    """
    return CKFTrackingFromSeedsAlg(
        "SeededQUBOReconstructor",
        CKF_Chi2CutOff = 10,
        CKF_NumMeasurementsCutOff = 1,
        MinSeedHits = 3,
        InputTrackerHitCollection = "MergedTrackerHits",
        InputSeedTrackCollection = "MultipletTracks_gurobi",
        OutputTrackCollection = "QUBOTracks",
        OutputSeedCollection = "QUBOSeededTracks",
        NumThreads = args.TrackingThreads,
        OutputLevel = INFO,
    )

def deduper_QUBO_cfg():
    """
    Create a new ACTSDuplicateRemoval instance for removing duplicate tracks.
    """
    return ACTSDuplicateRemoval(
        "Deduper_QUBO",
        InputTrackCollectionName = ["QUBOTracks"],
        OutputTrackCollectionName = ["QUBODedupedTracks"],
        OutputLevel = INFO
    )

def track_filter_QUBO_cfg():
    """
    Create a new FilterTracksAlg instance for filtering tracks.
    """
    return FilterTracksAlg(
        "Filterer_QUBO",
        InputTrackCollectionName = ["QUBODedupedTracks"],
        MinPt = "0.5",
        MaxD0 = 10,
        MaxZ0 = 10,
        NHitsInner = "0",
        NHitsOuter = "0",
        NHitsTotal = "0",
        NHitsVertex = "0",
        OutputTrackCollectionName = ["QUBOSelectedTracks"],
        OutputLevel = INFO
    )

def track_truth_QUBO_cfg(args):
    """
    Create a new TrackTruth instance for track truth matching.
    """
    return TrackTruthAlg(
        "TruthMatcher_QUBO",
        NumThreads = args.TrackingThreads,
        InputTrackCollectionName = ["QUBOSelectedTracks"],
        InputTrackerHit2SimTrackerHitRelationName = ["MergedTrackerHitsRelations"],
        OutputParticle2TrackRelationName = ["QUBOTrackRelations"],
        OutputLevel = INFO
    )

def CKFFromSeeds_DWAVE_cfg(args):
    """
    Create a CKFTrackingFromSeedsAlg instance that runs the CKF using the track
    candidates from ExaTrkGNNTrackFinder as seeds (instead of internal seeding).
    """
    return CKFTrackingFromSeedsAlg(
        "SeededDWAVEReconstructor",
        CKF_Chi2CutOff = 10,
        CKF_NumMeasurementsCutOff = 1,
        MinSeedHits = 3,
        InputTrackerHitCollection = "MergedTrackerHits",
        InputSeedTrackCollection = "MultipletTracks_dwave",
        OutputTrackCollection = "DWAVETracks",
        OutputSeedCollection = "DWAVESeededTracks",
        NumThreads = args.TrackingThreads,
        OutputLevel = INFO,
    )

def deduper_DWAVE_cfg():
    """
    Create a new ACTSDuplicateRemoval instance for removing duplicate tracks.
    """
    return ACTSDuplicateRemoval(
        "Deduper_DWAVE",
        InputTrackCollectionName = ["DWAVETracks"],
        OutputTrackCollectionName = ["DWAVEDedupedTracks"],
        OutputLevel = INFO
    )

def track_filter_DWAVE_cfg():
    """
    Create a new FilterTracksAlg instance for filtering tracks.
    """
    return FilterTracksAlg(
        "Filterer_DWAVE",
        InputTrackCollectionName = ["DWAVEDedupedTracks"],
        MinPt = "0.5",
        MaxD0 = 10,
        MaxZ0 = 10,
        NHitsInner = "0",
        NHitsOuter = "0",
        NHitsTotal = "0",
        NHitsVertex = "0",
        OutputTrackCollectionName = ["DWAVESelectedTracks"],
        OutputLevel = INFO
    )

def track_truth_DWAVE_cfg(args):
    """
    Create a new TrackTruth instance for track truth matching.
    """
    return TrackTruthAlg(
        "TruthMatcher_DWAVE",
        NumThreads = args.TrackingThreads,
        InputTrackCollectionName = ["DWAVESelectedTracks"],
        InputTrackerHit2SimTrackerHitRelationName = ["MergedTrackerHitsRelations"],
        OutputParticle2TrackRelationName = ["DWAVETrackRelations"],
        OutputLevel = INFO
    )


def CKFFromSeeds_BRUTE_cfg(args):
    """
    Create a CKFTrackingFromSeedsAlg instance that runs the CKF using the track
    candidates from ExaTrkGNNTrackFinder as seeds (instead of internal seeding).
    """
    return CKFTrackingFromSeedsAlg(
        "SeededBRUTEReconstructor",
        CKF_Chi2CutOff = 10,
        CKF_NumMeasurementsCutOff = 1,
        MinSeedHits = 3,
        InputTrackerHitCollection = "MergedTrackerHits",
        InputSeedTrackCollection = "MultipletTracks_bruteforce",
        OutputTrackCollection = "BRUTETracks",
        OutputSeedCollection = "BRUTESeededTracks",
        NumThreads = args.TrackingThreads,
        OutputLevel = INFO,
    )

def deduper_BRUTE_cfg():
    """
    Create a new ACTSDuplicateRemoval instance for removing duplicate tracks.
    """
    return ACTSDuplicateRemoval(
        "Deduper_BRUTE",
        InputTrackCollectionName = ["BRUTETracks"],
        OutputTrackCollectionName = ["BRUTEDedupedTracks"],
        OutputLevel = INFO
    )

def track_filter_BRUTE_cfg():
    """
    Create a new FilterTracksAlg instance for filtering tracks.
    """
    return FilterTracksAlg(
        "Filterer_BRUTE",
        InputTrackCollectionName = ["BRUTEDedupedTracks"],
        MinPt = "0.5",
        MaxD0 = 10,
        MaxZ0 = 10,
        NHitsInner = "0",
        NHitsOuter = "0",
        NHitsTotal = "0",
        NHitsVertex = "0",
        OutputTrackCollectionName = ["BRUTESelectedTracks"],
        OutputLevel = INFO
    )

def track_truth_BRUTE_cfg(args):
    """
    Create a new TrackTruth instance for track truth matching.
    """
    return TrackTruthAlg(
        "TruthMatcher_BRUTE",
        NumThreads = args.TrackingThreads,
        InputTrackCollectionName = ["BRUTESelectedTracks"],
        InputTrackerHit2SimTrackerHitRelationName = ["MergedTrackerHitsRelations"],
        OutputParticle2TrackRelationName = ["BRUTETtrackRelations"],
        OutputLevel = INFO
    )