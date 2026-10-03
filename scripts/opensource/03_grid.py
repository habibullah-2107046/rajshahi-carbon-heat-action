"""
03_grid.py  -  open-source version of Step 4 (docs/04_grid_integration.md)

Builds a 240 m grid aligned to the LULC pixels, clips it to the city and
calculates for every year and cell: LSCE density, mean LST, normalised LST,
mean NDVI and mean NDBI.

Run:  python 03_grid.py      (after 02_lsce.py and the Earth Engine export)
Out:  04_outputs/grid/RCC_grid_240m.shp and RCC_grid_values.csv
"""
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from shapely.geometry import box
from rasterstats import zonal_stats

import config as C

C.ensure_dirs()
GRID_DIR = C.OUT_DIR / "grid"
NODATA = -9999.0
boundary = gpd.read_file(C.BOUNDARY)

# ---------- 1. Grid aligned to the clipped LULC raster ----------
ref_path = C.OUT_DIR / f"RCC_LULC_{C.YEARS[0]}.tif"
with rasterio.open(ref_path) as ref:
    crs = ref.crs
    left, bottom, right, top = ref.bounds
boundary = boundary.to_crs(crs)

cells = []
x = left
while x < right:
    yb = bottom
    while yb < top:
        cells.append(box(x, yb, x + C.CELL, yb + C.CELL))
        yb += C.CELL
    x += C.CELL
fishnet = gpd.GeoDataFrame(geometry=cells, crs=crs)
grid = gpd.clip(fishnet, boundary)
grid = grid[grid.geom_type.isin(["Polygon", "MultiPolygon"])].reset_index(drop=True)
grid["AREA_KM2"] = grid.area / 1e6
full = C.CELL * C.CELL / 1e6
grid = grid[grid["AREA_KM2"] >= full * C.MIN_SHARE].reset_index(drop=True)
grid["GID"] = np.arange(len(grid))
print(f"Grid cells: {len(grid)}")


def band_means(path, band):
    """Mean of one band per cell; NaN pixels from Earth Engine are treated as NoData."""
    with rasterio.open(path) as src:
        arr = src.read(band).astype("float64")
        aff = src.transform
    arr[~np.isfinite(arr)] = NODATA
    zs = zonal_stats(grid, arr, affine=aff, nodata=NODATA, stats=["mean"])
    return np.array([z["mean"] if z["mean"] is not None else np.nan for z in zs])


# ---------- 2. Values for each year ----------
fields = []
for y in C.YEARS:
    lulc = C.OUT_DIR / f"RCC_LULC_{y}.tif"
    tif = C.LST_DIR / C.LST_PATTERN.format(year=y)
    if not lulc.exists() or not tif.exists():
        print(f"NOT FOUND for {y} (LULC raster or LST GeoTIFF)")
        continue

    # Pixel count of each class in each cell -> area-weighted coefficient
    codes = C.CLASS_CODES[y]
    cats = zonal_stats(grid, str(lulc), categorical=True, nodata=255)
    lsce = []
    for c in cats:
        tot = wsum = 0.0
        for v, n in c.items():
            cls = codes.get(int(v))
            if cls is not None:
                tot += n
                wsum += n * C.COEF[cls]
        lsce.append(wsum / tot * 1000.0 * 44.0 / 12.0 if tot > 0 else np.nan)   # t CO2 km-2 yr-1
    grid[f"LSCE_{y}"] = lsce

    grid[f"LST_{y}"] = band_means(tif, 1)
    grid[f"NDVI_{y}"] = band_means(tif, 2)
    grid[f"NDBI_{y}"] = band_means(tif, 3)
    lst = grid[f"LST_{y}"]
    grid[f"NLST_{y}"] = (lst - lst.min()) / (lst.max() - lst.min())

    cols = [f"LSCE_{y}", f"LST_{y}", f"NLST_{y}", f"NDVI_{y}", f"NDBI_{y}"]
    missing = int(grid[cols].isna().any(axis=1).sum())
    fields += cols
    print(f"{y} | missing cells={missing} | LSCE {np.nanmin(lsce):.1f} to {np.nanmax(lsce):.1f} t/km2/yr"
          f" | cell LST {lst.min():.2f} to {lst.max():.2f} C")

# ---------- 3. Save ----------
grid = grid[["GID", "AREA_KM2"] + fields + ["geometry"]]
grid.fillna(NODATA).to_file(GRID_DIR / f"RCC_grid_{C.CELL}m.shp")
grid.drop(columns="geometry").to_csv(GRID_DIR / "RCC_grid_values.csv", index=False)
print("DONE! Grid and CSV saved in", GRID_DIR)
