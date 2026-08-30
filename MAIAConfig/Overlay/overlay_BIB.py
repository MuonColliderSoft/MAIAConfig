from GaudiKernel.Constants import INFO, WARNING
# File-based sampling for existing one-entry-per-file BIB banks.
from Configurables import OverlayTimingRandomMix

def overlay_full_cfg(args):
    """
    Create a new overlay instance with the given parameters.
    """
    overlay_type = OverlayTimingRandomMix

    background_files = [
        [args.OverlayFullPathToMuPlus],
        [args.OverlayFullPathToMuMinus],
    ]
    number_background = [
        args.OverlayFullNumberBackground,
        args.OverlayFullNumberBackground,
    ]

    if args.OverlayBHMuonsSeparately:
        # Entry-based sampling supports multi-entry files and selecting with replacement.
        from Configurables import OverlayTimingRandomEntryMix

        overlay_type = OverlayTimingRandomEntryMix
        background_files += [
            [args.OverlayBHPathToMuPlus],
            [args.OverlayBHPathToMuMinus],
        ]
        number_background += [
            args.OverlayBHMeanDecays,
            args.OverlayBHMeanDecays,
        ]

    # TODO: the Yoke (muon) calorimeter collections are intentionally omitted for
    # now. DDSimpleMuonDigi resolves its input cellID encoding at initialize(),
    # which is not available for overlay-produced collections, so the muon
    # digitisers read the base Yoke* hits instead. Add YokeBarrelCollection /
    # YokeEndcapCollection back to TimeWindows, SimCalorimeterHits,
    # OutputSimCalorimeterHits and OutputCaloHitContributions once that is resolved.
    overlay = overlay_type(
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

    if args.OverlayBHMuonsSeparately:
        # Bulk files contain one event; packed BH files are sampled by entry.
        overlay.OneEntryPerFile = [True, True, False, False]
        overlay.Poisson_random_NOverlay = [False, False, True, True]
        overlay.AllowReusingBackgroundEntries = [False, False, True, True]

    return overlay
