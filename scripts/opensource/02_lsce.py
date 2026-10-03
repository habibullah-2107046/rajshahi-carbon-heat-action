"""
02_lsce.py  -  open-source version of Step 2 (docs/02_lulc_and_lsce.md)

Clips each LULC raster to the city boundary, measures the area of every
class and calculates land-specific carbon emission (LSCE):
TE (total emission), TA (total absorption) and NE (net emission).

Run:  python 02_lsce.py
Out:  04_outputs/RCC_LULC_<year>.tif, RCC_LSCE_by_class.csv, RCC_LSCE_summary.csv
"""
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask

import config as C

C.ensure_dirs()
boundary = gpd.read_file(C.BOUNDARY)
NODATA = 255

detail, summary = [], []
for y in C.YEARS:
    src_path = C.LULC_DIR / C.LULC_PATTERN.format(year=y)
    if not src_path.exists():
        print(f"NOT FOUND: {src_path}")
        continue
    with rasterio.open(src_path) as src:
        geoms = boundary.to_crs(src.crs).geometry
        # pixel is kept if its centre lies inside the boundary (same as ArcMap Extract by Mask)
        arr, transform = mask(src, geoms, crop=True, nodata=NODATA, filled=True)
        meta = src.meta.copy()
        px_area = abs(src.res[0] * src.res[1])               # m2 per pixel
    band = arr[0]
    meta.update(height=band.shape[0], width=band.shape[1], transform=transform,
                nodata=NODATA, dtype="uint8", count=1, compress="lzw")
    with rasterio.open(C.OUT_DIR / f"RCC_LULC_{y}.tif", "w", **meta) as dst:
        dst.write(band.astype("uint8"), 1)

    codes = C.CLASS_CODES[y]
    vals, counts = np.unique(band[band != NODATA], return_counts=True)
    te = ta = tot_area = 0.0
    for v, n in zip(vals, counts):
        cls = codes.get(int(v))
        if cls is None:
            print(f"WARNING {y}: raster value {v} has no class in config.CLASS_CODES")
            continue
        area = n * px_area / 1e6                              # km2
        lsce = area * C.COEF[cls] * 44.0 / 12.0               # 10^3 t CO2 per year
        tot_area += area
        te += max(lsce, 0)
        ta += min(lsce, 0)
        detail.append([y, int(v), cls, int(n), round(area, 4), C.COEF[cls], round(lsce, 4)])
    ne = te + ta
    summary.append([y, int(counts.sum()), round(tot_area, 2), round(te, 2), round(ta, 2), round(ne, 2)])
    print(f"{y} | Pixels={counts.sum()} | Area={tot_area:.2f} km2 | TE={te:.2f} | TA={ta:.2f} | NE={ne:.2f}")

pd.DataFrame(detail, columns=["Year", "Value", "Class", "Count", "Area_km2", "Coefficient",
                              "LSCE_1e3_tCO2_yr"]).to_csv(C.OUT_DIR / "RCC_LSCE_by_class.csv", index=False)
pd.DataFrame(summary, columns=["Year", "Pixels", "Total_Area_km2", "TE", "TA", "NE"]).to_csv(
    C.OUT_DIR / "RCC_LSCE_summary.csv", index=False)
print("DONE! Outputs saved in", C.OUT_DIR)
