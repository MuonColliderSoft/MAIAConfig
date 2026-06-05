cmake_minimum_required(VERSION 3.15)

project(MAIAConfig LANGUAGES CXX)

include(GNUInstallDirs)
include(CTest)

if(BUILD_TESTING)
  add_subdirectory(test)
endif()

install(DIRECTORY ${CMAKE_CURRENT_LIST_DIR}/MAIAConfig/ DESTINATION ${CMAKE_INSTALL_DATADIR}/${CMAKE_PROJECT_NAME})
