cmake_minimum_required(VERSION 3.10)
project(MyProject)

# Get all .c, .cpp, and .c++ files recursively from the subdirectories of Code
file(GLOB_RECURSE SOURCES "${CMAKE_CURRENT_LIST_DIR}/Code/*/*.c" "${CMAKE_CURRENT_LIST_DIR}/Code/*/*.cpp" "${CMAKE_CURRENT_LIST_DIR}/Code/*/*.c++")

# Create an executable for each source file
foreach(source ${SOURCES})
    get_filename_component(name ${source} NAME_WE)  # Get file name without extension
    add_executable(${name} ${source})  # Create executable with the same name as the file
endforeach()
