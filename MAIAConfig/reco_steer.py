'''-------------------------------------------------------------'''
''' Reconstruction Steering File for the Muon Collider Detector '''
'''-------------------------------------------------------------'''
import os, sys
# Make this directory importable so the domain-folder modules (Tracking/,
# ParticleFlow/, ...) and the Common/ helpers resolve regardless of PYTHONPATH.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reco_args import get_reco_args
from recoAlgList import makeRecoAlgList
from Common.steering import build_application

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

# Per-algorithm CPU monitoring via the Gaudi Auditor Service. The ChronoAuditor
# records CPU usage of each algorithm's execute() and ChronoStatSvc prints the
# per-algorithm total + per-event-average table ("Final CPU consumption") at end
# of job. Most meaningful single-threaded.
#
# The global message level is raised to INFO so the ChronoStatSvc table (emitted
# under the "*****Chrono*****" / "<Alg>:Execute" message sources) is not
# suppressed by the WARNING default that build_application sets.
from GaudiKernel.Constants import INFO
from Configurables import AuditorSvc, ChronoStatSvc
app.OutputLevel = INFO
app.AuditAlgorithms = True
app.ExtSvc += [
    AuditorSvc("AuditorSvc", Auditors = ["ChronoAuditor"]),
    ChronoStatSvc(),
]
