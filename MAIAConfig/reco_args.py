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

    # Shared with digi_args: the overlay flags are declared at digitisation, but
    # the reco steering needs to know about them too so that the (very large)
    # tracker and calorimeter hit collections can be dropped from the output
    # when background is overlaid. add_argument_once keeps the combined
    # digi_reco job working.
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

    return parser.parse_known_args()[0]
