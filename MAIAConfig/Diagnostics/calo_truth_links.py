from GaudiKernel.Constants import INFO
from Configurables import CreateTruthLinks


def calo_truth_links_cfg():
    """
    Create a new CreateTruthLinks instance, linking calorimeter hits and Pandora
    clusters to the MCParticles that deposited their energy, as Marlin's
    RecoMCTruthLinker did. The hit links point to the digitised ("...Digi") hits;
    the cluster links are found from them by matching cell IDs.
    """
    return CreateTruthLinks(
        "CaloTruthLinker",
        cell_hit_links = [
            "EcalBarrelRelationsSimDigi", "EcalEndcapRelationsSimDigi",
            "HcalBarrelRelationsSimDigi", "HcalEndcapRelationsSimDigi",
        ],
        clusters = ["PandoraClusters"],
        mcparticles = "MCParticles",
        cell_mcparticle_links = "CalohitMCTruthLink",
        cluster_mcparticle_links = "ClusterMCTruthLink",
        OutputLevel = INFO,
    )
