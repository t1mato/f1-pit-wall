# F1 Telemetry Visualizer

A desktop app for replaying Formula 1 race telemetry frame-by-frame. It fetches session data via the FastF1 API, renders live car positions on an accurate track map, and displays per-driver telemetry (speed, throttle, brake, DRS, gear) as you scrub through the race timeline.

![F1 Telemetry Visualizer](docs/screenshot.png)

---

## Tech Stack

| Layer | Library |
|---|---|
| UI Framework | PySide6 (Qt6) |
| Real-time plotting | pyqtgraph (OpenGL-backed) |
| F1 data | FastF1 |
| Numerics | NumPy, pandas, scipy |
| Performance | C++17 extension via pybind11 |

---

## Setup & Installation

**Prerequisites:** Python 3.10+, a C++ compiler (clang on macOS, gcc on Linux)

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd f1-telemetry

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Build the C++ extension (optional but recommended for best performance)
pip install --no-build-isolation -e .
```

> The C++ extension (`f1_processor`) accelerates position interpolation in the 20 FPS render loop. If the build is skipped, the app falls back to a pure-Python implementation automatically.

---

## Running

```bash
python main.py
```

On first launch, FastF1 downloads ~50–100 MB of session data. Subsequent runs load from the local cache in seconds.

**To change the race**, edit the top of `main.py`:

```python
YEAR         = 2023
ROUND_ID     = "Bahrain"   # race name or round number (1–24)
SESSION_TYPE = "R"          # R=Race, Q=Qualifying, FP1/FP2/FP3=Practice
```

---

## Features

- **Track map** — 2D circuit outline with live car dots colored by team, rotated to match broadcast orientation
- **Timeline scrubber** — drag or play/pause through the full race at 20 FPS
- **Driver telemetry cards** — click any driver in the leaderboard to pin a card showing speed, gear, throttle, brake, and DRS status in real time
- **Live leaderboard** — race standings updated every ~1 second as you scrub

## Architecture

```
models/      — data layer (session loading, lap telemetry, race state queries)
controllers/ — background QThread worker for async session loading
views/       — UI panels (track map, leaderboard, telemetry cards, scrubber)
src/         — C++ source for the fast lerp_position() hot path
include/     — C++ headers
```

The update loop runs at 20 FPS. Car position interpolation uses binary search (`std::lower_bound`) + linear interpolation in C++. Position DataFrames are converted to NumPy float64 arrays once at load time to eliminate per-frame pandas overhead.
