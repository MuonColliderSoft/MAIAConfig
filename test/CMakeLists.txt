set(DETECTOR $ENV{K4GEO}/MuColl/MAIA/compact/MAIA_v0/MAIA_v0.xml)
set(MAIAConfig_DIR ${CMAKE_CURRENT_LIST_DIR}/../MAIAConfig)

# The realistic (charge-transport) tracker digitisation needs MuonCVXDDigitiser, which not
# every release image ships. Probe for it and leave the tests that need it out when it is absent.
execute_process(COMMAND python3 -c "from Configurables import MuonCVXDDigitiser"
                RESULT_VARIABLE realistic_digi_probe
                OUTPUT_QUIET ERROR_QUIET)
if(realistic_digi_probe STREQUAL "0")
  set(HAVE_REALISTIC_TRACKER_DIGI TRUE)
else()
  set(HAVE_REALISTIC_TRACKER_DIGI FALSE)
  message(STATUS "MuonCVXDDigitiser not available: skipping the realistic tracker digitisation tests")
endif()

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
         COMMAND k4run reco_steer.py --DD4hepXMLFile=${DETECTOR}
)
set_property(TEST reco APPEND PROPERTY DEPENDS digi)

# Realistic digitisation of every tracker subdetector, with the fired pixels stored
if(HAVE_REALISTIC_TRACKER_DIGI)
  add_test(NAME digi_realistic
           WORKING_DIRECTORY ${MAIAConfig_DIR}
           COMMAND k4run digi_steer.py --DD4hepXMLFile=${DETECTOR}
                   --doRealisticDigiVertex --doRealisticDigiInner --doRealisticDigiOuter --storeFiredPixels
                   --outputFile digi_realistic_output.edm4hep.root
  )
  set_property(TEST digi_realistic APPEND PROPERTY DEPENDS ddsim)

  add_test(NAME check_fired_pixels
           WORKING_DIRECTORY ${MAIAConfig_DIR}
           COMMAND python3 ${CMAKE_CURRENT_LIST_DIR}/check_fired_pixels.py digi_realistic_output.edm4hep.root
  )
  set_property(TEST check_fired_pixels APPEND PROPERTY DEPENDS digi_realistic)
endif()

add_test(NAME digi_help
         WORKING_DIRECTORY ${MAIAConfig_DIR}
         COMMAND k4run --help digi_steer.py
)
set_property(TEST digi_help APPEND PROPERTY PASS_REGULAR_EXPRESSION "show this help message and exit")

# The Pandora settings XML and the likelihood data it references must resolve
# from a working directory that holds no copy of PandoraSettings/.
add_test(NAME pandora_settings_path
         WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
         COMMAND ${CMAKE_COMMAND} -E env PYTHONPATH=${MAIAConfig_DIR}
                 python3 ${CMAKE_CURRENT_LIST_DIR}/check_pandora_settings.py
)

# With --pandoraCalibration on, the theta-energy plugins must be added to the
# settings XML, and the default settings must stay free of them.
add_test(NAME pandora_theta_energy_settings
         WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
         COMMAND ${CMAKE_COMMAND} -E env PYTHONPATH=${MAIAConfig_DIR}
                 python3 ${CMAKE_CURRENT_LIST_DIR}/check_pandora_theta_energy_settings.py
)

# The parametric and realistic tracker digitisers must write the collections the tracking reads.
# Without MuonCVXDDigitiser the check covers the parametric digitisers only.
add_test(NAME tracker_collection_names
         WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
         COMMAND ${CMAKE_COMMAND} -E env PYTHONPATH=${MAIAConfig_DIR}:$ENV{PYTHONPATH}
                 python3 ${CMAKE_CURRENT_LIST_DIR}/check_tracker_collections.py
)

add_test(NAME reco_help
         WORKING_DIRECTORY ${MAIAConfig_DIR}
         COMMAND k4run --help reco_steer.py
)
set_property(TEST reco_help APPEND PROPERTY PASS_REGULAR_EXPRESSION "show this help message and exit")
