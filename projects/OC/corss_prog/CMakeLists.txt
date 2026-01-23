cmake_minimum_required(VERSION 3.16)
project(prog_counter LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(program src/program.cpp)

if (WIN32)
    target_compile_definitions(program PRIVATE NOMINMAX)
else()
    find_package(Threads REQUIRED)
    target_link_libraries(program PRIVATE Threads::Threads)
endif()


set_target_properties(program PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)
