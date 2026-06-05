'''-------------------------------------------------------------------'''
''' Combined Digitization + Reconstruction Steering File (single job) '''
'''-------------------------------------------------------------------'''
# Runs digitisation and reconstruction back-to-back in a single process: the
# simulation output is read once, the intermediate digi collections are kept in
# memory, and only the reconstructed output is written. This avoids the extra
# I/O of the separate digi_steer.py -> reco_steer.py two-step workflow.
import os, sys
# Make this directory importable so the domain-folder modules and the Common/
# helpers resolve regardless of PYTHONPATH.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from digi_args import get_digi_args
from reco_args import get_reco_args
from digiAlgList import makeDigiAlgList
from recoAlgList import makeRecoAlgList
from Common.steering import build_application, merge_alg_lists

# Register the digi arguments first, then the reco arguments; the returned reco
# namespace is a superset that carries every option needed by both lists. The
# shared --DD4hepXMLFile option is registered only once (see add_argument_once).
get_digi_args()
args = get_reco_args()

# Build the combined sequence: digitisation followed by reconstruction.
# merge_alg_lists drops the EventCounter shared by the two lists.
algList = merge_alg_lists(makeDigiAlgList(args), makeRecoAlgList(args))

# Read the simulation output, write the reconstruction output
build_application(
    args, algList,
    input_files = ["sim_output.edm4hep.root"],
    output_file = "digireco_output.edm4hep.root",
    histo_file = "digireco_histograms.root",
)
