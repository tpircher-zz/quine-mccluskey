cmake_minimum_required(VERSION 3.23)

project(qmc)

find_package(Python COMPONENTS Interpreter Development)
find_package(pybind11 CONFIG)

# Python method:
Python_add_library(_qmc src/qmc.cpp)
target_link_libraries(_qmc PRIVATE pybind11::headers)
set_target_properties(_qmc 
    PROPERTIES
    INTERPROCEDURAL_OPTIMIZATION ON
    CXX_VISIBILITY_PRESET default
    VISIBILITY_INLINES_HIDDEN ON
)