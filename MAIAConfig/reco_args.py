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

    parser.add_argument(
        "--doTrackPerf",
        help="Run Performance Analysis on Tracking",
        action="store_true",
        default=False
    )

    # Shared with digi_args: the digi step produces the "...Coned" collections
    # and the merger here must read them. add_argument_once allows the two
    # parsers to coexist in the combined digi_reco job.
    add_argument_once(
        parser,
        "--doTrackerConing",
        help="Filter tracker hits into cones around the signal MC particles (BIB cleaning)",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--TrackingThreads",
        help="Number of threads for tracking",
        type=int,
        default=1,
    )

    return parser.parse_known_args()[0]
