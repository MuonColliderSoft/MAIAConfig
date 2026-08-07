from Configurables import GNNTrackFinder, SortTrackerHitsAlg
from Gaudi.Configuration import VERBOSE, INFO, DEBUG

def HitSorter_cfg(args):
    """
    Create a new SortTrackerHitsAlg instance for sorting hits by radius.
    """
    return SortTrackerHitsAlg(
        "SortHitsByPhi",
        InputHitCollection=["MergedTrackerHits"],
        OutputHitCollection=["MergedTrackerHitsSortedByPhi"],
        SortBy="phi",
        Descending=False,
    )

def GNNTracker_cfg(args):
    """
    Create a new GNNTrackFinder instance for GNN tracking.
    """
    return GNNTrackFinder(
        "Reconstructor",
        #EdgeClassifierModelPath=[str(args.modelBase + "/edge_classifier-Filter.onnx"), str(args.modelBase + "/edge_classifier-InteractionGNN.onnx")],
        EdgeClassifierModelPath=[str(args.modelBase + "/edge_classifier-InteractionGNN2-v1.onnx")],
        #EdgeClassifierCut=[0.0,0.1],
        EdgeClassifierCut=[0.01],
        NodeEmbeddingModelPath=str(
            args.modelBase + "/graph_construction-MetricLearningT-v1.onnx"
        ),
        EdgeBuildingRadius=0.1,
        EdgeBuildingKnn=100.0,
        EmbeddingFixedInputLength=100,
        # InteractionGNN2 is exported at a fixed 100 nodes too, so the padding
        # rows have to survive the embedding stage and reach it. The edge
        # building still runs on the real hits alone.
        KeepEmbeddingPadding=True,
        # ... and at a fixed 2000 edges. The padding edges are self loops on a
        # padding node and are dropped again after the classification.
        EdgeClassifierFixedInputLength=2000,
        #InputFeaturesEmbedding="r,phi,z,t",
        InputFeaturesEmbedding="r,phi,eta,z,t",
        #InputScalesEmbedding="1000,3.14,1000,1",
        InputScalesEmbedding="1,1,1,1,1",
        #InputFeaturesEdgeClassifier=["r,phi,z,t,volume_id,layer_id,module_id", "r,phi,z,t"],
        #InputScalesEdgeClassifier=["1000,3.14,1000,1,7,10,500", "1000,3.14,1000,1"],
        InputFeaturesEdgeClassifier=["r,phi,eta,z,t"],
        InputScalesEdgeClassifier=["1,1,1,1,1"],
        # InteractionGNN2 has three inputs and takes the six edge features
        # (dr, dphi, dz, deta, phislope, rphislope) as its edge_attr, so they
        # have to be computed. The scales are those of r, phi, z and eta -- in
        # that order, which is *not* the order of InputFeaturesEdgeClassifier
        # above. The classifier does not scale its edge input, so these have to
        # be the scales it was trained with. Turn both off for a two-input model.
        ComputeEdgeFeatures=True,
        EdgeFeatureScales="1,1,1,1",
        PhiBins=50,
        PhiOverlap=0.1,
        TrackBuilding="cc-and-walk",
        WalkAddScore=0.6,   # follow every neighbour above this, branching if several
        WalkMinScore=0.1,   # else follow only the best, and only above this
        MinHitsPerTrack=3,
        # "cpu" or "cuda" (optionally "cuda:<index>"). The default image ships a
        # CPU-only onnxruntime, so "cuda" requires a CUDA-enabled build.
        Device=getattr(args, "device", "cpu"),
        OutputLevel=DEBUG,
        DetailedDebugOut=True, # If True this will print all inputs in full detail!
        InputHitCollections=[
            "MergedTrackerHitsSortedByPhi",
        ],
        OutputTrackCandidates=["GNNTrackCandidates"],
    )