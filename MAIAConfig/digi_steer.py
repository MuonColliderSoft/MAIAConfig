'''-------------------------------------------------------------'''
'''  Digitization Steering File for the Muon Collider Detector  '''
'''-------------------------------------------------------------'''
import os, sys
# Make this directory importable so the domain-folder modules (CaloDigi/,
# TrackerDigi/, Overlay/, ...) and the Common/ helpers resolve regardless of
# PYTHONPATH.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from digi_args import get_digi_args
from digiAlgList import makeDigiAlgList
from Common.steering import build_application

# Collect arguments and build the digitisation algorithm list
args = get_digi_args()
algList = makeDigiAlgList(args)

# Read the simulation output, write the digitisation output
build_application(
    args, algList,
    input_files = ["sim_output.edm4hep.root"],
    output_file = "digi_output.edm4hep.root",
    histo_file = "digi_histograms.root",
)
