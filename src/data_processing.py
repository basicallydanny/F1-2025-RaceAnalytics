import pandas as pd


def parse_duration_seconds(series: pd.Series) -> pd.Series:
    """Parse duration strings like '0 days 00:01:59.392000' into seconds."""
    return pd.to_timedelta(series, errors='coerce').dt.total_seconds()


def load_lap_data(path: str) -> pd.DataFrame:
    """Load F1 lap data and normalize key time columns."""
    df = pd.read_csv(path, low_memory=False)

    duration_cols = [
        'Time',
        'LapTime',
        'PitOutTime',
        'PitInTime',
        'Sector1Time',
        'Sector2Time',
        'Sector3Time',
        'Sector1SessionTime',
        'Sector2SessionTime',
        'Sector3SessionTime',
    ]

    for col in duration_cols:
        if col in df.columns:
            df[col] = parse_duration_seconds(df[col])

    df['LapNumber'] = pd.to_numeric(df['LapNumber'], errors='coerce')
    df['Position'] = pd.to_numeric(df['Position'], errors='coerce')
    df['RoundNumber'] = pd.to_numeric(df['RoundNumber'], errors='coerce')
    df['Team'] = df['Team'].astype(str)
    df['Driver'] = df['Driver'].astype(str)
    df['EventName'] = df['EventName'].astype(str)
    df['Compound'] = df['Compound'].astype(str).replace('nan', pd.NA)

    return df


def summarize_strategy(compounds: pd.Series) -> str:
    """Create a tire strategy string from the ordered compound sequence."""
    compounds = compounds.dropna().astype(str)
    if compounds.empty:
        return 'unknown'
    unique_sequence = list(dict.fromkeys(compounds))
    return ' -> '.join(unique_sequence)


def create_driver_session_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate lap-level data into driver-session summary features."""
    valid_laps = df.dropna(subset=['LapTime'])

    summary = (
        valid_laps
        .groupby(['EventName', 'RoundNumber', 'Driver', 'Team'])
        .agg(
            total_laps=('LapTime', 'count'),
            valid_laps=('LapTime', 'count'),
            best_lap_sec=('LapTime', 'min'),
            average_lap_sec=('LapTime', 'mean'),
            median_lap_sec=('LapTime', 'median'),
            std_lap_sec=('LapTime', 'std'),
            fastest_sector1_sec=('Sector1Time', 'min'),
            fastest_sector2_sec=('Sector2Time', 'min'),
            fastest_sector3_sec=('Sector3Time', 'min'),
            pit_stops=('Stint', 'max'),
            compound_changes=('Compound', lambda x: len(list(dict.fromkeys(x.dropna().astype(str))))),
            strategy=('Compound', summarize_strategy),
        )
        .reset_index()
    )

    summary['consistency'] = summary['std_lap_sec'] / summary['average_lap_sec']
    summary['consistency'] = summary['consistency'].fillna(0.0)
    summary['average_sector_sec'] = (
        summary[['fastest_sector1_sec', 'fastest_sector2_sec', 'fastest_sector3_sec']]
        .mean(axis=1)
    )

    return summary


def build_target_labels(df: pd.DataFrame, summary: pd.DataFrame) -> pd.DataFrame:
    """Compute final driving position labels and merge with summary features."""
    final_positions = (
        df.sort_values(['EventName', 'Driver', 'LapNumber'])
        .groupby(['EventName', 'Driver'])['Position']
        .last()
        .reset_index()
        .rename(columns={'Position': 'final_position'})
    )

    merged = summary.merge(final_positions, on=['EventName', 'Driver'], how='left')
    merged['final_position'] = merged['final_position'].fillna(999).astype(int)
    merged['top_10'] = (merged['final_position'] <= 10).astype(int)
    merged['top_3'] = (merged['final_position'] <= 3).astype(int)
    merged['finished'] = (merged['final_position'] < 99).astype(int)

    return merged


def build_feature_matrix(summary: pd.DataFrame) -> pd.DataFrame:
    """Select features for modeling and keep identifiers for analysis."""
    feature_columns = [
        'RoundNumber',
        'Team',
        'total_laps',
        'valid_laps',
        'best_lap_sec',
        'average_lap_sec',
        'median_lap_sec',
        'std_lap_sec',
        'consistency',
        'average_sector_sec',
        'fastest_sector1_sec',
        'fastest_sector2_sec',
        'fastest_sector3_sec',
        'pit_stops',
        'compound_changes',
    ]
    return summary[['EventName', 'Driver', 'Team'] + feature_columns + ['final_position', 'top_10', 'top_3', 'finished']]
