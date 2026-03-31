"""
data_collector.py
─────────────────
Fetch lap-level data for every race in the 2025 F1 season using FastF1
and write a single consolidated CSV to data/raw/.

Usage
-----
    python src/data_collector.py                     # full season
    python src/data_collector.py --rounds 1 5        # only rounds 1-5
    python src/data_collector.py --output custom.csv

The script skips rounds whose data are already present in the output file
so it is safe to re-run after an interruption.
"""

import argparse
import os
import sys
import time

import fastf1
import pandas as pd

# ─── Constants ────────────────────────────────────────────────────────────────

YEAR = 2025
DEFAULT_OUT = os.path.join(
    os.path.dirname(__file__), "..", "data", "raw", "all_grand_prix_laps_2025.csv"
)
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "FastF1Cache")

DURATION_COLS = [
    "Time", "LapTime", "PitOutTime", "PitInTime",
    "Sector1Time", "Sector2Time", "Sector3Time",
    "Sector1SessionTime", "Sector2SessionTime", "Sector3SessionTime",
]


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _duration_to_str(series: pd.Series) -> pd.Series:
    """Convert timedelta series to 'X days HH:MM:SS.ffffff' strings for CSV storage."""
    return series.astype(str)


def fetch_race_laps(year: int, round_number: int) -> pd.DataFrame | None:
    """Load lap data for a single race round. Returns None on failure."""
    try:
        session = fastf1.get_session(year, round_number, "R")
        session.load(telemetry=False, weather=False, messages=False)
        laps = session.laps.copy()

        if laps.empty:
            print(f"  [WARN] Round {round_number}: no lap data returned.")
            return None

        laps["RoundNumber"] = round_number
        laps["EventName"] = session.event["EventName"]
        return laps

    except Exception as exc:
        print(f"  [ERROR] Round {round_number}: {exc}")
        return None


def _existing_rounds(path: str) -> set[int]:
    """Return the set of RoundNumbers already saved in the output CSV."""
    if not os.path.exists(path):
        return set()
    try:
        existing = pd.read_csv(path, usecols=["RoundNumber"])
        return set(existing["RoundNumber"].dropna().astype(int).unique())
    except Exception:
        return set()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Collect 2025 F1 lap data via FastF1.")
    parser.add_argument(
        "--rounds", nargs=2, type=int, metavar=("START", "END"),
        default=[1, 24],
        help="Inclusive range of round numbers to fetch (default: 1 24).",
    )
    parser.add_argument(
        "--output", type=str, default=DEFAULT_OUT,
        help="Path to output CSV file.",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Re-fetch rounds even if already present in the output file.",
    )
    args = parser.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)
    fastf1.Cache.enable_cache(CACHE_DIR)

    already_done = set() if args.force else _existing_rounds(args.output)
    rounds_to_fetch = [
        r for r in range(args.rounds[0], args.rounds[1] + 1)
        if r not in already_done
    ]

    if not rounds_to_fetch:
        print("All requested rounds already present. Use --force to re-fetch.")
        return

    print(f"Fetching rounds: {rounds_to_fetch}")
    all_frames: list[pd.DataFrame] = []

    for i, rnd in enumerate(rounds_to_fetch, 1):
        print(f"[{i}/{len(rounds_to_fetch)}] Round {rnd} ...", end=" ", flush=True)
        t0 = time.time()
        df = fetch_race_laps(YEAR, rnd)
        elapsed = time.time() - t0

        if df is not None:
            all_frames.append(df)
            print(f"OK  ({len(df)} laps, {elapsed:.1f}s)")
        else:
            print(f"SKIPPED ({elapsed:.1f}s)")

    if not all_frames:
        print("No new data fetched.")
        sys.exit(0)

    new_data = pd.concat(all_frames, ignore_index=True)

    # Merge with existing data if file already exists
    if os.path.exists(args.output) and not args.force:
        existing = pd.read_csv(args.output, low_memory=False)
        combined = pd.concat([existing, new_data], ignore_index=True)
        combined.sort_values(["RoundNumber", "Driver", "LapNumber"], inplace=True)
    else:
        combined = new_data
        combined.sort_values(["RoundNumber", "Driver", "LapNumber"], inplace=True)

    combined.to_csv(args.output, index=False)
    print(f"\nSaved {len(combined):,} total laps → {args.output}")
    rounds_present = sorted(combined["RoundNumber"].dropna().astype(int).unique())
    print(f"Rounds in file: {rounds_present}")


if __name__ == "__main__":
    main()
