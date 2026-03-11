/**
 * src/bindings.cpp
 * ─────────────────
 * pybind11 glue layer: exposes the C++ lerp_position() to Python.
 *
 * pybind11 handles all C Python API boilerplate — reference counting,
 * type conversion, exception translation — so we only write the logic.
 *
 * Key pybind11 types used here:
 *   py::array_t<double>   — accepts a NumPy ndarray of float64 from Python.
 *   .unchecked<1>()       — zero-copy 1-D view; gives direct pointer access.
 *   .data(0)              — raw C pointer to element 0 of the array buffer.
 *   .shape(0)             — number of elements in dimension 0.
 *   py::make_tuple(a, b)  — constructs a Python tuple from C++ values.
 */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include "f1_processor.h"

namespace py = pybind11;

/**
 * lerp_position_py
 * ─────────────────
 * Python-facing wrapper around the C++ lerp_position().
 * Converts NumPy arrays to raw C pointers and packages the result
 * as a Python tuple (x, y).
 */
py::tuple lerp_position_py(
    double              time_s,
    py::array_t<double> times,
    py::array_t<double> xs, // tells pybind11 to expect a NumPy array containing 64-bit floats 
    py::array_t<double> ys
) {
    // TODO(human): implement this function body.
    //
    // 1. Get unchecked 1-D views of each array (zero-copy, no bounds checking):
    //       auto t = times.unchecked<1>();
    //       auto x = xs.unchecked<1>();
    //       auto y = ys.unchecked<1>();
    //
    // 2. Declare output variables:
    //       double out_x, out_y;
    //
    // 3. Call lerp_position() with raw pointers and array length:
    //       lerp_position(time_s, t.data(0), x.data(0), y.data(0),
    //                     (std::size_t)t.shape(0), &out_x, &out_y);
    //
    // 4. Return as a Python tuple:
    //       return py::make_tuple(out_x, out_y);

    auto t = times.unchecked<1>(); // creates 1-dimensional "view" of the NumPy array. .unchecked() = disables bounds-checking for max speed
    auto x = xs.unchecked<1>(); // 
    auto y = ys.unchecked<1>();

    double out_x, out_y;

    // .data(0) reaches directly into Python NumPy array and grabs raw C-memory pointer to very first element
    // passes raw pointer directly to C++ math function, zero data copied
    lerp_position(time_s, t.data(0), x.data(0), y.data(0), (std::size_t)t.shape(0), &out_x, &out_y);

    return py::make_tuple(out_x, out_y); // takes C++ double answers, bundles into Python tuple, returns to Python interpreter
}

PYBIND11_MODULE(f1_processor, m) {
    m.doc() = "C++ accelerated F1 telemetry interpolation";

    m.def(
        "lerp_position",
        &lerp_position_py,
        "Binary search + linear interpolation for one driver's (x, y) at time_s.",
        py::arg("time_s"),
        py::arg("times"),
        py::arg("xs"),
        py::arg("ys")
    );
}
