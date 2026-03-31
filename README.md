<div align="center">

# 🏎️ F1 2025 — Race Analytics & Result Prediction

**End-to-end data analysis on the complete 2025 Formula 1 season**

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python)
![FastF1](https://img.shields.io/badge/FastF1-3.4%2B-red?style=for-the-badge)
![pandas](https://img.shields.io/badge/pandas-2.0%2B-150458?style=for-the-badge&logo=pandas)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0%2B-green?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-lightgrey?style=for-the-badge)

</div>

---

## 📌 Overview

This project collects, cleans, and analyses lap-by-lap telemetry data from all **24 races of the 2025 F1 World Championship** using the [FastF1](https://github.com/theOehrly/Fast-F1) API.

The analysis covers driver performance, tyre strategy, circuit characteristics, and culminates in a **machine learning model** that predicts final race positions from in-race features.

**2025 Champion:** Lando Norris 🏆 (McLaren — first drivers' title since 2008)

---

## 📚 Table of Contents

- [Project Structure](#project-structure)
- [Notebooks Walkthrough](#notebooks-walkthrough)
- [Key Insights](#key-insights)
- [Quickstart](#quickstart)
- [Data Dictionary](#data-dictionary)
- [Tech Stack](#tech-stack)

---

## 🗂️ Project Structure <a name="project-structure"></a>

```
f1-2025-analysis/
│
├── data/
│   ├── raw/                          ← downloaded by notebook 01
│   └── processed/                    ← engineered features (CSV)
│
├── notebooks/
│   ├── 01_data_collection.ipynb      ← fetch all 24 races via FastF1
│   ├── 02_eda_lap_performance.ipynb  ← driver & team lap time analysis
│   ├── 03_strategy_analysis.ipynb    ← tyre strategy & pit stop patterns
│   ├── 04_feature_engineering.ipynb  ← build race-level features
│   └── 05_race_result_prediction.ipynb ← ML models & predictions
│
├── src/
│   ├── data_collector.py             ← CLI script for data download
│   └── data_processing.py            ← shared parsing & feature functions
│
├── requirements.txt
└── README.md
```

---

## 📓 Notebooks Walkthrough <a name="notebooks-walkthrough"></a>

### [01 — Data Collection](notebooks/01_data_collection.ipynb)
Pulls lap-by-lap telemetry for all 24 races from FastF1. Covers lap times, sector splits, tyre compounds, pit stop windows, and track status (safety car, VSC, red flag).

### [02 — EDA: Lap Performance](notebooks/02_eda_lap_performance.ipynb)
Explores driver and constructor pace across the season.
- Lap time distributions per driver and team
- How pace evolves as tyres degrade
- Circuit vs. constructor performance matrix

### [03 — Strategy Analysis](notebooks/03_strategy_analysis.ipynb)
Breaks down tyre strategy decisions.
- Compound usage (Soft / Medium / Hard) per circuit
- Stint length distributions
- Pit stop timing windows and undercut/overcut patterns

### [04 — Feature Engineering](notebooks/04_feature_engineering.ipynb)
Transforms raw lap data into race-level features for modelling.
- Best & average lap time, consistency score
- Tyre degradation rate per stint
- Pit stop count and strategy chain
- Sector performance index

### [05 — Race Result Prediction](notebooks/05_race_result_prediction.ipynb)
Trains XGBoost and LightGBM models to predict final finishing position.
- Leave-one-race-out cross-validation
- Feature importance ranking
- Podium and Top-10 binary classification

---

## 💡 Key Insights <a name="key-insights"></a>

> This section is updated after each notebook is completed.

| # | Insight |
|---|---------|
| 1 | TBD — filled after EDA |
| 2 | TBD — filled after strategy analysis |
| 3 | TBD — filled after modelling |

---

## 🚀 Quickstart <a name="quickstart"></a>

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/f1-2025-analysis.git
cd f1-2025-analysis

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download race data  (all 24 rounds, ~5–10 min first run)
python src/data_collector.py

# 4. Open notebooks in order
jupyter lab
```

> **Cache note:** FastF1 stores telemetry in `FastF1Cache/` (excluded from git). First run downloads ~1–2 GB; subsequent runs use the local cache.

---

## 📖 Data Dictionary <a name="data-dictionary"></a>

| Column | Type | Description |
|--------|------|-------------|
| `Driver` | str | Three-letter code (e.g. `NOR`, `VER`) |
| `Team` | str | Constructor name |
| `LapTime` | float | Lap duration in seconds |
| `LapNumber` | int | Lap number within the race |
| `Stint` | int | Tyre stint (increments per pit stop) |
| `Compound` | str | SOFT / MEDIUM / HARD / INTERMEDIATE / WET |
| `TyreLife` | int | Laps on current tyre set |
| `Sector1/2/3Time` | float | Sector times in seconds |
| `SpeedI1/I2/FL/ST` | float | Speed trap readings in km/h |
| `Position` | int | Track position at end of each lap |
| `TrackStatus` | str | 1=clear · 2=yellow · 4=SC · 5=red · 6=VSC |
| `EventName` | str | Grand Prix name |
| `RoundNumber` | int | Round number in the championship |

---

## 🛠️ Tech Stack <a name="tech-stack"></a>

| Tool | Role |
|------|------|
| [FastF1](https://github.com/theOehrly/Fast-F1) | F1 telemetry & timing data |
| pandas / numpy | Data wrangling |
| Plotly / seaborn / matplotlib | Interactive & static visualisations |
| scikit-learn | Preprocessing, cross-validation, metrics |
| XGBoost / LightGBM | Gradient boosting regression & classification |

---

## 📜 License

MIT — free to use for learning and portfolio purposes.
F1 timing data is provided by Formula 1 via the FastF1 library under their terms of service.
