def choose_parallelism():
    """Set number of threads based CPU count"""
    import os

    cpu_count = os.cpu_count()
    if cpu_count is None:
        return 1
    else:
        return cpu_count

def get_mt_args():
    """Parse command line arguments for multi-threading configuration.

    A single knob, --numThreads, controls everything: 1 (the default) runs the
    serial event loop, any value > 1 enables the multi-threaded Gaudi Hive event
    loop with that many threads, and 0 auto-detects a sensible thread count from
    the CPU count. The convenience flag ``useMT`` is derived from it. Registered
    with add_argument_once so this can be called from several places (e.g. the
    tracking config also reads --numThreads) without argparse complaining about
    duplicate options.
    """
    from k4FWCore.parseArgs import parser
    from Common.argutils import add_argument_once

    add_argument_once(
        parser,
        "--numThreads",
        help="Number of threads to use; 1 runs serially, > 1 enables multi-threading, "
             "0 auto-detects from the CPU count",
        type=int,
        default=1,
    )

    mt_args = parser.parse_known_args()[0]
    if mt_args.numThreads == 0:
        mt_args.numThreads = choose_parallelism()
    mt_args.useMT = mt_args.numThreads > 1
    return mt_args

def get_k4run_mt(threads, event_slots):
    """Create a k4run instance configured for multi-threading."""
    from Gaudi.Configuration import INFO, WARNING
    from Configurables import HiveSlimEventLoopMgr, HiveWhiteBoard, AvalancheSchedulerSvc

    wb = HiveWhiteBoard(
        "EventDataSvc",
        EventSlots=event_slots,
    )
    elm = HiveSlimEventLoopMgr(
        "HiveSlimEventLoopMgr",
        SchedulerName = "AvalancheSchedulerSvc",
        OutputLevel = WARNING,
    )
    sch = AvalancheSchedulerSvc(
        ThreadPoolSize = threads,
        ShowDataFlow = True,
        OutputLevel = WARNING,
    )

    return wb, elm, sch
