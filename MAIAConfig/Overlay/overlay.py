import os
from GaudiKernel.Constants import INFO, WARNING
from Configurables import OverlayTimingRandomMix

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
# TODO: the Yoke (muon) calorimeter collections are intentionally omitted for
# now. DDSimpleMuonDigi resolves its input cellID encoding at initialize(),
# which is not available for overlay-produced collections, so the muon
# digitisers read the base Yoke* hits instead. Add YokeBarrelCollection /
# YokeEndcapCollection back here once that is resolved.
_CALO_WINDOWS = {
    "ECalBarrelCollection": [-0.5, 15.],
    "ECalEndcapCollection": [-0.5, 15.],
    "HCalBarrelCollection": [-0.5, 15.],
    "HCalEndcapCollection": [-0.5, 15.],
}

# Number of incoherent-pair events overlaid per signal event. One pair file
# holds one bunch crossing worth of pairs, so a single one is overlaid.
_IP_NUMBER_BACKGROUND = 1


def _as_directories(paths):
    """
    Map background file paths onto the directories that contain them, keeping
    the first-seen order and dropping duplicates.

    OverlayTimingRandomMix decides once, from the very first entry of
    BackgroundFileNames, whether the whole property lists files or directories,
    so the BIB directories and the incoherent-pair files cannot be mixed. The
    BIB side can only be given as directories, hence the pair files are folded
    into theirs when both overlays run together. Every .root file in that
    directory then joins the pool the pair event is drawn from.
    """
    directories = []
    for path in paths:
        directory = path if os.path.isdir(path) else os.path.dirname(os.path.abspath(path))
        if directory not in directories:
            directories.append(directory)
    return directories


def _background_groups(args):
    """
    Build the (BackgroundFileNames, NumberBackground) pair describing every
    enabled background source.

    Each group is overlaid independently, so the BIB muon-decay samples and the
    incoherent pairs simply become separate groups of the same algorithm.
    """
    ip_paths = list(args.OverlayIPBackgroundFileNames) if args.doOverlayIP else []
    # Directory mode is forced as soon as the BIB overlay contributes a group.
    if args.doOverlayFull and ip_paths:
        ip_paths = _as_directories(ip_paths)

    groups, number_background = [], []
    if args.doOverlayFull:
        groups += [[args.OverlayFullPathToMuPlus], [args.OverlayFullPathToMuMinus]]
        number_background += [args.OverlayFullNumberBackground] * 2
    if args.doOverlayIP:
        if args.doOverlayFull:
            # One group per directory: the algorithm splits a directory-valued
            # property one entry per group, so anything else would desynchronise
            # the groups from NumberBackground.
            groups += [[path] for path in ip_paths]
            number_background += [_IP_NUMBER_BACKGROUND] * len(ip_paths)
        else:
            groups.append(ip_paths)
            number_background.append(_IP_NUMBER_BACKGROUND)
    return groups, number_background


def overlay_cfg(args):
    """
    Create the overlay instance covering every enabled background source.

    Beam-induced background (--doOverlayFull) and incoherent pairs
    (--doOverlayIP) are overlaid by a single algorithm, as parallel background
    groups, rather than by two chained ones. Chaining does not work with this
    algorithm: the second instance would look its background collections up in
    the pair files under the *output* names of the first ("Overlay..."), which do
    not exist there, and it would index the signal MCParticle collection with the
    unset particle references that the first instance leaves on the background
    calorimeter contributions -- an out-of-bounds read that segfaults.

    The overlaid hits are written to the "Overlay*" collections that the
    digitisers pick up via Common.overlay_utils.overlay_input.
    """
    groups, number_background = _background_groups(args)

    return OverlayTimingRandomMix(
        "Overlay",
        BackgroundFileNames = groups,
        NumberBackground = number_background,
        TimeWindows = {**_TRACKER_WINDOWS, **_CALO_WINDOWS},
        BackgroundMCParticleCollectionName = "MCParticles",
        # The background MC particles (millions of them per event) are not kept:
        # the background hits carry their truth momentum instead of a relation.
        MergeMCParticles = False,
        # Propagate the cellID encoding metadata onto the Overlay* outputs so the
        # downstream digitisers can resolve their input collections.
        CopyCellIDMetadata = True,
        SimTrackerHits = list(_TRACKER_WINDOWS),
        SimCalorimeterHits = list(_CALO_WINDOWS),
        MCParticles = ["MCParticles"],
        OutputSimTrackerHits = ["Overlay" + name for name in _TRACKER_WINDOWS],
        OutputSimCalorimeterHits = ["Overlay" + name for name in _CALO_WINDOWS],
        OutputCaloHitContributions = [
            "Overlay" + name.replace("Collection", "ContributionCollection")
            for name in _CALO_WINDOWS],
        OutputLevel = INFO
    )
