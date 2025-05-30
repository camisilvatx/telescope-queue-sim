import matplotlib.pyplot as plt
import numpy as np
from config import MIN_SEEING, MAX_SEEING, SEEING_MEAN
from utils import forecast_uncertainty

def plot_forecast_windows(common_series, night2):
    forecast_means = np.array(night2.forecast_means)
    forecast_uncertainties = np.array(night2.forecast_uncertainties)

    plt.figure(figsize=(14, 5))
    plt.plot(common_series, label='True Seeing', color='blue')

    exec_times = []
    noisy_forecasts = []
    forecast_uncs = []
    true_forecast_means = []

    for entry in night2.log:
        if 'Executing' in entry:
            start_time = int(entry.split(':')[0])
            details = entry.split('min')[0]
            duration = int(details.split(',')[-1].strip().split()[0])
            end_time = start_time + duration

            forecast_start = end_time
            forecast_end = min(end_time + 30, len(common_series))
            forecast_window = np.arange(forecast_start, forecast_end)

            true_vals = common_series[forecast_window]
            mins_ahead = forecast_window - end_time
            sigmas = np.array([forecast_uncertainty(m) for m in mins_ahead])

            upper = np.clip(true_vals + sigmas, MIN_SEEING, MAX_SEEING)
            lower = np.clip(true_vals - sigmas, MIN_SEEING, MAX_SEEING)

            plt.fill_between(forecast_window, lower, upper, color='purple', alpha=0.15)
            true_avg_seeing = np.mean(true_vals)
            plt.hlines(true_avg_seeing, forecast_start, forecast_end,
                       color='purple', linestyle='--', linewidth=1.5)

            forecast_unc_used = night2.forecast_uncertainties[start_time]
            noisy_forecast = night2.forecast_means[start_time]

            exec_times.append(start_time)
            noisy_forecasts.append(noisy_forecast)
            forecast_uncs.append(forecast_unc_used)
            true_forecast_means.append(true_avg_seeing)

            plt.axvline(start_time, linestyle=':', color='black', linewidth=1)
            plt.axvline(end_time, linestyle='--', color='gray', linewidth=1)

    plt.errorbar(exec_times, noisy_forecasts, yerr=forecast_uncs,
                 fmt='o', color='orange', label='Noisy Forecast (used in decision)')

    plt.axhline(SEEING_MEAN, linestyle='--', color='gray', label='Mean Seeing')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Seeing (arcsec)')
    plt.title('Forecast Windows with Pointwise Uncertainty and Decision Forecasts')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()