import os
from k4FWCore.parseArgs import parser
from Common.argutils import add_argument_once

def get_digi_args():
    # Shared with reco_args; added once so the two can be combined in one job.
    add_argument_once(
        parser,
        "--DD4hepXMLFile",
        help="Compact detector description file",
        type=str,
        default=os.environ.get("k4geo_DIR", "")+"/MuColl/MAIA/compact/MAIA_v0/MAIA_v0.xml",
    )

    parser.add_argument(
        "--OverlayFullPathToMuPlus",
        help="Path to files for muplus BIB overlay",
        type=str,
        default="/path/to/muplus/",
    )

    parser.add_argument(
        "--OverlayFullPathToMuMinus",
        help="Path to files for muminus BIB overlay",
        type=str,
        default="/path/to/muminus/",
    )

    parser.add_argument(
        "--OverlayFullNumberBackground",
        help="Number of background files used for BIB overlay",
        type=int,
        default=1666, #Magic number for EU24 BIB
    )

    parser.add_argument(
        "--OverlayIPBackgroundFileNames",
        help="Path(s) to file(s) used for incoherent pairs overlay",
        type=str,
        nargs="+",
        default=["/path/to/pairs.edm4hep.root"],
    )

    parser.add_argument(
        "--doOverlayFull",
        help="Do BIB overlay",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--doOverlayIP",
        help="Do incoherent pairs overlay",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--doFilterDL",
        help="Do double-layer filtering",
        action="store_true",
        default=False,
    )

    # Shared with reco_args (the merger reads the coned hits when enabled), so
    # added once to allow combining the two parsers in a single job.
    add_argument_once(
        parser,
        "--doTrackerConing",
        help="Filter tracker hits into cones around the signal MC particles (BIB cleaning)",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--RandSeed",
        help="Random seed for digitization",
        type=int,
        default=42,
    )

    return parser.parse_known_args()[0]
