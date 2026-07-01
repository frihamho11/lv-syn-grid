from pathlib import Path
import numpy as np
import pandas as pd

project = "Test"
out_dir = Path("grids") / project / "data"
out_dir.mkdir(parents=True, exist_ok=True)

ts = pd.date_range("2025-01-01 00:00:00", "2025-12-31 23:45:00", freq="15min")

hour = ts.hour.to_numpy() + ts.minute.to_numpy() / 60.0
day_of_year = ts.dayofyear.to_numpy()

morning_peak = np.exp(-0.5 * ((hour - 7.0) / 1.8) ** 2)
evening_peak = np.exp(-0.5 * ((hour - 19.0) / 2.3) ** 2)
midday_peak = np.exp(-0.5 * ((hour - 13.0) / 3.0) ** 2)
night_base = 0.35 * np.ones_like(hour)

season = 1.0 + 0.15 * np.cos(2 * np.pi * (day_of_year - 15) / 365.0)

def normalize_to_1000_kwh(shape):
    shape = np.maximum(shape, 0.001)
    profile = shape * season
    return profile / profile.sum() * 1000.0

df = pd.DataFrame({"ts": ts})

df["H0"] = normalize_to_1000_kwh(night_base + 0.8 * morning_peak + 1.2 * evening_peak)
df["G0"] = normalize_to_1000_kwh(0.3 + 0.9 * midday_peak)
df["G1"] = normalize_to_1000_kwh(np.where((hour >= 8) & (hour <= 18), 1.0, 0.15))
df["G2"] = normalize_to_1000_kwh(0.2 + 1.2 * evening_peak)
df["G3"] = normalize_to_1000_kwh(0.8 + 0.2 * midday_peak)
df["G6"] = normalize_to_1000_kwh(0.4 + 0.7 * midday_peak)

file = out_dir / "synthload2025.xlsx"
df.to_excel(file, index=False)

print(f"created: {file}")
print(df.head())
