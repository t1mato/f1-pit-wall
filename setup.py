"""
setup.py
─────────
Builds the f1_processor C++ extension using pybind11's setuptools helpers.

Build command (run from the project root with the venv active):
    pip install --no-build-isolation -e .

The --no-build-isolation flag tells pip to use the already-installed
pybind11 from the venv instead of creating a fresh build environment.

The resulting shared library (e.g. f1_processor.cpython-39-darwin.so)
is placed in the project root and importable as:
    import f1_processor
"""

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

ext_modules = [
    Pybind11Extension(
        "f1_processor",
        sources=["src/f1_processor.cpp", "src/bindings.cpp"],
        include_dirs=["include"],
        extra_compile_args=["-std=c++17", "-O2"],
    ),
]

setup(
    name="f1_processor",
    version="0.1",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
