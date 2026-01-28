cmake_minimum_required(VERSION 3.16)
project(temp_serial_logger LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(temp_logger
        src/logger_main.cpp
        src/core/csv_log.cpp
        src/core/time_utils.cpp
        src/core/rolling_agg.cpp
        src/core/exe_path.cpp
        src/serial/serial_port_win.cpp
)

add_executable(temp_simulator
        src/simulator_main.cpp
        src/core/time_utils.cpp
)

target_include_directories(temp_logger PRIVATE src)
target_include_directories(temp_simulator PRIVATE src)

if (WIN32)
    target_sources(temp_logger PRIVATE src/serial/serial_port_win.cpp)
else()
    target_sources(temp_logger PRIVATE src/serial/serial_port_posix.cpp)
endif()
