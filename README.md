# Telescope Queue Simulation

This project simulates a night of observations at Gemini South, comparing two scheduling strategies:
- A **baseline**, conditions-based queue
- A **forecast-aware**, signal-to-noise-optimized queue

## Features
This simulation models a single night of telescope observing time at Gemini South, minute by minute, under variable seeing conditions. It compares two queue scheduling strategies:

1. **Baseline Strategy (Conditions-Based)**
   - Selects the highest-priority observing program that can be executed given the current seeing and available time.
   - Ignores future conditions — decisions are made only with present knowledge.

2. **Forecast-Aware Strategy (SNR-Optimized)**
   - Uses a 30-minute forecast window to estimate future seeing.
   - Applies a time-dependent uncertainty model to simulate real-world forecast degradation.
   - Chooses observing programs based on predicted conditions, not just current ones.

For both strategies:
- Seeing quality is divided into bins (e.g., 0–20%, 20–50%) based on a realistic distribution of seeing values.
- Programs are drawn from a pool of imaging and spectroscopic observations, each with a required seeing bin and fixed time requirement (including overhead).
- Programs are only executed if there is enough time and the expected seeing meets their quality threshold.
- Seeing is simulated using a constrained random walk and smoothed to mimic realistic atmospheric variation.
- **Seeing bin thresholds (in arcseconds) and overhead times are based on typical operational values at Gemini South.**

The simulation outputs:
- A log of which programs were executed, when, and whether their seeing requirements were met.
- A plot comparing true seeing, forecast seeing, forecast uncertainty, and executed observation windows.

## Forecast Model
Forecasts in the simulation incorporate uncertainty that increases exponentially with time. The standard deviation σ used to perturb future seeing values is calculated as:
σ(t) = max_uncertainty × exp(t / t_max − 1)

Where:
- `t` is the number of minutes ahead
- `t_max` is the maximum forecast horizon (default: 30 minutes)
- `max_uncertainty` is the maximum standard deviation applied (default: 0.2 arcsec)

This models increasing uncertainty the further ahead the telescope tries to predict seeing conditions.

## File Overview
- `core.py`: Defines the main classes for observing programs and nightly simulation
- `utils.py`: Utility functions (e.g., seeing generation, forecast uncertainty)
- `config.py`: Global constants and seeing bin definitions
- `plotting.py`: Code for visualizing forecasts and execution decisions
- `runsimulation.py`: Command-line script that runs both queue strategies and invokes plotting

## How to Run

1. Make sure you have Python 3 and the required packages installed:

```bash
pip install numpy matplotlib

2.	Then run the main simulation:
python runsimulation.py

This will simulate both strategies over the same night and generate a plot comparing actual vs. forecast seeing conditions, as well as program execution outcomes.


# telescope-queue-sim
