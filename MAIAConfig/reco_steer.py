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

# Collections to drop from the reconstruction output. IOSvc applies the commands
# in order, so keep everything first and then drop the unwanted entries.
#
# By type: podio collection type (getTypeName(), note the trailing "Collection").
# Type matching is exact (no wildcards).
drop_types = [
    "edm4hep::CalorimeterHitCollection",
    "edm4hep::ReconstructedParticleCollection",
    "podio::LinkCollection<edm4hep::Vertex,edm4hep::ReconstructedParticle>",
    "edm4hep::ClusterCollection",
    "edm4hep::VertexCollection",
]
# By name: specific collections (name matching supports '*'/'?' wildcards).
drop_names = [
    "MCParticle_SelectedTracks",
    "MCParticle_SiTracks",
    "SelectedTracks",
    "SelectedTracks_dQdx",
    "SiTracks",
    "SiTracks_dQdx",
    "SiTracksPreFit",
]
output_commands = (
    ["keep *"]
    + [f"drop type {t}" for t in drop_types]
    + [f"drop {n}" for n in drop_names]
)

# Read the digitisation output, write the reconstruction output
build_application(
    args, algList,
    input_files = ["digi_output.edm4hep.root"],
    output_file = "reco_output.edm4hep.root",
    histo_file = "reco_histograms.root",
    output_commands = output_commands,
)
