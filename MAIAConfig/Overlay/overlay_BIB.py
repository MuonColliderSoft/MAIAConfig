from GaudiKernel.Constants import INFO, WARNING
from Configurables import OverlayTimingRandomMix

def overlay_full_cfg(args):
    """
    Create a new overlay instance with the given parameters.
    """
    # TODO: the Yoke (muon) calorimeter collections are intentionally omitted for
    # now. DDSimpleMuonDigi resolves its input cellID encoding at initialize(),
    # which is not available for overlay-produced collections, so the muon
    # digitisers read the base Yoke* hits instead. Add YokeBarrelCollection /
    # YokeEndcapCollection back to TimeWindows, SimCalorimeterHits,
    # OutputSimCalorimeterHits and OutputCaloHitContributions once that is resolved.
    return OverlayTimingRandomMix(
        "OverlayFull",
        BackgroundFileNames = [[args.OverlayFullPathToMuPlus], [args.OverlayFullPathToMuMinus]],
        TimeWindows = {
            "VertexBarrelCollection": [-0.18, 0.18],
            "VertexEndcapCollection": [-0.18, 0.18],
            "InnerTrackerBarrelCollection": [-0.36, 0.36],
            "InnerTrackerEndcapCollection": [-0.36, 0.36],
            "OuterTrackerBarrelCollection": [-0.36, 0.36],
            "OuterTrackerEndcapCollection": [-0.36, 0.36],
            "ECalBarrelCollection": [-0.5, 15.],
            "ECalEndcapCollection": [-0.5, 15.],
            "HCalBarrelCollection": [-0.5, 15.],
            "HCalEndcapCollection": [-0.5, 15.] },
        BackgroundMCParticleCollectionName = "MCParticles",
        MergeMCParticles = False,
        NumberBackground = [args.OverlayFullNumberBackground, args.OverlayFullNumberBackground],
        SimTrackerHits = [
            "VertexBarrelCollection", "VertexEndcapCollection",
            "InnerTrackerBarrelCollection", "InnerTrackerEndcapCollection",
            "OuterTrackerBarrelCollection", "OuterTrackerEndcapCollection"],
        SimCalorimeterHits = [
            "ECalBarrelCollection", "ECalEndcapCollection",
            "HCalBarrelCollection", "HCalEndcapCollection"],
        MCParticles = ["MCParticles"],
        OutputSimTrackerHits = [
            "OverlayVertexBarrelCollection", "OverlayVertexEndcapCollection",
            "OverlayInnerTrackerBarrelCollection", "OverlayInnerTrackerEndcapCollection",
            "OverlayOuterTrackerBarrelCollection", "OverlayOuterTrackerEndcapCollection"],
        OutputSimCalorimeterHits = [
            "OverlayECalBarrelCollection", "OverlayECalEndcapCollection",
            "OverlayHCalBarrelCollection", "OverlayHCalEndcapCollection"],
        OutputCaloHitContributions = [
            "OverlayECalBarrelContributionCollection", "OverlayECalEndcapContributionCollection",
            "OverlayHCalBarrelContributionCollection", "OverlayHCalEndcapContributionCollection"],
        OutputLevel = INFO
    )
