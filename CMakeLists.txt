cmake_minimum_required(VERSION 3.15)
project(f1_processor CXX)

# ── Require C++17 ─────────────────────────────────────────────────────────────
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ── Find Python & pybind11 ────────────────────────────────────────────────────
# pybind11 ships its own CMake config; point CMAKE_PREFIX_PATH at the venv:
#   cmake -S . -B build -DCMAKE_PREFIX_PATH=.venv-1
find_package(pybind11 REQUIRED)

# ── Build the extension module ─────────────────────────────────────────────────
# pybind11_add_module creates a shared library with the correct Python ABI
# naming convention (e.g. f1_processor.cpython-39-darwin.so).
pybind11_add_module(f1_processor
    src/f1_processor.cpp
    src/bindings.cpp
)

target_include_directories(f1_processor PRIVATE include)
target_compile_options(f1_processor PRIVATE -O2)
