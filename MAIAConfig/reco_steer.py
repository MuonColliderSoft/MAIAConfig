'''-------------------------------------------------------------'''
''' Reconstruction Steering File for the Muon Collider Detector '''
'''-------------------------------------------------------------'''
import os, sys
# Make this directory importable so the domain-folder modules (Tracking/,
# ParticleFlow/, ...) and the Common/ helpers resolve regardless of PYTHONPATH.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reco_args import get_reco_args
from recoAlgList import makeRecoAlgList
from Common.steering import build_application, drop_calorimeter_hits, drop_tracker_hits

# Collect arguments and build the reconstruction algorithm list
args = get_reco_args()
algList = makeRecoAlgList(args)

# Read the digitisation output, write the reconstruction output
app = build_application(
    args, algList,
    input_files = ["digi_output.edm4hep.root"],
    output_file = "reco_output.edm4hep.root",
    histo_file = "reco_histograms.root",
)

# With BIB, drop every (Sim)TrackerHit and (Sim)CalorimeterHit collection
# from the reco output. --keepEverything writes the full event.
if (args.doOverlayIP or args.doOverlayFull) and not args.keepEverything:
    drop_tracker_hits()
    drop_calorimeter_hits()

# Per-algorithm CPU monitoring via the Gaudi Auditor Service. Most meaningful
# single-threaded. Global message level raised to INFO not to be suppressed
# by the WARNING default.
from GaudiKernel.Constants import INFO
from Configurables import AuditorSvc, ChronoStatSvc
app.OutputLevel = INFO
app.AuditAlgorithms = True
app.ExtSvc += [
    AuditorSvc("AuditorSvc", Auditors = ["ChronoAuditor"]),
    ChronoStatSvc(),
]
