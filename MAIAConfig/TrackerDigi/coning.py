'''-------------------------------------------------------------'''
'''  Tracker hit cone filtering (BIB cleaning)                   '''
'''-------------------------------------------------------------'''
# One FilterConeHits instance per tracker subdetector. Each keeps the digitised
# hits that lie inside a cone around the trajectory of a signal MC particle,
# together with the corresponding sim hits and reco-to-sim relations, and writes
# them to "...Coned" collections. This is the Gaudi-native equivalent of the
# six FilterConeHits coners in the Marlin steer_reco.py.
from GaudiKernel.Constants import INFO
from Configurables import FilterConeHits

# (collection prefix used by the digitisers, base sim-hit collection name) for
# each subdetector. The digitiser output names come from
# tracking_{vertex,inner,outer}.py: reco hits "<prefix>Hits", relations
# "<prefix>HitsRelations".
_TRACKER_SUBDETECTORS = [
    ("VXDBarrel", "VertexBarrelCollection"),
    ("VXDEndcap", "VertexEndcapCollection"),
    ("ITBarrel", "InnerTrackerBarrelCollection"),
    ("ITEndcap", "InnerTrackerEndcapCollection"),
    ("OTBarrel", "OuterTrackerBarrelCollection"),
    ("OTEndcap", "OuterTrackerEndcapCollection"),
]


def _coner_cfg(prefix, sim_collection):
    return FilterConeHits(
        f"{prefix}Coner",
        MCParticleCollection = ["MCParticles"],
        TrackerHitInputCollections = [f"{prefix}Hits"],
        TrackerHitInputRelations = [f"{prefix}HitsRelations"],
        TrackerHitOutputCollections = [f"{prefix}HitsConed"],
        TrackerSimHitOutputCollections = [f"{sim_collection}Coned"],
        TrackerHitOutputRelations = [f"{prefix}HitsRelationsConed"],
        Dist3DCut = 30.0,
        DeltaRCut = -1.0,
        FillHistograms = False,
        OutputLevel = INFO,
    )


def tracker_coner_cfgs(args):
    """Return one FilterConeHits per tracker subdetector."""
    return [_coner_cfg(prefix, sim) for prefix, sim in _TRACKER_SUBDETECTORS]
