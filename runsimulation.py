from core import ObservingNight
from utils import generate_seeing_time_series, forecast_uncertainty
from config import MIN_SEEING, MAX_SEEING, SEEING_MEAN
from plotting import plot_forecast_windows

# Shared seeing
common_series = generate_seeing_time_series(600)

# Run both strategies
night1 = ObservingNight(seeing_time_series=common_series, SeeingCurve=False)
print("\nBaseline (conditions-based):")
night1.run_night(use_forecast=False)

night2 = ObservingNight(seeing_time_series=common_series, SeeingCurve=False)
print("\nForecast-aware:")
night2.run_night(use_forecast=True)

if __name__ == "__main__":
    ...
    plot_forecast_windows(common_series, night2)


def main():
    common_series = generate_seeing_time_series(600)

    print("\nBaseline (conditions-based):")
    night1 = ObservingNight(seeing_time_series=common_series, SeeingCurve=False)
    night1.run_night(use_forecast=False)

    print("\nForecast-aware:")
    night2 = ObservingNight(seeing_time_series=common_series, SeeingCurve=False)
    night2.run_night(use_forecast=True)

    # Optionally: plotting logic here