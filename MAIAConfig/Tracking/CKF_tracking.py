from GaudiKernel.Constants import INFO, WARNING, DEBUG
from Configurables import (
    ActsGeoSvc, 
    CKFTrackingAlg,
    CKFTrackingFromSeedsAlg,
    ACTSDuplicateRemoval,
    FilterTracksAlg,
    TrackTruthAlg,
    RefitFinal,
)
from Common.muc_mt import get_mt_args

def ActsGeoSvc_cfg(args):
    """Configure the ACTS GeoSvc.
    Set use_dd4hep_field=True to make ACTS use the real, position-dependent
    DD4hep field.
    """
    return ActsGeoSvc(
        "ActsGeoSvc",
        #UseDD4hepBField=args.use_dd4hep_field
    )

def CKFTracker_cfg(args):
    """
    Create a new CKFTrackingAlg instance for CKF tracking.
    """
    return CKFTrackingAlg(
        "Reconstructor",
        RunCKF = True,
        CKF_Chi2CutOff = 10,
        # Hits with chi2CutOff <= local chi2 < chi2CutOffOutlier are kept as outliers; above -> hole.
        CKF_Chi2CutOffOutlier = 25,
        # CKF branch stopper: terminate fake branches early instead of extending
        # them through the whole detector, aligned with the downstream selection
        # (>= 8 hits, <= 2 holes).
        UseBranchStopper = True,
        BranchStopper_MaxHoles = 2,
        BranchStopper_MaxOutliers = 3,
        BranchStopper_MinMeasurements = 8,
        BranchStopper_PtMin = 0.5,
        BranchStopper_PtMinMeasurements = 4,
        SeedFinding_RMax = 150,
        SeedFinding_MinPt = 500,
        SeedFinding_ImpactMax = 3,
        CKF_NumMeasurementsCutOff = 1,
        SeedFinding_SigmaScattering = 50,
        SeedFinding_CollisionRegion = 6,
        SeedFinding_RadLengthPerSeed = 0.1,
        SeedingSensorsCellIDs = ["system:1", "system:2,layer:1|2|3"],
        OutputTrackCollection = "AllTracks",
        OutputSeedCollection = "SeedTracks",
        InputTrackerHitCollection = "MergedTrackerHits",
        InputTrackerHitRelationCollection = "MergedTrackerHitsRelations",
        NumThreads = args.TrackingThreads,
        OutputLevel = INFO,
    )

def CKFFromSeeds_cfg(args):
    """
    Create a CKFTrackingFromSeedsAlg instance that runs the CKF using the track
    candidates from ExaTrkGNNTrackFinder as seeds (instead of internal seeding).
    """
    return CKFTrackingFromSeedsAlg(
        "SeededCKFReconstructor",
        CKF_Chi2CutOff = 10,
        CKF_NumMeasurementsCutOff = 1,
        MinSeedHits = 3,
        InputTrackerHitCollection = "MergedTrackerHits",
        InputSeedTrackCollection = "GNNTrackCandidates",
        OutputTrackCollection = "AllTracks",
        OutputSeedCollection = "GNNSeededTracks",
        NumThreads = get_mt_args().numThreads,
        OutputLevel = INFO,
    )


def deduper_cfg():
    """
    Create a new ACTSDuplicateRemoval instance for removing duplicate tracks.
    """
    return ACTSDuplicateRemoval(
        "Deduper",
        InputTrackCollectionName = ["AllTracks"],
        OutputTrackCollectionName = ["DedupedTracks"],
        OutputLevel = INFO
    )


def track_filter_cfg():
    """
    Create a new FilterTracksAlg instance for filtering tracks.
    """
    return FilterTracksAlg(
        "Filterer",
        InputTrackCollectionName = ["DedupedTracks"],
        MinPt = "0.5",
        MaxD0 = 10,
        MaxZ0 = 10,
        NHitsInner = "0",
        NHitsOuter = "0",
        NHitsTotal = "7",
        NHitsVertex = "0",
        MaxHoles = 2,
        OutputTrackCollectionName = ["SiTracks"],
        OutputLevel = INFO
    )

def track_truth_cfg(args):
    """
    Create a new TrackTruth instance for track truth matching.
    """
    return TrackTruthAlg(
        "TruthMatcher",
        NumThreads = args.TrackingThreads,
        InputTrackCollectionName = ["SiTracks"],
        InputTrackerHit2SimTrackerHitRelationName = ["MergedTrackerHitsRelations"],
        OutputParticle2TrackRelationName = ["SiTrackRelations"],
        OutputLevel = INFO
    )

def track_refitter_cfg():
    """
    Create a new TrackRefitter instance for refitting tracks.
    """
    return RefitFinal(
        "Refitter",
#        DoCutsOnRedChi2Nhits = True,
        EnergyLossOn = True,
        InputRelationCollectionName = ["SiTrackRelations"],
        InputTrackCollectionName = ["SiTracks"],
        Max_Chi2_Incr = 1.79769e+30,
        MinClustersOnTrackAfterFit = 3,
        MultipleScatteringOn = True,
#        NHitsCuts = ["1,2", "1", "3,4", "1", "5,6", "0"],
        OutputRelationCollectionName = ["SiTracks_Refitted_Relation"],
        OutputTrackCollectionName = ["SiTracks_Refitted"],
#        ReducedChi2Cut = 10.,
        ReferencePoint = -1,
        SmoothOn = False,
        extrapolateForward = True,
        OutputLevel = INFO
    )
