set(DETECTOR $ENV{K4GEO}/MuColl/MAIA/compact/MAIA_v0/MAIA_v0.xml)
set(MAIAConfig_DIR ${CMAKE_CURRENT_LIST_DIR}/../MAIAConfig)

# Simulate a few single-particle events to feed the digitisation/reconstruction
add_test(NAME ddsim
         WORKING_DIRECTORY ${MAIAConfig_DIR}
         COMMAND  ddsim --runType=batch -G -N=10
                  --gun.multiplicity 10
                  --gun.particle mu-
                  --gun.distribution uniform
                  --outputFile sim_output.edm4hep.root
                  --compactFile ${DETECTOR}
)

# Digitisation: reads sim_output.edm4hep.root, writes digi_output.edm4hep.root
add_test(NAME digi
         WORKING_DIRECTORY ${MAIAConfig_DIR}
         COMMAND k4run digi_steer.py --DD4hepXMLFile=${DETECTOR}
)
set_property(TEST digi APPEND PROPERTY DEPENDS ddsim)

# Reconstruction: reads digi_output.edm4hep.root, writes reco_output.edm4hep.root
add_test(NAME reco
         WORKING_DIRECTORY ${MAIAConfig_DIR}
         COMMAND k4run reco_steer.py --DD4hepXMLFile=${DETECTOR} --DetectorSchema=MAIA_v0
)
set_property(TEST reco APPEND PROPERTY DEPENDS digi)

add_test(NAME digi_help
         WORKING_DIRECTORY ${MAIAConfig_DIR}
         COMMAND k4run --help digi_steer.py
)
set_property(TEST digi_help APPEND PROPERTY PASS_REGULAR_EXPRESSION "show this help message and exit")

add_test(NAME reco_help
         WORKING_DIRECTORY ${MAIAConfig_DIR}
         COMMAND k4run --help reco_steer.py
)
set_property(TEST reco_help APPEND PROPERTY PASS_REGULAR_EXPRESSION "show this help message and exit")
