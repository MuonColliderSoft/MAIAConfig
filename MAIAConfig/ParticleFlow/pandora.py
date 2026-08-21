from GaudiKernel.Constants import INFO, WARNING, DEBUG
from Configurables import DDPandoraPFANewAlgorithm, FastJetAlg

from Common.pandora_settings import resolve_pandora_settings
from Common.pandora_calibration import pandora_calibration_params

def pandoraPFA_cfg(the_args=None):
    """
    Create a new DDPandoraPFANewAlgorithm instance for Pandora PFA.

    The Pandora settings XML is located inside this package (or wherever
    --pandoraSettings / MAIA_PANDORA_SETTINGS_DIR point), so the job does not
    have to run from a directory containing a copy of PandoraSettings/.

    The theta-energy calibration payloads are located the same way (see
    Common/pandora_calibration.py) and applied by default, so a plain
    reconstruction job produces calibrated cluster and PFO energies. Pass
    --pandoraCalibration none to switch them off, or a comma-separated list of
    payload names/paths to use your own.
    """
    settings = getattr(the_args, "pandoraSettings", None) or "PandoraSettingsDefault.xml"
    calibration = pandora_calibration_params(getattr(the_args, "pandoraCalibration", None))
    return DDPandoraPFANewAlgorithm(
        "PandoraPFANew",
        CreateGaps = False,
        CurvatureToMomentumFactor =  0.00015,
        D0TrackCut =  200,
        D0UnmatchedVertexTrackCut = 5,
        DigitalMuonHits = 0,
        ECalBarrelNormalVector = [0, 0, 1],
        ECalMipThreshold = 0.5,
        ECalScMipThreshold = 0,
        ECalScToEMGeVCalibration = 1,
        ECalScToHadGeVCalibrationBarrel = 1,
        ECalScToHadGeVCalibrationEndCap = 1,
        ECalScToMipCalibration = 1,
        ECalSiMipThreshold = 0,
        ECalSiToEMGeVCalibration = 1,
        ECalSiToHadGeVCalibrationBarrel = 1,
        ECalSiToHadGeVCalibrationEndCap = 1,
        ECalSiToMipCalibration = 1,
        # The four flat GeV calibrations below define the energy basis the
        # theta-energy calibration tables are trained in. Change any of them and
        # the tables in Calibration/ have to be regenerated to match, or the
        # correction is applied in a different basis than it was measured in.
        ECalToEMGeVCalibration = 1.02373335516,
        ECalToHadGeVCalibrationBarrel = 1.371,
        ECalToHadGeVCalibrationEndCap = 1.371,
        ECalToMipCalibration = 181.818,
        EMConstantTerm = 0.01,
        EMStochasticTerm = 0.17,
        FinalEnergyDensityBin = 110.,
        HCalBarrelNormalVector = [0, 0, 1],
        HCalMipThreshold = 0.3,
        HCalToEMGeVCalibration = 1.02373335516,
        HCalToHadGeVCalibration = 0.902,
        HCalToMipCalibration = 40.8163,
        HadConstantTerm = 0.03,
        HadStochasticTerm = 0.6,
        InputEnergyCorrectionPoints = [],
        LayersFromEdgeMaxRearDistance = 250,
        MaxBarrelTrackerInnerRDistance = 200,
        MaxClusterEnergyToApplySoftComp = 2000.,
        MaxHCalHitHadronicEnergy = 1000000,
        MaxTrackHits = 5000,
        MaxTrackSigmaPOverP = 0.15,
        MinBarrelTrackerHitFractionOfExpected = 0,
        MinCleanCorrectedHitEnergy = 0.1,
        MinCleanHitEnergy = 0.5,
        MinCleanHitEnergyFraction = 0.01,
        MinFtdHitsForBarrelTrackerHitFraction = 0,
        MinFtdTrackHits = 0,
        MinMomentumForTrackHitChecks = 0,
        MinTrackECalDistanceFromIp = 0,
        MinTrackHits = 0,
        MuonBarrelBField = 0.0001,
        MuonEndCapBField = 0.0001,
        MuonHitEnergy = 0.5,
        MuonToMipCalibration = 19607.8,
        NOuterSamplingLayers = 3,
        OutputEnergyCorrectionPoints = [],
        PandoraSettingsXmlFile = resolve_pandora_settings(settings),
        ReachesECalBarrelTrackerOuterDistance = -100,
        ReachesECalBarrelTrackerZMaxDistance = -50,
        ReachesECalFtdZMaxDistance = 1,
        ReachesECalMinFtdLayer = 0,
        ReachesECalNBarrelTrackerHits = 0,
        ReachesECalNFtdHits = 0,
        ShouldFormTrackRelationships = 1,
        SoftwareCompensationEnergyDensityBins = [0, 2., 5., 7.5, 9.5, 13., 16., 20., 23.5, 28., 33., 40., 50., 75., 100.],
        SoftwareCompensationWeights = [1.61741, -0.00444385, 2.29683e-05, -0.0731236, -0.00157099, -7.09546e-07, 0.868443, 1.0561, -0.0238574],
        StartVertexAlgorithmName = "PandoraPFANew",
        StripSplittingOn = 0,
        TrackCreatorName = "DDTrackCreatorCLIC",
        TrackStateTolerance = 0,
        TrackSystemName = "DDKalTest",
        UnmatchedVertexTrackMaxEnergy = 5,
        UseEcalScLayers = 0,
        UseEcalSiLayers = 0,
        UseNonVertexTracks = 1,
        #UseOldTrackStateCalculation = 0,
        UseUnmatchedNonVertexTracks = 0,
        UseUnmatchedVertexTracks = 1,
        YokeBarrelNormalVector = [0, 0, 1],
        Z0TrackCut = 200,
        Z0UnmatchedVertexTrackCut = 5,
        ZCutForNonVertexTracks = 250,
        ClusterCollectionName = ["PandoraClusters"],
        ProngVertexCollections = [],#"ProngVertices"],
        SplitVertexCollections = [],#"SplitVertices"],
        KinkVertexCollections = [],#"KinkVertices"],
        V0VertexCollections = [],#"V0Vertices"],
        TrackCollections = ["SiTracks"],
        RelTrackCollections = [],#"MergedTrackerHitsRelations"],
        MCParticleCollections = ["MCParticles"],
        MuonCaloHitCollections = ["MuonBarrelHits", "MuonEndcapHits"],
        # ECAL/HCAL hits are coned and BIB-selected upstream (see
        # CaloDigi/calo_coning.py), so Pandora reads the "...Sel" collections.
        ECalCaloHitCollections = ["EcalBarrelCollectionSel", "EcalEndcapCollectionSel"],
        HCalCaloHitCollections = ["HcalBarrelCollectionSel", "HcalEndcapCollectionSel"],
        RelCaloHitCollections = [
            "EcalBarrelRelationsSimSel", "EcalEndcapRelationsSimSel",
            "HcalBarrelRelationsSimSel", "HcalEndcapRelationsSimSel",
            "MuonBarrelHitsRelations", "MuonEndcapHitsRelations"],
        PFOCollectionName = ["PandoraPFOs"],
        StartVertexCollectionName = ["PandoraStartVertices"],
        OutputLevel = INFO,
        # Theta-energy calibration: the Electromagnetic/HadronicThetaEnergy-
        # Correction* properties built from Calibration/*.json. Empty when
        # --pandoraCalibration none or when no payloads are installed, in which
        # case the correction plugins register with empty tables and act as the
        # identity. The plugins also have to be named in
        # PandoraSettings/PandoraSettingsDefault.xml to be called at all.
        **calibration
    )

def fastJet_cfg():
    return FastJetAlg("AntiKt FastJet",
        algorithm = ["antikt_algorithm", "0.4"],
        clusteringMode = ["Inclusive", "5"],
        jetOut = ["JetOut"],
        recParticleIn = ["PandoraPFOs"],
        recParticleOut = ["UsedPFOs"],
        recombinationScheme = "E_scheme",
        OutputLevel = INFO
    )
