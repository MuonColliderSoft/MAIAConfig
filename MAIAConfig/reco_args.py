import os
from Gaudi.Configuration import *
from k4FWCore.parseArgs import parser
from Common.argutils import add_argument_once

def get_reco_args():
    """
    Parse command line arguments for the reconstruction steering.
    """
    # Shared with digi_args; added once so the two can be combined in one job.
    add_argument_once(
        parser,
        "--DD4hepXMLFile",
        help="Compact detector description file",
        type=str,
        default=os.environ.get("k4geo_DIR", "")+"/MuColl/MAIA/compact/MAIA_v0/MAIA_v0.xml",
    )

    add_argument_once(
        parser,
        "--materialMapFile",
        help="Material map file",
        type=str,
        default=os.environ.get("ACTSTRACKING_DATA") + "/k4ActsTracking/data/MAIA_v0_gen3_material_map.json",
    )

    parser.add_argument(
        "--doTrackPerf",
        help="Run Performance Analysis on Tracking",
        action="store_true",
        default=True
    )

    parser.add_argument(
        "--use_dd4hep_field",
        help="Use DD4hep field",
        action="store_true",
        default=True
    )

    parser.add_argument(
        "--TrackingThreads",
        help="Number of threads used internally by the tracking algorithms "
             "(independent of the --numThreads Gaudi event-loop setting)",
        type=int,
        default=1,
    )

    # Shared with digi_args.
    add_argument_once(
        parser,
        "--doTrackerConing",
        help="Filter tracker hits into cones around the signal MC particles (BIB cleaning)",
        action="store_true",
        default=False,
    )

    # Shared with digi_args.
    add_argument_once(
        parser,
        "--doOverlayFull",
        help="Do BIB overlay",
        action="store_true",
        default=False,
    )

    add_argument_once(
        parser,
        "--doOverlayIP",
        help="Do incoherent pairs overlay",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--keepEverything",
        help="Write every collection to the reconstruction output, including "
             "the tracker and calorimeter hits that are otherwise dropped when "
             "an overlay is enabled",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--pandoraSettings",
        help="Pandora settings XML. A bare file name is looked up in the "
             "PandoraSettings directory shipped with MAIAConfig (override it "
             "with MAIA_PANDORA_SETTINGS_DIR); an absolute or run-directory "
             "relative path is used as given",
        type=str,
        default="PandoraSettingsDefault.xml",
    )

    # CLUE args
    parser.add_argument(
        "--doCLUE",
        help="Enable CLUE clustering in addition to Pandora.",
        action="store_true"
    )

    parser.add_argument(
        "--clueCriticalDistance",
        help="Critical distance used to compute the local density in CLUE clustering",
        type=float,
        default=30,
    )

    parser.add_argument(
        "--clueMinLocalDensity",
        help="Minimum local density for a point to be promoted to a seed in CLUE clustering",
        type=float,
        default=0.1,
    )

    parser.add_argument(
        "--clueFollowerDistance",
        help="Maximum distance considered to search for followers in CLUE clustering",
        type=float,
        default=120,
    )

    parser.add_argument(
        "--clueSeedCriticalDistance",
        help="Critical distance used to promote a high density point as a seed in CLUE clustering; defaults to critical distance if set to -1.",
        type=float,
        default=-1,
    )

    # GNN CKF tracking args
    parser.add_argument(
        "--findGNNTracks",
        help="Additionally run the GNN track finder and seed a second CKF pass "
             "with its candidates, into the GNN* collections. The standard CKF "
             "chain is unaffected and keeps writing SiTracks",
        action="store_true",
        default=False,
    )

    add_argument_once(
        parser,
        "--modelBase",
        help="Path to base directory containing the GNN models",
        type=str,
        default=os.environ.get("MODEL_DIR", ""),
    )
    add_argument_once(
        parser,
        "--device",
        help="Device to run the GNN pipeline on: 'cpu' or 'cuda' (optionally 'cuda:<index>')",
        type=str,
        default="cpu",
    )

    return parser.parse_known_args()[0]
