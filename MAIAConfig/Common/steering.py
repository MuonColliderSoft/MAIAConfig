'''-------------------------------------------------------------'''
'''  Shared steering helpers for the MAIA digi/reco macros       '''
'''-------------------------------------------------------------'''
# Centralises the service setup and ApplicationMgr wiring so that the
# individual steering files (digi_steer.py, reco_steer.py, digi_reco_steer.py)
# stay thin and free of duplicated boilerplate.


def merge_alg_lists(*alg_lists):
    """
    Concatenate several algorithm lists into one, dropping duplicate
    Configurable instances (e.g. the EventCounter shared between the digi and
    reco lists) while preserving first-seen order.
    """
    merged = []
    seen = set()
    for alg_list in alg_lists:
        for alg in alg_list:
            key = alg.getName() if hasattr(alg, "getName") else id(alg)
            if key in seen:
                continue
            seen.add(key)
            merged.append(alg)
    return merged


# EDM4hep collection types covering every flavour of tracker hit written by the
# MAIA chain: the simulated hits, both the plane-measurement (VXD/IT/OT) and the
# 3D digitised/merged hits, and the hit <-> simulated-hit links, which would
# otherwise be left pointing at collections that are no longer in the file.
TRACKER_HIT_TYPES = [
    "edm4hep::SimTrackerHitCollection",
    "edm4hep::TrackerHitPlaneCollection",
    "edm4hep::TrackerHit3DCollection",
    "podio::LinkCollection<edm4hep::TrackerHit,edm4hep::SimTrackerHit>",
]

# The calorimeter counterpart: the simulated hits together with their per-hit
# contributions, the digitised/reconstructed hits (ECal, HCal and the muon
# system, which uses the same type), and the hit <-> simulated-hit links.
CALORIMETER_HIT_TYPES = [
    "edm4hep::SimCalorimeterHitCollection",
    "edm4hep::CaloHitContributionCollection",
    "edm4hep::CalorimeterHitCollection",
    "podio::LinkCollection<edm4hep::CalorimeterHit,edm4hep::SimCalorimeterHit>",
]


def _drop_collection_types(collection_types):
    """
    Append type-based drop commands to the IOSvc keep/drop switch.

    Reading the current value back before appending keeps successive calls
    (tracker + calorimeter) from overwriting each other.
    """
    from k4FWCore import IOSvc

    io_svc = IOSvc("IOSvc")
    commands = list(getattr(io_svc, "outputCommands", [])) or ["keep *"]
    commands += ["drop type " + coll_type for coll_type in collection_types]
    io_svc.outputCommands = commands


def drop_tracker_hits():
    """
    Exclude all TrackerHit and SimTrackerHit collections (and their relation
    links) from the output file.

    Must be called after build_application, which creates the IOSvc that the
    keep/drop switch belongs to. The selection is type based, so it also
    catches the collections created downstream (merged hits) whose names are
    not known here.
    """
    _drop_collection_types(TRACKER_HIT_TYPES)


def drop_calorimeter_hits():
    """
    Exclude all CalorimeterHit and SimCalorimeterHit collections (plus the
    calorimeter contributions and relation links) from the output file.

    Same call-after-build_application requirement as drop_tracker_hits. Note
    that the Pandora clusters and PFOs are kept, but their references into the
    calorimeter hits no longer resolve once the hits are gone.
    """
    _drop_collection_types(CALORIMETER_HIT_TYPES)


def build_application(args, alg_list, input_files, output_file, histo_file, evt_max=-1):
    """
    Configure the services, IO and ApplicationMgr common to every steering
    macro and return the ApplicationMgr instance.

    Parameters:
    args         : parsed arguments namespace (must carry DD4hepXMLFile / RandSeed).
    alg_list     : ordered list of algorithm Configurables to run.
    input_files  : list of input EDM4hep files for the IOSvc.
    output_file  : output EDM4hep file for the IOSvc.
    histo_file   : ROOT file for the THistSvc histogram output.
    evt_max      : number of events to process (default -1 = every event in the input).
    """
    from GaudiKernel.Constants import WARNING
    from Common.muc_mt import get_mt_args, get_k4run_mt
    from Common.muc_services import set_services
    from k4FWCore import IOSvc, ApplicationMgr
    from k4FWCore.parseArgs import parser
    from Common.argutils import add_argument_once

    # Allow the input/output files to be chosen on the command line, falling back
    # to the per-steering defaults passed in by each macro.
    add_argument_once(parser, "--inputFiles", nargs="+", default=input_files,
                      help="Input EDM4hep file(s) to read")
    add_argument_once(parser, "--outputFile", default=output_file,
                      help="Output EDM4hep file to write")
    add_argument_once(parser, "--histoFile", default=histo_file,
                      help="Output ROOT file for the histograms")
    io_args = parser.parse_known_args()[0]
    input_files = io_args.inputFiles
    output_file = io_args.outputFile
    histo_file = io_args.histoFile

    services = []

    # Set up multi-threading if enabled
    mt_args = get_mt_args()
    event_loop_mgr = None
    if mt_args.useMT:
        whiteboard, event_loop_mgr, scheduler = get_k4run_mt(
            mt_args.numThreads, mt_args.numThreads
        )
        services += [whiteboard]

    # Set up the remaining services
    services += list(set_services(args, mt_args, histo_file))

    # Declare input and output for the IOSvc
    IOSvc(
        "IOSvc",
        Input = input_files,
        Output = output_file,
    )

    # Run the Application Manager
    app = ApplicationMgr(
        TopAlg = alg_list,
        EvtSel = "NONE",
        EvtMax = evt_max,
        ExtSvc = services,
        OutputLevel = WARNING,
    )
    if mt_args.useMT:
        app.EventLoop = event_loop_mgr
    return app
