from Configurables import ExaTrkGNNTrackFinder
from Gaudi.Configuration import VERBOSE, INFO, DEBUG

def GNNTracker_cfg(args):
    """
    Create a new ExaTrkGNNTrackFinder instance for GNN tracking.
    """
    return ExaTrkGNNTrackFinder(
        "Reconstructor",
        EdgeClassifierModelPath=str(args.modelBase + "/edge_classifier-InteractionGNN.onnx"),
        EdgeClassifierCut=0.5,
        NodeEmbeddingModelPath=str(
            args.modelBase + "/graph_construction-MetricLearning.onnx"
        ),
        EdgeBuildingRadius=0.1,
        EdgeBuildingKnn=100.0,
        EmbeddingDim=4,
        MinHitsPerTrack=3,
        # "cpu" or "cuda" (optionally "cuda:<index>"). The default image ships a
        # CPU-only onnxruntime, so "cuda" requires a CUDA-enabled build.
        Device=getattr(args, "device", "cpu"),
        OutputLevel=DEBUG,
        InputHitCollections=[
            "MergedTrackerHits",
        ],
    )
