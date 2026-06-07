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


def build_application(args, alg_list, input_files, output_file, histo_file, evt_max=10):
    """
    Configure the services, IO and ApplicationMgr common to every steering
    macro and return the ApplicationMgr instance.

    Parameters:
    args         : parsed arguments namespace (must carry DD4hepXMLFile / RandSeed).
    alg_list     : ordered list of algorithm Configurables to run.
    input_files  : list of input EDM4hep files for the IOSvc.
    output_file  : output EDM4hep file for the IOSvc.
    histo_file   : ROOT file for the THistSvc histogram output.
    evt_max      : number of events to process (default 10).
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
