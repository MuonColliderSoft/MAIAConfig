from GaudiKernel.Constants import INFO, WARNING
# Two components named "OverlayTiming" are registered (k4Reco and k4FWCore); the
# bare "from Configurables import OverlayTiming" resolves to the k4Reco one.
# Pick the k4FWCore implementation explicitly.
from k4FWCore.k4FWCorePluginsConf import OverlayTiming
# Shared with the digitisers, which resolve their inputs through
# Common.overlay_utils.overlay_input.
from Common.overlay_utils import OUTPUT_PREFIX

# Per-collection integration time windows [t_min, t_max] in ns. The tracker
# windows are tighter than the calorimeter ones. Every SimTrackerHit and
# SimCalorimeterHit collection handed to OverlayTiming needs an entry here.
_TRACKER_WINDOWS = {
    "VertexBarrelCollection": [-0.18, 0.18],
    "VertexEndcapCollection": [-0.18, 0.18],
    "InnerTrackerBarrelCollection": [-0.36, 0.36],
    "InnerTrackerEndcapCollection": [-0.36, 0.36],
    "OuterTrackerBarrelCollection": [-0.36, 0.36],
    "OuterTrackerEndcapCollection": [-0.36, 0.36],
}
# TODO: the Yoke (muon) calorimeter collections are intentionally omitted. See
# the note on CopyCellIDMetadata below; once the muon digitisers can resolve
# their cellID encoding from an overlay-produced collection, add
# YokeBarrelCollection / YokeEndcapCollection here and drop the special case in
# CaloDigi/calorimetry_MU.py.
_CALO_WINDOWS = {
    "ECalBarrelCollection": [-0.5, 15.],
    "ECalEndcapCollection": [-0.5, 15.],
    "HCalBarrelCollection": [-0.5, 15.],
    "HCalEndcapCollection": [-0.5, 15.],
}

def _background_groups(args):
    """
    Assemble the enabled background streams.

    OverlayTiming takes a *list of groups*: BackgroundFileNames, NumberBackground
    and Poisson_random_NOverlay are all indexed by group, and each group is drawn
    from independently. That is what lets the beam-induced background and the
    incoherent pairs be overlaid by a single algorithm instead of being chained.

    Returns (file_names, number_background), both indexed by group.
    """
    file_names, number_background = [], []

    if args.doOverlayFull:
        # One group per beam. The entries are directories; OverlayTiming collects
        # their .root files itself.
        file_names += [[args.OverlayFullPathToMuPlus], [args.OverlayFullPathToMuMinus]]
        number_background += [args.OverlayFullNumberBackground] * 2

    if args.doOverlayIP:
        # A single pair pseudo-event per signal event.
        file_names.append(list(args.OverlayIPBackgroundFileNames))
        number_background.append(1)

    return file_names, number_background


def overlay_cfg(args):
    """
    Create the overlay instance for whichever backgrounds are enabled.

    Both the beam-induced background (--doOverlayFull) and the incoherent pairs
    (--doOverlayIP) are overlaid by *one* OverlayTiming reading the raw simulation
    collections, as two extra background groups rather than two algorithms in
    series.

    Chaining a second OverlayTiming behind the first cannot work: the algorithm
    looks its background collections up by its own *input* names
    (backgroundEvent.get(inputLocations(...)[i])), so a second pass reading the
    "Overlay*" collections would search the pair file for "OverlayVertexBarrelCollection"
    and find nothing. Overlaying everything in one pass also avoids re-reading the
    first pass' output.
    """
    file_names, number_background = _background_groups(args)
    if not file_names:
        raise ValueError("overlay_cfg called with neither --doOverlayFull nor --doOverlayIP")

    sim_tracker_hits = list(_TRACKER_WINDOWS)
    sim_calo_hits = list(_CALO_WINDOWS)

    out_tracker_hits = [OUTPUT_PREFIX + name for name in sim_tracker_hits]
    out_calo_hits = [OUTPUT_PREFIX + name for name in sim_calo_hits]
    out_calo_contribs = [OUTPUT_PREFIX + name.replace("Collection", "ContributionCollection")
                         for name in sim_calo_hits]

    return OverlayTiming(
        "Overlay",
        # --- background streams, one group per beam and one for the pairs ---
        BackgroundFileNames = file_names,
        NumberBackground = number_background,
        # The BIB is split over thousands of files holding a single pseudo-event
        # each, so every file is treated as an independent event source and a
        # random set is drawn per event. The pair group is normally a single file,
        # which random mixing walks entry by entry just as a sequential read would.
        RandomMixBackgroundFiles = True,
        # Required with the above: one pseudo-event per file means a random draw
        # picks the same file again long before the input is exhausted, and the
        # job would otherwise abort with "No more events in background file".
        AllowReusingBackgroundFiles = True,
        # Reading and decompressing the background dominates the runtime; with > 1
        # the files of one event are read on several worker threads. The randomness
        # is drawn up front and the merge stays serial and in order, so the result
        # does not depend on this value.
        OverlayThreads = args.OverlayThreads,

        # --- single bunch crossing ---
        # Everything is overlaid onto the one crossing that holds the physics
        # event, so no time offsets are applied and Delta_t never comes into play.
        NBunchtrain = 1,
        PhysicsBX = 1,
        RandomBx = False,

        # --- collections ---
        TimeWindows = {**_TRACKER_WINDOWS, **_CALO_WINDOWS},
        SimTrackerHits = sim_tracker_hits,
        SimCalorimeterHits = sim_calo_hits,
        OutputSimTrackerHits = out_tracker_hits,
        OutputSimCalorimeterHits = out_calo_hits,
        OutputCaloHitContributions = out_calo_contribs,
        # Propagate the cellID encoding metadata onto the Overlay* outputs so the
        # downstream digitisers can resolve their input collections.
        CopyCellIDMetadata = True,

        # --- MC particles ---
        BackgroundMCParticleCollectionName = "MCParticles",
        MCParticles = "MCParticles",
        # The background particles are not kept: tracker hits carry the momentum of
        # their originating particle instead of a link and calorimeter contributions
        # get an empty particle, so only the signal particles reach the output.
        MergeMCParticles = False,
        OutputMCParticles = "MCParticlesOverlay",

        OutputLevel = INFO
    )
