cmake_minimum_required(VERSION 3.16)
project(temp_serial_logger LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(temp_logger
        src/logger_main.cpp

        src/core/time_utils.cpp
        src/core/rolling_agg.cpp
        src/core/exe_path.cpp

        src/db/sqlite_db.cpp
        src/db/schema.cpp
        src/db/repo.cpp

        src/http/server.cpp

        src/serial/serial_port.h
)

if (WIN32)
    target_compile_definitions(temp_logger PRIVATE _WIN32_WINNT=0x0A00 WINVER=0x0A00)
endif()

target_include_directories(temp_logger PRIVATE src third_party)

if (WIN32)
    target_sources(temp_logger PRIVATE src/serial/serial_port_win.cpp)
else()
    target_sources(temp_logger PRIVATE src/serial/serial_port_posix.cpp)
endif()


# sqlite3
find_package(SQLite3 QUIET)
if (SQLite3_FOUND)
    target_link_libraries(temp_logger PRIVATE SQLite::SQLite3)
else()
    target_link_libraries(temp_logger PRIVATE sqlite3)
endif()

if (WIN32)
    target_link_libraries(temp_logger PRIVATE ws2_32)
endif()

add_executable(temp_simulator
        src/simulator_main.cpp
        src/core/time_utils.cpp
)
target_include_directories(temp_simulator PRIVATE src)
