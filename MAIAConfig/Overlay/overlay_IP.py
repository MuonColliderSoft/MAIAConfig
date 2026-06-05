from GaudiKernel.Constants import INFO, WARNING
# Two components named "OverlayTiming" are registered (k4Reco and k4FWCore); the
# bare "from Configurables import OverlayTiming" resolves to the k4Reco one.
# Pick the k4FWCore implementation explicitly.
from k4FWCore.k4FWCorePluginsConf import OverlayTiming

# Per-collection integration time windows for the incoherent-pair overlay
# (tracker windows are tighter than the calorimeter ones). The keys are the
# *base* collection names; they are prefixed below to match the actual input.
_TRACKER_WINDOWS = {
    "VertexBarrelCollection": [-0.18, 0.18],
    "VertexEndcapCollection": [-0.18, 0.18],
    "InnerTrackerBarrelCollection": [-0.36, 0.36],
    "InnerTrackerEndcapCollection": [-0.36, 0.36],
    "OuterTrackerBarrelCollection": [-0.36, 0.36],
    "OuterTrackerEndcapCollection": [-0.36, 0.36],
}
# Note: the Yoke (muon) collections are intentionally NOT overlaid. DDSimpleMuonDigi
# resolves its input cellID encoding at initialize(), which is not available for an
# overlay-produced collection, so the muon digitisers read the base Yoke collections.
_CALO_WINDOWS = {
    "ECalBarrelCollection": [-0.5, 15.],
    "ECalEndcapCollection": [-0.5, 15.],
    "HCalBarrelCollection": [-0.5, 15.],
    "HCalEndcapCollection": [-0.5, 15.],
}

def overlay_ip_cfg(args):
    """
    Create the incoherent-pair (IP) overlay instance.

    This is the fully Gaudi-native equivalent of the Marlin "OverlayTimingGeneric"
    processor (k4Reco Configurable ``OverlayTiming``). It is the last stage of the
    overlay chain: when BIB overlay is also enabled it reads the BIB output
    ("Overlay*") collections, otherwise it reads the raw simulation collections,
    and in both cases it writes "OverlayIP*" collections that the digitisers pick
    up via Common.overlay_utils.overlay_input.
    """
    # Input collections come from BIB (Overlay*) if it ran, else the raw sim hits.
    in_prefix = "Overlay" if args.doOverlayFull else ""

    sim_tracker_hits = [in_prefix + name for name in _TRACKER_WINDOWS]
    sim_calo_hits = [in_prefix + name for name in _CALO_WINDOWS]
    # TimeWindows keys must match the actual input collection names.
    time_windows = {in_prefix + name: win
                    for name, win in {**_TRACKER_WINDOWS, **_CALO_WINDOWS}.items()}

    out_tracker_hits = ["OverlayIP" + name for name in _TRACKER_WINDOWS]
    out_calo_hits = ["OverlayIP" + name for name in _CALO_WINDOWS]
    out_calo_contribs = ["OverlayIP" + name.replace("Collection", "ContributionCollection")
                         for name in _CALO_WINDOWS]

    return OverlayTiming(
        "OverlayIP",
        # Propagate the cellID encoding metadata onto the OverlayIP* outputs so
        # the downstream digitisers can resolve their input collections.
        CopyCellIDMetadata = True,
        AllowReusingBackgroundFiles = True,
        BackgroundFileNames = [args.OverlayIPBackgroundFileNames],
        Delta_t = 10000.0,
        NBunchtrain = 1,
        PhysicsBX = 1,
        NumberBackground = [1],
        RandomBx = False,
        TimeWindows = time_windows,
        BackgroundMCParticleCollectionName = "MCParticles",
        MCParticles = "MCParticles",
        OutputMCParticles = "MCParticlesIP",
        SimTrackerHits = sim_tracker_hits,
        SimCalorimeterHits = sim_calo_hits,
        OutputSimTrackerHits = out_tracker_hits,
        OutputSimCalorimeterHits = out_calo_hits,
        OutputCaloHitContributions = out_calo_contribs,
        OutputLevel = INFO
    )
