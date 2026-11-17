import os
import glob
from GaudiKernel.Constants import INFO, WARNING
from Configurables import OverlayTiming

# Per-collection integration time windows. The tracker windows are tighter than
# the calorimeter ones; the same windows apply to every background source, so a
# single map covers both the BIB and the incoherent-pair overlay.
_TRACKER_WINDOWS = {
    "VertexBarrelCollection": [-0.18, 0.18],
    "VertexEndcapCollection": [-0.18, 0.18],
    "InnerTrackerBarrelCollection": [-0.36, 0.36],
    "InnerTrackerEndcapCollection": [-0.36, 0.36],
    "OuterTrackerBarrelCollection": [-0.36, 0.36],
    "OuterTrackerEndcapCollection": [-0.36, 0.36],
}

_CALO_WINDOWS = {
    "ECalBarrelCollection": [-0.5, 15.],
    "ECalEndcapCollection": [-0.5, 15.],
    "HCalBarrelCollection": [-0.5, 15.],
    "HCalEndcapCollection": [-0.5, 15.],
    "YokeBarrelCollection": [-0.5, 15.],
    "YokeEndcapCollection": [-0.5, 15.],
}

# Number of incoherent-pair events overlaid per signal event. One pair file
# holds one bunch crossing worth of pairs, so a single one is overlaid.
_IP_NUMBER_BACKGROUND = 1


def _expand_files(paths):
    """
    Expand background paths into a sorted list of ROOT files: a directory
    contributes every .root file it contains, a file is kept as is.

    With RandomMixBackgroundFiles each file of a group is an independent
    pseudo-event source, and OverlayTiming expects the files themselves (the
    directory globbing was moved out of the algorithm into the options).
    """
    files = []
    for path in paths:
        if os.path.isdir(path):
            files += sorted(glob.glob(os.path.join(path, "*.root")))
        else:
            files.append(path)
    return files


def _background_groups(args):
    """
    Build the (BackgroundFileNames, NumberBackground) pair describing every
    enabled background source.

    Each group is overlaid independently, so the BIB muon-decay samples and the
    incoherent pairs simply become separate groups of the same algorithm.
    """
    groups, number_background = [], []
    if args.doOverlayFull:
        groups += [_expand_files([args.OverlayFullPathToMuPlus]),
                   _expand_files([args.OverlayFullPathToMuMinus])]
        number_background += [args.OverlayFullNumberBackground] * 2
    if args.doOverlayIP:
        groups.append(_expand_files(args.OverlayIPBackgroundFileNames))
        number_background.append(_IP_NUMBER_BACKGROUND)
    return groups, number_background


def overlay_cfg(args):
    """
    Create the overlay instance covering every enabled background source.

    Beam-induced background (--doOverlayFull) and incoherent pairs
    (--doOverlayIP) are overlaid by a single algorithm, as parallel background
    groups.

    The overlaid hits are written to the "Overlay*" collections that the
    digitisers pick up via Common.overlay_utils.overlay_input.
    """
    groups, number_background = _background_groups(args)

    return OverlayTiming(
        "Overlay",
        # Draw one background file per overlaid event (one pseudo-event each).
        RandomMixBackgroundFiles = True,
        BackgroundFileNames = groups,
        NumberBackground = number_background,
        TimeWindows = {**_TRACKER_WINDOWS, **_CALO_WINDOWS},
        KeepAllHitContributions = False,
        BackgroundMCParticleCollectionName = "MCParticles",
        # The background MC particles (millions of them per event) are not kept:
        # the background hits carry their truth momentum instead of a relation.
        MergeMCParticles = False,
        # Propagate the cellID encoding metadata onto the Overlay* outputs so the
        # downstream digitisers can resolve their input collections.
        CopyCellIDMetadata = True,
        SimTrackerHits = list(_TRACKER_WINDOWS),
        SimCalorimeterHits = list(_CALO_WINDOWS),
        MCParticles = "MCParticles",
        OutputSimTrackerHits = ["Overlay" + name for name in _TRACKER_WINDOWS],
        OutputSimCalorimeterHits = ["Overlay" + name for name in _CALO_WINDOWS],
        OutputCaloHitContributions = [
            "Overlay" + name.replace("Collection", "ContributionCollection")
            for name in _CALO_WINDOWS],
        OutputLevel = INFO
    )
