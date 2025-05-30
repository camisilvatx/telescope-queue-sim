import numpy as np

# Define overhead times for different observation types
IMAGING_OVERHEAD = 10 
SPECTROSCOPY_OVERHEAD = 20 
MAX_FORECAST_LOOKAHEAD = 30  
FORECAST_OBS_WINDOW = 10    # last portion of forecast window for actual observation

# Seeing simulation parameters
SEEING_MEAN = 0.7  
SEEING_STD_DEV = 0.2  # Typical seeing variation
MIN_SEEING = 0.3
MAX_SEEING = 2.0

# Calculate percentiles to categorize seeing conditions
SEEING_SAMPLE = np.clip(
    np.random.normal(SEEING_MEAN, SEEING_STD_DEV, 10000), 0, 2
)
SEEING_PERCENTILES = np.percentile(SEEING_SAMPLE, [20, 50, 70])

SEEING_BINS = {
    "0-20%": (0, SEEING_PERCENTILES[0]),
    "20-50%": (SEEING_PERCENTILES[0], SEEING_PERCENTILES[1]),
    "50-70%": (SEEING_PERCENTILES[1], SEEING_PERCENTILES[2]),
    ">70%": (SEEING_PERCENTILES[2], float("inf")),
}