import numpy as np
from config import MAX_FORECAST_LOOKAHEAD, SEEING_MEAN, SEEING_STD_DEV, MIN_SEEING, MAX_SEEING

def forecast_uncertainty(minutes_ahead, max_ahead=MAX_FORECAST_LOOKAHEAD, max_uncertainty=0.2):
    return np.exp((minutes_ahead / max_ahead) - 1) * max_uncertainty  # exponential

def generate_seeing_time_series(n_minutes, base=SEEING_MEAN, std=SEEING_STD_DEV):
    """
    Generates a realistic minute-by-minute seeing time series using a smoothed random walk,
    clipped to a physical range.
    """
    deltas = np.random.normal(0, std / 10, n_minutes)
    raw_series = np.zeros(n_minutes)
    raw_series[0] = base
    for i in range(1, n_minutes):
        drift = (base - raw_series[i - 1]) * 0.01  # weak pull toward mean
        raw_series[i] = raw_series[i - 1] + deltas[i] + drift
    window_size = 30
    padded = np.pad(raw_series, (window_size // 2,), mode="edge")
    smoothed = np.convolve(padded, np.ones(window_size)/window_size, mode="valid")
    return np.clip(smoothed, MIN_SEEING, MAX_SEEING)