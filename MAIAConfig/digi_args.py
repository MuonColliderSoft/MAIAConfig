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
        "--OverlayFullMuonPathToMuPlus",
        help="Path to muplus BIB decays containing muons",
        type=str,
        default="/path/to/muplus/muon/",
    )

    parser.add_argument(
        "--OverlayFullMuonPathToMuMinus",
        help="Path to muminus BIB decays containing muons",
        type=str,
        default="/path/to/muminus/muon/",
    )

    parser.add_argument(
        "--OverlayFullNumberBackground",
        help="Number of background files used for BIB overlay",
        type=int,
        default=1667, #Magic number for EU24 BIB
    )

    parser.add_argument(
        "--OverlayFullMuonNumberBackground",
        help="Poisson mean for each BIB muon-component stream",
        type=float,
        default=None, #7924.2 for a full BX: 14,218,800 * 743 / (6666 * 200)
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
        "--OverlayFullUseMuonComponent",
        help="Add separately sampled BIB decays containing muons",
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

    # Shared with reco_args (the merger reads the coned hits when enabled).
    add_argument_once(
        parser,
        "--doTrackerConing",
        help="Filter tracker hits into cones around the signal MC particles (BIB cleaning)",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--doCaloConing",
        help="Filter calorimeter hits into cones around the signal MC particles "
             "before the BIB hit selection",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--caloConeWidth",
        help="Half-opening angle [rad] of the calorimeter cones (used with "
             "--doCaloConing)",
        type=float,
        default=0.6,
    )

    parser.add_argument(
        "--RandSeed",
        help="Random seed for digitization",
        type=int,
        default=42,
    )

    args = parser.parse_known_args()[0]

    if args.OverlayFullUseMuonComponent:
        if args.OverlayFullMuonNumberBackground is None:
            parser.error("--OverlayFullMuonNumberBackground is required")
        if args.OverlayFullMuonNumberBackground <= 0:
            parser.error("--OverlayFullMuonNumberBackground must be positive")

    return args
