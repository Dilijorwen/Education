cmake_minimum_required(VERSION 3.16)
project(temp_gui_client LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets Network Charts)

qt_standard_project_setup()

add_executable(temp_gui_client
        src/main.cpp
        src/main_window.h
        src/main_window.cpp
        src/api_client.h
        src/api_client.cpp
)

target_link_libraries(temp_gui_client PRIVATE
        Qt6::Widgets
        Qt6::Network
        Qt6::Charts
)
