from GaudiKernel.Constants import INFO, WARNING
from Configurables import OverlayTimingRandomMix

def overlay_full_cfg(args):
    """
    Create a new overlay instance with the given parameters.
    """
    background_files = [
        [args.OverlayFullPathToMuPlus],
        [args.OverlayFullPathToMuMinus],
    ]
    number_background = [
        args.OverlayFullNumberBackground,
        args.OverlayFullNumberBackground,
    ]

    if args.OverlayFullUseMuonComponent:
        # Each file groups K unrotated muon-producing decays, K ~ Poisson(4.75).
        # 4.75 = 14_218_800 * 743 / (6666 * 200 * 1667).
        background_files += [
            [args.OverlayFullMuonPathToMuPlus],
            [args.OverlayFullMuonPathToMuMinus],
        ]
        number_background += [
            args.OverlayFullNumberBackground,
            args.OverlayFullNumberBackground,
        ]

    # TODO: the Yoke (muon) calorimeter collections are intentionally omitted for
    # now. DDSimpleMuonDigi resolves its input cellID encoding at initialize(),
    # which is not available for overlay-produced collections, so the muon
    # digitisers read the base Yoke* hits instead. Add YokeBarrelCollection /
    # YokeEndcapCollection back to TimeWindows, SimCalorimeterHits,
    # OutputSimCalorimeterHits and OutputCaloHitContributions once that is resolved.
    overlay = OverlayTimingRandomMix(
        "OverlayFull",
        BackgroundFileNames = background_files,
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
        NumberBackground = number_background,
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

    return overlay
