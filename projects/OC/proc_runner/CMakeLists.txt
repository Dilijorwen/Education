cmake_minimum_required(VERSION 3.16)
project(proc_runner LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(proc_runner STATIC
        src/proc_runner.cpp
)
target_include_directories(proc_runner PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

add_executable(proc_test
        tools/proc_test.cpp
)
target_link_libraries(proc_test PRIVATE proc_runner)