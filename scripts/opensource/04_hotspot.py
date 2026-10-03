"""
04_hotspot.py  -  open-source version of Step 5 (docs/05_hotspot_and_zones.md)

Getis-Ord Gi* hotspot analysis of LSCE and LST for every year, written to
reproduce ArcMap's "Hot Spot Analysis (Getis-Ord Gi*)" with the settings
used in the study: fixed distance band of 480 m between cell centroids,
two-sided p-values and False Discovery Rate (FDR) correction.

The Gi* z-score is calculated with the standard formula used by ArcGIS
(Getis and Ord, 1992; Ord and Getis, 1995). It works for variables with
negative values such as LSCE, and it is not changed by row standardisation
because every row is scaled by a constant.

The two results are then combined into carbon-heat stress zones.

Run:  python 04_hotspot.py
Out:  04_outputs/grid/RCC_grid_240m.shp (new fields HSC_, HSH_, ZONE_)
      04_outputs/hotspots/hotspot_zone_summary.csv
"""
import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.stats import norm
from scipy.spatial import cKDTree

import config as C

C.ensure_dirs()
GRID = C.OUT_DIR / "grid" / f"RCC_grid_{C.CELL}m.shp"
grid = gpd.read_file(GRID)

# Binary weights: every cell whose centroid lies within BAND metres,
# including the cell itself (this is what makes it Gi* rather than Gi)
pts = np.column_stack([grid.centroid.x, grid.centroid.y])
neighbours = cKDTree(pts).query_ball_point(pts, r=C.BAND)
n = len(pts)
W = np.zeros((n, n))
for i, nb in enumerate(neighbours):
    W[i, nb] = 1.0


def gi_star_z(x):
    """Gi* z-score for every cell (ArcGIS formula)."""
    x = np.asarray(x, dtype=float)
    xbar = x.mean()
    s = np.sqrt((x ** 2).mean() - xbar ** 2)
    sw = W.sum(axis=1)
    sw2 = (W ** 2).sum(axis=1)
    num = W @ x - xbar * sw
    den = s * np.sqrt((n * sw2 - sw ** 2) / (n - 1))
    return num / den


def bh_threshold(p, alpha):
    """Benjamini-Hochberg cut-off: the largest p(k) with p(k) <= k/n * alpha."""
    ps = np.sort(p)
    ok = ps <= (np.arange(1, len(ps) + 1) / len(ps)) * alpha
    return ps[ok].max() if ok.any() else 0.0


def gi_bin(values):
    """Gi_Bin as in ArcGIS: +3/+2/+1 = hot spot at 99/95/90 %, negative = cold spot."""
    z = gi_star_z(values)
    p = 2 * (1 - norm.cdf(np.abs(z)))                  # two-sided p-value
    bins = np.zeros(len(z), dtype=int)
    for level, alpha in ((1, 0.10), (2, 0.05), (3, 0.01)):
        sig = p <= bh_threshold(p, alpha)
        bins[sig] = level * np.sign(z[sig]).astype(int)
    return bins


summary = []
for y in C.YEARS:
    if f"LSCE_{y}" not in grid.columns:
        print(f"NOT FOUND: fields for {y}")
        continue
    c = gi_bin(grid[f"LSCE_{y}"])
    h = gi_bin(grid[f"LST_{y}"])
    L = C.ZONE_LEVEL
    zone = np.select(
        [(c >= L) & (h >= L), c >= L, h >= L, (c <= -L) & (h <= -L)],
        [1, 2, 3, 4], default=0)
    grid[f"HSC_{y}"], grid[f"HSH_{y}"], grid[f"ZONE_{y}"] = c, h, zone

    a = grid.groupby(zone)["AREA_KM2"].sum()
    row = [y] + [round(a.get(k, 0.0), 2) for k in (1, 2, 3, 4, 0)]
    summary.append(row)
    print(f"{y} | Dual={row[1]:.2f} | Carbon only={row[2]:.2f} | Heat only={row[3]:.2f} "
          f"| Cool sink={row[4]:.2f} | Other={row[5]:.2f} km2")

grid.to_file(GRID)
pd.DataFrame(summary, columns=["Year", "Dual_stress_km2", "Carbon_only_km2", "Heat_only_km2",
                               "Cool_sink_km2", "Not_significant_km2"]).to_csv(
    C.OUT_DIR / "hotspots" / "hotspot_zone_summary.csv", index=False)
print("DONE! Zones written to", GRID)
