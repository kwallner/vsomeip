# Copyright (C) 2015-2017 Bayerische Motoren Werke Aktiengesellschaft (BMW AG)
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

cmake_minimum_required (VERSION 2.8.12)
project (vsomeip)

set (VSOMEIP_MAJOR_VERSION 2)
set (VSOMEIP_MINOR_VERSION 10)
set (VSOMEIP_PATCH_VERSION 21)
set (VSOMEIP_HOTFIX_VERSION 0)

set (VSOMEIP_VERSION ${VSOMEIP_MAJOR_VERSION}.${VSOMEIP_MINOR_VERSION}.${VSOMEIP_PATCH_VERSION})
set (PACKAGE_VERSION ${VSOMEIP_VERSION}) # Used in documentatin/doxygen.in

###################################################################################################
# Use Conan.io
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

###################################################################################################
# Packages
find_package(Boost REQUIRED COMPONENTS system thread log)
find_package(Threads REQUIRED)

###################################################################################################
# Signal handling
#if (ENABLE_SIGNAL_HANDLING)
#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DVSOMEIP_ENABLE_SIGNAL_HANDLING")
#endif ()

###################################################################################################
# Options
# Yet missing
# automotive-dlt --> -DUSE_DLT
# libsystemd --> !-DWITHOUT_SYSTEMD

###################################################################################################
# Global definitions
if (${VSOMEIP_HOTFIX_VERSION} EQUAL 0)
    add_definitions(-DVSOMEIP_VERSION="${VSOMEIP_VERSION}")
else()
    add_definitions(-DVSOMEIP_VERSION="${VSOMEIP_VERSION}.${VSOMEIP_HOTFIX_VERSION}")
endif()

set(BOOST_WINDOWS_VERSION "0x600" CACHE STRING "Set the same Version as the Version with which Boost was built, otherwise there will be errors. (normaly 0x600 is for Windows 7 and 0x501 is for Windows XP)")
if (WIN32)
    add_definitions(-D_WINSOCK_DEPRECATED_NO_WARNINGS -D_WIN32_WINNT=${BOOST_WINDOWS_VERSION} -DWIN32 -DBOOST_ASIO_DISABLE_IOCP /EHsc)
endif()

###################################################################################################
# confugure internal.hpp for correct version number
configure_file (
   "${CMAKE_CURRENT_SOURCE_DIR}/implementation/configuration/include/internal.hpp.in"
   "${CMAKE_CURRENT_BINARY_DIR}/implementation/configuration/include/internal.hpp"
)

###################################################################################################
# Base library: vsomeip
file(GLOB vsomeip_SRC
    "implementation/endpoints/src/*.cpp"
    "implementation/logging/src/*.cpp"
    "implementation/tracing/src/*.cpp"
    "implementation/message/src/*.cpp"
    "implementation/routing/src/*.cpp"
    "implementation/runtime/src/*.cpp"
    "implementation/utility/src/*.cpp"
    "implementation/plugin/src/*.cpp"
)

file(GLOB_RECURSE vsomeip_e2e_SRC
    "implementation/e2e_protection/src/*.cpp"
)

list(SORT vsomeip_SRC)
list(SORT vsomeip_e2e_SRC)

add_library(vsomeip SHARED ${vsomeip_SRC} ${vsomeip_e2e_SRC})
target_include_directories(vsomeip
    PRIVATE
        $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/implementation>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/implementation>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/implementation/helper>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/implementation/configuration/include>
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/interface>
        $<INSTALL_INTERFACE:include>
    )
target_compile_definitions(vsomeip
    PRIVATE
        -DWITHOUT_SYSTEMD
    )
set_target_properties (vsomeip PROPERTIES 
    VERSION ${VSOMEIP_VERSION} 
    SOVERSION ${VSOMEIP_MAJOR_VERSION}
    )

# PRIVATE means the listed libraries won't be included in the "link interface",
# meaning the exported vsomeipTargets.cmake targets won't try to link against
# them (which shouldn't be required). ${Boost_LIBRARIES} includes absolute
# build host paths as of writing, which also makes this important as it breaks
# the build.
target_link_libraries(vsomeip 
    PUBLIC
        Boost::system Boost::thread
    PRIVATE
        #${Boost_LIBRARIES} ${USE_RT} ${DL_LIBRARY} ${DLT_LIBRARIES} ${SystemD_LIBRARIES} 
        ${CMAKE_THREAD_LIBS_INIT}
    )

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WORKMARK
#!!!!!!!!!!!!!!!!!!!!!!!
RETURN()



# Configuration library
file(GLOB vsomeip-cfg_SRC
    "implementation/configuration/src/*.cpp"
)
list(SORT vsomeip-cfg_SRC)

add_library(vsomeip-cfg SHARED ${vsomeip-cfg_SRC})
set_target_properties (vsomeip-cfg PROPERTIES VERSION ${VSOMEIP_VERSION} SOVERSION ${VSOMEIP_MAJOR_VERSION})
target_link_libraries(vsomeip-cfg vsomeip ${Boost_LIBRARIES} ${USE_RT} ${DL_LIBRARY} ${SystemD_LIBRARIES})

# Service-Discovery library
file(GLOB vsomeip-sd_SRC
    "implementation/service_discovery/src/*.cpp"
)
list(SORT vsomeip-sd_SRC)

add_library(vsomeip-sd SHARED ${vsomeip-sd_SRC})
set_target_properties (vsomeip-sd PROPERTIES VERSION ${VSOMEIP_VERSION} SOVERSION ${VSOMEIP_MAJOR_VERSION})
target_link_libraries(vsomeip-sd vsomeip ${Boost_LIBRARIES} ${USE_RT} ${DL_LIBRARY} ${SystemD_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})

if (MSVC)
    set_target_properties(vsomeip-cfg PROPERTIES COMPILE_DEFINITIONS "VSOMEIP_DLL_COMPILATION_PLUGIN")
    set_target_properties(vsomeip-sd PROPERTIES COMPILE_DEFINITIONS "VSOMEIP_DLL_COMPILATION_PLUGIN")
    set_target_properties(vsomeip PROPERTIES COMPILE_DEFINITIONS "VSOMEIP_DLL_COMPILATION")
endif()

# Configuration files

set(EXAMPLE_CONFIG_FILES
    "config/vsomeip.json"
    "config/vsomeip-local.json"
    "config/vsomeip-tcp-client.json"
    "config/vsomeip-tcp-service.json"
    "config/vsomeip-udp-client.json"
    "config/vsomeip-udp-service.json"
)

###################################################################################################
set (VSOMEIP_DIAGNOSIS_ADDRESS "0x00")
if (DIAGNOSIS_ADDRESS)
set (VSOMEIP_DIAGNOSIS_ADDRESS ${DIAGNOSIS_ADDRESS})
endif ()
set (VSOMEIP_UNICAST_ADDRESS "127.0.0.1")
if (UNICAST_ADDRESS)
set (VSOMEIP_UNICAST_ADDRESS ${UNICAST_ADDRESS})
endif ()
set (VSOMEIP_ROUTING "vsomeipd")
if (ROUTING)
set (VSOMEIP_ROUTING ${ROUTING})
endif ()
set (VSOMEIP_ROUTING_READY_MESSAGE "SOME/IP routing ready.")
if (ROUTING_READY_MESSAGE)
set (VSOMEIP_ROUTING_READY_MESSAGE ${ROUTING_READY_MESSAGE})
endif ()
message("Predefined unicast address: ${VSOMEIP_UNICAST_ADDRESS}")
message("Predefined diagnosis address: ${VSOMEIP_DIAGNOSIS_ADDRESS}")
message("Predefined routing application: ${VSOMEIP_ROUTING}")

###################################################################################################

set(INCLUDE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/interface/vsomeip")

file (GLOB_RECURSE vsomeip_INCLUDE RELATIVE ${INCLUDE_PATH} "interface/*.hpp"  )
list (SORT vsomeip_INCLUDE)

foreach ( file ${vsomeip_INCLUDE} )
    get_filename_component( dir ${file} DIRECTORY )
    install( FILES "${INCLUDE_PATH}/${file}" DESTINATION "${INSTALL_INCLUDE_DIR}/vsomeip/${dir}" COMPONENT dev)
endforeach()

install (
    TARGETS vsomeip 
    # IMPORTANT: Add the vsomeip library to the "export-set"
    EXPORT vsomeipTargets
    RUNTIME DESTINATION "${INSTALL_BIN_DIR}" COMPONENT
    LIBRARY DESTINATION "${INSTALL_LIB_DIR}" COMPONENT
    ARCHIVE DESTINATION "${INSTALL_LIB_DIR}"
    COMPONENT dev
)

install (
    TARGETS vsomeip-cfg
    LIBRARY DESTINATION "${INSTALL_LIB_DIR}" COMPONENT shlib
    RUNTIME DESTINATION "${INSTALL_BIN_DIR}" COMPONENT bin
)

install (
    TARGETS vsomeip-sd
    LIBRARY DESTINATION "${INSTALL_LIB_DIR}" COMPONENT shlib
    RUNTIME DESTINATION "${INSTALL_BIN_DIR}" COMPONENT bin
)

install (
  FILES ${EXAMPLE_CONFIG_FILES} DESTINATION etc/vsomeip COMPONENT config
)

# Add all targets to the build-tree export set
export (TARGETS vsomeip FILE "${PROJECT_BINARY_DIR}/vsomeipTargets.cmake")

# Export the package for use from the build-tree
# (this registers the build-tree with a global CMake-registry)
export (PACKAGE vsomeip)

# Create the vsomeipConfig.cmake and vsomeipConfigVersion files
file (RELATIVE_PATH REL_INCLUDE_DIR "${ABSOLUTE_INSTALL_CMAKE_DIR}" "${ABSOLUTE_INSTALL_INCLUDE_DIR}")

# ... for the build tree
set (CONF_INCLUDE_DIRS "${PROJECT_SOURCE_DIR}/interface" "${PROJECT_BINARY_DIR}")
configure_file (vsomeipConfig.cmake.in "${PROJECT_BINARY_DIR}/vsomeipConfig.cmake" @ONLY)

# ... for the install tree
set (CONF_INCLUDE_DIRS "\${VSOMEIP_CMAKE_DIR}/${REL_INCLUDE_DIR}")
configure_file (vsomeipConfig.cmake.in "${PROJECT_BINARY_DIR}${CMAKE_FILES_DIRECTORY}/vsomeipConfig.cmake" @ONLY)

# ... for both
configure_file (vsomeipConfigVersion.cmake.in "${PROJECT_BINARY_DIR}/vsomeipConfigVersion.cmake" @ONLY)


# Install the vsomeipConfig.cmake and vsomeipConfigVersion.cmake
install (
    FILES
    "${PROJECT_BINARY_DIR}${CMAKE_FILES_DIRECTORY}/vsomeipConfig.cmake"
    "${PROJECT_BINARY_DIR}/vsomeipConfigVersion.cmake"
    DESTINATION "${INSTALL_CMAKE_DIR}"
    COMPONENT dev
)

# Install the export set for use with the install-tree
install (
    EXPORT vsomeipTargets
    DESTINATION "${INSTALL_CMAKE_DIR}"
    COMPONENT dev
)

##############################################################################
# build documentation
##############################################################################
if (UNDEF)
add_custom_target(doc)

find_package(Doxygen)
if (NOT DOXYGEN_FOUND)
    message(WARNING "Doxygen is not installed. Documentation can not be built.")
else()
    # set configuration variables for doxygen.in
    set(PROJECT "vsomeip")
    set(DOCDIR documentation)
    set(SRCDIR .)
    set(GENERATE_HTML YES)
    set(GENERATE_HTMLHELP NO)
    set(GENERATE_CHI NO)
    set(GENERATE_LATEX NO)
    set(GENERATE_PDF NO)
    set(GENERATE_RTF NO)
    set(GENERATE_MAN NO)
    set(GENERATE_XML NO)
    set(HAVE_DOT YES)

    if(HAVE_DOT)
        # Note: the @DOT_PATH@ variable won't be used in doxygen.in as doxygen
        # somehow manages to strip the last slash from the path and therfore no
        # graphs are generated. Therefore dot should be available in your $PATH
        FIND_PROGRAM(DOT_PATH dot)
        if ("${DOT_PATH}" STREQUAL "DOT_PATH-NOTFOUND")
            message(WARNING "dot (graphviz) is not installed. Graphs in documentation can't be generated.")
        else()
            message("dot found")
        endif()
    endif()

    configure_file(documentation/doxygen.in ${PROJECT_BINARY_DIR}/Doxyfile @ONLY)
    add_custom_target(doxygen-doc
                      COMMAND ${DOXYGEN_EXECUTABLE} ${PROJECT_BINARY_DIR}/Doxyfile
                      SOURCES ${PROJECT_BINARY_DIR}/Doxyfile)

    add_dependencies(doc doxygen-doc)
endif()

find_program(ASCIIDOC_PATH asciidoc)
find_program(SOURCE_HIGHLIGHT_PATH source-highlight)
if ("${ASCIIDOC_PATH}" STREQUAL "ASCIIDOC_PATH-NOTFOUND")
    message(WARNING "asciidoc is not installed. Readme can not be built.")
elseif("${SOURCE_HIGHLIGHT_PATH}" STREQUAL "SOURCE_HIGHLIGHT_PATH-NOTFOUND")
    message(WARNING "source-highlight is not installed. Readme can not be built.")
else()
    message("asciidoc found")
    message("source-highlight found")
    add_custom_command(TARGET doc
                       POST_BUILD
                       COMMAND asciidoc
                               -a version=${VSOMEIP_VERSION}
                               -b html
                               -o documentation/vsomeipUserGuide.html
                               ${PROJECT_BINARY_DIR}/../documentation/vsomeipUserGuide)
endif()
endif()

##############################################################################
# create pkg-config file
if(NOT WIN32)
        configure_file(vsomeip.pc.in ${PROJECT_BINARY_DIR}/vsomeip.pc @ONLY)
        install(FILES ${PROJECT_BINARY_DIR}/vsomeip.pc DESTINATION lib/pkgconfig)
endif()

##############################################################################
# build daemon (Non-Windows only)
if (UNDEF)
if (NOT WIN32)
add_custom_target( daemon )
add_subdirectory( daemon )
endif()

# build tools
add_custom_target( tools )
add_subdirectory( tools )

# build examples
add_custom_target( examples )
add_subdirectory( examples EXCLUDE_FROM_ALL )

# build plugins located directly in the build tree
# (Non-Windows only)
if (NOT MSVC)
    if(EXISTS "${PROJECT_SOURCE_DIR}/plugins/CMakeLists.txt")
       # build plugins if available
       message("Plugins CMakeList.txt found: Build plugins")
       add_subdirectory( plugins )
    endif()
endif()
endif()

##############################################################################
# build tests
if (UNDEF)
enable_testing()
SET(TESTS_BAT "OFF" CACHE BOOL
    "Controls whether only BAT tests should be build or not")
SET(TEST_SYMLINK_CONFIG_FILES "OFF" CACHE BOOL
    "Controls if the json and scripts needed needed to run the tests are copied or symlinked into the build directroy (ignored on Windows)")
SET(TEST_SYMLINK_CONFIG_FILES_RELATIVE "OFF" CACHE BOOL
    "Controls if the json and scripts needed needed to run the tests are symlinked relatively into the build directroy (ignored on Windows)")

SET(TEST_IP_DEFAULT_VALUE "XXX.XXX.XXX.XXX")
SET(TEST_IP_MASTER "${TEST_IP_DEFAULT_VALUE}" CACHE STRING
    "The IP address of the interface which will act as test master")
SET(TEST_IP_SLAVE "${TEST_IP_DEFAULT_VALUE}" CACHE STRING
    "The IP address of the interface which will act as test slave")

if((${TEST_IP_MASTER} STREQUAL ${TEST_IP_DEFAULT_VALUE}) OR
   (${TEST_IP_SLAVE}  STREQUAL ${TEST_IP_DEFAULT_VALUE}))
    message(WARNING "TEST_IP_MASTER and/or TEST_IP_SLAVE isn't set. "
                    "Only local tests will be runnable "
                    "Please specify them via for example "
                    "-DTEST_IP_MASTER=10.0.3.1 -DTEST_IP_SLAVE=10.0.3.125")
endif()

SET(TEST_UID_DEFAULT_VALUE "123456789")
SET(TEST_UID "${TEST_UID_DEFAULT_VALUE}" CACHE STRING
    "The User ID of the user running the test: Needed for security")
SET(TEST_GID_DEFAULT_VALUE "123456789")
SET(TEST_GID "${TEST_GID_DEFAULT_VALUE}" CACHE STRING
    "The Group ID of the user running the test: Needed for security")

SET(TEST_SECURITY "ON" CACHE BOOL
    "Controls whether security tests should run or not")

if((${TEST_UID} STREQUAL ${TEST_UID_DEFAULT_VALUE}) OR
   (${TEST_GID}  STREQUAL ${TEST_GID_DEFAULT_VALUE}))
    message(WARNING "TEST_UID and/or TEST_GID isn't set. "
                    "Security Tests are not runnable "
                    "Please specify them for example "
                    "-DTEST_UID=1000 -DTEST_GID=1000")
    SET(TEST_SECURITY "OFF")
endif()

add_custom_target(build_tests)
add_dependencies(build_tests vsomeip)
add_dependencies(build_tests vsomeip-sd)

set(CMAKE_CTEST_COMMAND ctest -V)
add_custom_target(check COMMAND ${CMAKE_CTEST_COMMAND})

add_dependencies(check build_tests)
endif()

##############################################################################
# add test directory
if (UNDEF)
add_subdirectory( test EXCLUDE_FROM_ALL )
endif()
