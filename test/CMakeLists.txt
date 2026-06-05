set(DETECTOR $ENV{K4GEO}/MuColl/MAIA/compact/MAIA_v0/MAIA_v0.xml)
set(MAIAConfig_DIR ${CMAKE_CURRENT_LIST_DIR}/../MAIAConfig)

add_test(NAME ddsim
         WORKING_DIRECTORY ${MAIAConfig_DIR}
         COMMAND  ddsim --runType=batch -G -N=10
                  --gun.multiplicity 10
                  --gun.particle mu-
                  --gun.distribution uniform
                  --compactFile ${DETECTOR}
)