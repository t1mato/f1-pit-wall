#pragma once
#include <cstddef>   // std::size_t

/**
 * lerp_position
 * ─────────────
 * Given one driver's time-series position data as parallel C arrays,
 * binary-searches for the two samples surrounding `time_s` and
 * linearly interpolates between them.
 *
 * This is the pure-C++ core — no Python objects, no pandas, no GIL.
 *
 * @param time_s    Query time in seconds (from session start).
 * @param times_ptr Sorted array of sample timestamps (seconds), length n.
 * @param xs_ptr    X-positions in metres, length n, parallel to times_ptr.
 * @param ys_ptr    Y-positions in metres, length n, parallel to times_ptr.
 * @param n         Number of samples.
 * @param out_x     Output: interpolated X position.
 * @param out_y     Output: interpolated Y position.
 */
void lerp_position(
    double         time_s,
    const double*  times_ptr,
    const double*  xs_ptr,
    const double*  ys_ptr,
    std::size_t    n,
    double*        out_x,
    double*        out_y
);
