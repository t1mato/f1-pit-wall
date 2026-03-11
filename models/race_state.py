"""
models/race_state.py
─────────────────────
Session-level state for all cars at a given point in time.

Drives three panels in the dashboard:
  • Track map   — car X/Y positions at the current time
  • Leaderboard — race order at the current time
  • Telemetry   — LapData for the selected driver's current lap

Data sources (all from session.load()):
  session.pos_data  — dict[driver_number: str → DataFrame]
                      ~10 Hz X/Y/Z positions, Time-indexed (timedelta)
  session.laps      — all laps for all drivers (LapTime, Position, etc.)
  session.results   — final race results (used for driver metadata)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import fastf1.core

from models.lap import LapData

# Try to import the compiled C++ extension.
# If it hasn't been built yet, fall back to the pure-Python lerp.
try:
    import f1_processor as _f1_cpp
    _USE_CPP = True
except ImportError:
    _USE_CPP = False


class RaceState:
    """Wraps a loaded FastF1 session and answers time-based queries."""

    def __init__(self, session: fastf1.core.Session) -> None:
        self.session = session

        # Position data: {driver_number → DataFrame with Time/X/Y columns}
        self._pos_data: dict[str, pd.DataFrame] = session.pos_data

        # All laps across all drivers
        self._laps: pd.DataFrame = session.laps

        # Driver abbreviation lookup: number → abbr (e.g. "1" → "VER")
        self._num_to_abbr: dict[str, str] = (
            session.results.set_index("DriverNumber")["Abbreviation"]
            .to_dict()
        )

        # Pre-convert position DataFrames to NumPy arrays for the C++ hot path.
        # Done once at load time so the 20 FPS loop has zero pandas overhead.
        # Each value is a dict with keys "times_s", "xs", "ys" as float64 arrays.
        self._pos_arrays: dict[str, dict] = {} # type hint tells us the keys will be strings (driver numbers) and values will be inner dictionaries holding data
        if _USE_CPP:
            for num, df in self._pos_data.items(): 
                self._pos_arrays[num] = {
                    "times_s": (df["Time"].dt.total_seconds()).to_numpy(dtype=np.float64),
                    "xs":       df["X"].to_numpy(dtype=np.float64),
                    "ys":       df["Y"].to_numpy(dtype=np.float64),
                }

    # ── Time range ─────────────────────────────────────────────────────────────

    @property
    def time_range(self) -> tuple[pd.Timedelta, pd.Timedelta]:
        """
        (start, end) timedeltas for the scrubber range.
        Derived from the earliest and latest position sample across all cars.
        """
        all_times = pd.concat(
            [df["Time"] for df in self._pos_data.values()]
        )
        return all_times.min(), all_times.max()

    # ── Track map ─────────────────────────────────────────────────────────────

    def get_positions_at(
        self, time_delta: pd.Timedelta
    ) -> dict[str, tuple[float, float]]:
        """
        Return each car's interpolated (X, Y) position at time_delta.

        Uses the C++ f1_processor extension when available (compiled binary
        search + lerp), otherwise falls back to the pure-Python implementation.

        Args:
            time_delta: Time since session start (from the scrubber).

        Returns:
            dict mapping driver abbreviation → (x, y) in metres.
        """
        result = {}
        time_s = time_delta.total_seconds()

        if _USE_CPP:
            # ── C++ fast path ─────────────────────────────────────────────
            for driver_num, arrs in self._pos_arrays.items():
                abbr = self._num_to_abbr.get(driver_num)
                if not abbr:
                    continue
                x, y = _f1_cpp.lerp_position(
                    time_s,
                    arrs["times_s"],
                    arrs["xs"],
                    arrs["ys"],
                )
                result[abbr] = (x, y)
        else:
            # ── Pure-Python fallback ──────────────────────────────────────
            for driver_num, df in self._pos_data.items():
                abbr = self._num_to_abbr.get(driver_num)
                if not abbr:
                    continue

                times = df["Time"]
                idx = times.searchsorted(time_delta)

                if idx <= 0:
                    result[abbr] = (float(df["X"].iloc[0]), float(df["Y"].iloc[0]))
                    continue
                if idx >= len(df):
                    result[abbr] = (float(df["X"].iloc[-1]), float(df["Y"].iloc[-1]))
                    continue

                t0, t1 = times.iloc[idx - 1], times.iloc[idx]
                x0, y0 = float(df["X"].iloc[idx - 1]), float(df["Y"].iloc[idx - 1])
                x1, y1 = float(df["X"].iloc[idx]),     float(df["Y"].iloc[idx])

                alpha = (time_delta - t0) / (t1 - t0)
                result[abbr] = (x0 + alpha * (x1 - x0), y0 + alpha * (y1 - y0))

        return result

    # ── Leaderboard ───────────────────────────────────────────────────────────

    def get_leaderboard_at(self, time_delta: pd.Timedelta) -> list[str]:
        """
        Return driver abbreviations in race order at the given time.

        Uses lap count + last known Position column from session.laps.
        Drivers who haven't started yet are placed at the back.
        """
        elapsed = self.session.t0_date + time_delta
        completed = self._laps[self._laps["LapStartDate"] <= elapsed].copy()

        if completed.empty:
            return list(self._num_to_abbr.values())

        # Latest lap per driver
        latest = (
            completed.sort_values("LapNumber")
            .groupby("Driver")
            .last()
            .reset_index()
        )
        ordered = latest.sort_values(
            ["LapNumber", "Position"], ascending=[False, True]
        )
        return ordered["Driver"].tolist()

    # ── Telemetry ─────────────────────────────────────────────────────────────

    def get_lap_data_for(
        self, driver_abbr: str, time_delta: pd.Timedelta
    ) -> LapData | None:
        """
        Return a LapData for driver_abbr's current lap at time_delta.

        Returns None if the driver has no lap data at that time.
        """
        elapsed = self.session.t0_date + time_delta
        driver_laps = self._laps[
            (self._laps["Driver"] == driver_abbr)
            & (self._laps["LapStartDate"] <= elapsed)
        ]

        if driver_laps.empty:
            return None

        current_lap = driver_laps.sort_values("LapNumber").iloc[-1]
        return LapData(current_lap)
