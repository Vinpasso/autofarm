cmake_minimum_required(VERSION 3.16)
project(cpp)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_VERBOSE_MAKEFILE on)

option(AUTOFARM_BUILD_TESTS "Configure and build tests for libautofarm_intercept")

include(util/cmake/CPM.cmake)


# ASIO
find_package(Threads REQUIRED)

CPMAddPackage("gh:chriskohlhoff/asio#asio-1-18-1@1.18.1")

# ASIO doesn't use CMake, we have to configure it manually. Extra notes for using on Windows:
#
# 1) If _WIN32_WINNT is not set, ASIO assumes _WIN32_WINNT=0x0501, i.e. Windows XP target, which is
# definitely not the platform which most users target.
#
# 2) WIN32_LEAN_AND_MEAN is defined to make Winsock2 work.
if(asio_ADDED)
    add_library(asio INTERFACE)

    target_include_directories(asio SYSTEM INTERFACE ${asio_SOURCE_DIR}/asio/include)

    target_compile_definitions(asio INTERFACE ASIO_STANDALONE ASIO_NO_DEPRECATED)

    target_link_libraries(asio INTERFACE Threads::Threads)

    if(WIN32)
        # macro see @ https://stackoverflow.com/a/40217291/1746503
        macro(get_win32_winnt version)
            if(CMAKE_SYSTEM_VERSION)
                set(ver ${CMAKE_SYSTEM_VERSION})
                string(REGEX MATCH "^([0-9]+).([0-9])" ver ${ver})
                string(REGEX MATCH "^([0-9]+)" verMajor ${ver})
                # Check for Windows 10, b/c we'll need to convert to hex 'A'.
                if("${verMajor}" MATCHES "10")
                    set(verMajor "A")
                    string(REGEX REPLACE "^([0-9]+)" ${verMajor} ver ${ver})
                endif("${verMajor}" MATCHES "10")
                # Remove all remaining '.' characters.
                string(REPLACE "." "" ver ${ver})
                # Prepend each digit with a zero.
                string(REGEX REPLACE "([0-9A-Z])" "0\\1" ver ${ver})
                set(${version} "0x${ver}")
            endif()
        endmacro()

        if(NOT DEFINED _WIN32_WINNT)
            get_win32_winnt(ver)
            set(_WIN32_WINNT ${ver})
        endif()

        message(STATUS "Set _WIN32_WINNET=${_WIN32_WINNT}")

        target_compile_definitions(asio INTERFACE _WIN32_WINNT=${_WIN32_WINNT} WIN32_LEAN_AND_MEAN)
    endif()
endif()

# JSON
CPMAddPackage("gh:nlohmann/json@3.10.5")


# libautofarm_intercept
add_library(autofarm_intercept SHARED
            src/exec_intercept.h src/exec_intercept.cpp
            src/Client.h src/Client.cpp
            src/ExecInvocationParam.h src/ExecInvocationParam.cpp)

target_link_libraries(autofarm_intercept asio nlohmann_json::nlohmann_json ${CMAKE_DL_LIBS})

# Tests
if(AUTOFARM_BUILD_TESTS)
    enable_testing()

    CPMAddPackage(
            NAME googletest
            GITHUB_REPOSITORY google/googletest
            GIT_TAG release-1.11.0
            VERSION 1.11.0
            OPTIONS "INSTALL_GTEST OFF" "gtest_force_shared_crt"
    )

    # Dont link libautofarm_intercept. We want to test preload functionality.
    add_executable(autofarm_intercept_test_invoke_exec test/invokeExec.cpp)

    add_executable(autofarm_intercept_test
            test/test_ExecInvocationParam.cpp
            test/test_Intercept.cpp)
    target_link_libraries(autofarm_intercept_test autofarm_intercept gtest gtest_main gmock asio)
    add_dependencies(autofarm_intercept_test autofarm_intercept_test_invoke_exec)

    include(GoogleTest)
    gtest_discover_tests(autofarm_intercept_test)
endif()
