#include "f1_processor.h"
#include <algorithm>   // std::lower_bound

void lerp_position(
    double         time_s,
    const double*  times_ptr,
    const double*  xs_ptr,
    const double*  ys_ptr,
    std::size_t    n,
    double*        out_x,
    double*        out_y
) {
    // Empty array guard
    if (n == 0) { *out_x = 0.0; *out_y = 0.0; return; }

    // std::lower_bound performs a binary search over the range [begin, end).
    // It returns a pointer to the first element that is NOT LESS THAN time_s.
    // Subtracting times_ptr from that pointer gives the integer index.
    const double* it  = std::lower_bound(times_ptr, times_ptr + n, time_s);
    std::size_t   idx = static_cast<std::size_t>(it - times_ptr);

    // Before first sample: return the first known position
    if (idx == 0) {
        *out_x = xs_ptr[0];
        *out_y = ys_ptr[0];
        return;
    }

    // After last sample: return the last known position
    if (idx >= n) {
        *out_x = xs_ptr[n - 1];
        *out_y = ys_ptr[n - 1];
        return;
    }

    // Surrounding samples
    double t0 = times_ptr[idx - 1], t1 = times_ptr[idx];
    double x0 = xs_ptr[idx - 1],    x1 = xs_ptr[idx];
    double y0 = ys_ptr[idx - 1],    y1 = ys_ptr[idx];

    // Linear interpolation: alpha = 0 → at t0, alpha = 1 → at t1
    double alpha = (time_s - t0) / (t1 - t0);
    *out_x = x0 + alpha * (x1 - x0);
    *out_y = y0 + alpha * (y1 - y0);
}
