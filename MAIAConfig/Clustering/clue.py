from GaudiKernel.Constants import INFO, WARNING, DEBUG
from Configurables import ClueGaudiAlgorithmWrapper3D, CLUENtuplizer

def CLUEWrapper_cfg(the_args):
    return ClueGaudiAlgorithmWrapper3D("ClueGaudiAlgorithm",
        CaloHitsCollections = ["EcalBarrelCollectionSel",
                               "HcalBarrelCollectionSel",
                               "EcalEndcapCollectionSel",
                               "HcalEndcapCollectionSel"],
        CriticalDistance = the_args.clueCriticalDistance,
        MinLocalDensity = the_args.clueMinLocalDensity,
        FollowerDistance = the_args.clueFollowerDistance,
        SeedCriticalDistance = the_args.clueSeedCriticalDistance,
        OutputLevel = INFO,
        strategy = "MergeCollections", # "PerDetectorRegion", "PerCollection" , "MergeCollections"
        coordinate = "Polar", # "Cartesian"
        SaveClustersAsHits = True
    )

# This doesn't seem to currently work. It expects MCParticles <-> Clusters links to exist
# but I'm not sure what creates them.
def makeCLUENtuplizer(the_args = None):
    return CLUENtuplizer("CLUEAnalysis",
       OutputLevel = WARNING
    )
