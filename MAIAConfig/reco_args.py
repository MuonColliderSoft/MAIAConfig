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
        default=os.environ.get("MUCOLL_GEO", ""),
    )

    parser.add_argument(
        "--doTrackPerf",
        help="Run Performance Analysis on Tracking",
        action="store_true",
        default=False
    )

    parser.add_argument(
        "--TrackingThreads",
        help="Number of threads for tracking",
        type=int,
        default=1,
    )

    return parser.parse_known_args()[0]
