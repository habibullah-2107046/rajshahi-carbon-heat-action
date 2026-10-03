# -*- coding: utf-8 -*-
r"""
03_grid.py  -  ArcMap (ArcPy, Python 2.7)

Study : Carbon-Conscious Urban Heat Action in Rajshahi, Bangladesh
Step  : 4 of 6 (see docs/04_grid_integration.md)

WHAT IT DOES
    1. Builds a 240 m x 240 m grid aligned to the LULC pixels and clips it
       to the city boundary (edge cells < 25% of a full cell are removed).
    2. For every year and every cell calculates:
         LSCE_YYYY  land-specific carbon emission density (t CO2 km-2 yr-1)
         LST_YYYY   mean land surface temperature (deg C)
         NLST_YYYY  normalised LST within the year (0-1)
         NDVI_YYYY, NDBI_YYYY  mean spectral indices
    3. Saves the grid shapefile and a CSV of all values.

BEFORE RUNNING
    - Step 2 (clipped LULC rasters in 04_outputs) and Step 3 (GeoTIFFs from
      Google Earth Engine in 03_Landsat_hot_season) must be finished.
    - Remove any grid layer from the map (otherwise the file is locked).
    - Edit FOLDER and BOUNDARY below.

OUTPUT (in 04_outputs\grid)
    RCC_grid_240m.shp, RCC_grid_values.csv
"""
import arcpy
import csv
import os
from arcpy.sa import TabulateArea, ZonalStatisticsAsTable, Con, Raster

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

# ============================== SETTINGS ===================================
FOLDER = r"C:\RCC_project"
BOUNDARY = os.path.join(FOLDER, "01_boundary", "RCC", "RCC.shp")
YEARS = [2000, 2005, 2010, 2015, 2020, 2025]
CELL = 240          # grid size in metres (8 x 8 Landsat pixels)
MIN_SHARE = 0.25    # drop edge cells smaller than 25% of a full cell
NODATA = -9999      # written to cells without a value
# ===========================================================================

OUT_DIR = os.path.join(FOLDER, "04_outputs")
LST_DIR = os.path.join(FOLDER, "03_Landsat_hot_season")
GRID_DIR = os.path.join(OUT_DIR, "grid")
if not os.path.exists(GRID_DIR):
    os.makedirs(GRID_DIR)
SCRATCH = arcpy.env.scratchGDB


def is_bad(x):
    """True for None or NaN (NaN is not equal to itself)."""
    return x is None or x != x


def get_class(name):
    n = str(name).lower()
    if "water" in n:
        return ("Water body", -0.0459)
    if "veg" in n:
        return ("Vegetation", -0.0645)
    if "settle" in n or "built" in n:
        return ("Built-up", 0.0742)
    if "bare" in n or "char" in n:
        return ("Bare/Char land", -0.0527)
    if "crop" in n:
        return ("Crop land", 0.0497)
    return None


def find_raster(y):
    candidates = [
        os.path.join(OUT_DIR, "RCC_LULC_%d.tif" % y),
        os.path.join(OUT_DIR, "RCC_LULC_%d" % y, "rcc_lulc_%d" % y),
        os.path.join(OUT_DIR, "RCC_LULC_%d" % y, "rcc_lulc_%d.tif" % y),
        os.path.join(OUT_DIR, "rcc_lulc_%d" % y),
    ]
    for p in candidates:
        if arcpy.Exists(p) and arcpy.Describe(p).dataType in ("RasterDataset", "RasterBand"):
            return p
    return None


def read_table(tbl, key, field):
    out = {}
    with arcpy.da.SearchCursor(tbl, [key, field]) as cur:
        for k, v in cur:
            if not is_bad(v):
                out[k] = v
    return out


# ---------- 1. Build the grid aligned to the LULC pixels ----------
ref = find_raster(YEARS[0])
r = arcpy.Raster(ref)
ext = r.extent
arcpy.env.snapRaster = ref
arcpy.env.cellSize = ref
arcpy.env.outputCoordinateSystem = r.spatialReference

grid = os.path.join(GRID_DIR, "RCC_grid_%dm.shp" % CELL)
if arcpy.Exists(grid):
    arcpy.Delete_management(grid)

fishnet = os.path.join(SCRATCH, "fishnet")
arcpy.CreateFishnet_management(
    fishnet,
    "%f %f" % (ext.XMin, ext.YMin),
    "%f %f" % (ext.XMin, ext.YMin + 10),
    CELL, CELL, "0", "0",
    "%f %f" % (ext.XMax + CELL, ext.YMax + CELL),
    "NO_LABELS", "#", "POLYGON")
arcpy.Clip_analysis(fishnet, BOUNDARY, grid)

arcpy.AddField_management(grid, "GID", "LONG")
arcpy.AddField_management(grid, "AREA_KM2", "DOUBLE")
arcpy.CalculateField_management(grid, "GID", "!FID!", "PYTHON_9.3")
arcpy.CalculateField_management(grid, "AREA_KM2", "!shape.area@squarekilometers!", "PYTHON_9.3")

full = (CELL * CELL) / 1000000.0
with arcpy.da.UpdateCursor(grid, ["AREA_KM2"]) as cur:
    for row in cur:
        if row[0] < full * MIN_SHARE:
            cur.deleteRow()

print("Grid cells: %s" % arcpy.GetCount_management(grid).getOutput(0))

# ---------- 2. Values for each year ----------
all_fields = []
existing = [f.name for f in arcpy.ListFields(grid)]

for y in YEARS:
    lulc = find_raster(y)
    tif = os.path.join(LST_DIR, "RCC_LST_NDVI_NDBI_%d.tif" % y)
    if lulc is None or not arcpy.Exists(tif):
        print("NOT FOUND for %d (LULC raster or LST GeoTIFF)" % y)
        continue

    # Raster value -> coefficient for this year (codes can differ between years)
    coef = {}
    with arcpy.da.SearchCursor(lulc, ["VALUE", "CLASS_NAME"]) as cur:
        for val, cname in cur:
            info = get_class(cname)
            if info:
                coef[val] = info[1]

    # Area of each class inside each grid cell
    ta = os.path.join(SCRATCH, "ta_%d" % y)
    TabulateArea(grid, "GID", lulc, "VALUE", ta, 30)
    ta_fields = [f.name for f in arcpy.ListFields(ta) if f.name.upper().startswith("VALUE_")]

    # LSCE density = area-weighted coefficient x 1000 x 44/12  (t CO2 km-2 yr-1)
    lsce = {}
    with arcpy.da.SearchCursor(ta, ["GID"] + ta_fields) as cur:
        for row in cur:
            tot = 0.0
            wsum = 0.0
            for fname, a in zip(ta_fields, row[1:]):
                v = int(fname.split("_")[1])
                if v in coef and not is_bad(a):
                    tot += a
                    wsum += a * coef[v]
            if tot > 0:
                lsce[row[0]] = wsum / tot * 1000.0 * 44.0 / 12.0

    # Mean LST, NDVI, NDBI per cell. GEE GeoTIFFs keep band names and store
    # empty pixels as NaN, so NaN is converted to NoData first.
    vals = {}
    band_names = [b.name for b in arcpy.Describe(tif).children]
    for i, name in enumerate(["LST", "NDVI", "NDBI"]):
        band = Raster(os.path.join(tif, band_names[i]))
        clean = Con(band > -1000, band)
        clean_path = os.path.join(SCRATCH, "c_%s_%d" % (name, y))
        clean.save(clean_path)
        zt = os.path.join(SCRATCH, "zs_%s_%d" % (name, y))
        ZonalStatisticsAsTable(grid, "GID", clean_path, zt, "DATA", "MEAN")
        vals[name] = read_table(zt, "GID", "MEAN")

    # Normalised LST (0-1) within the year
    lv = list(vals["LST"].values())
    lo, hi = min(lv), max(lv)
    nlst = dict((k, (v - lo) / (hi - lo)) for k, v in vals["LST"].items())

    flds = ["LSCE_%d" % y, "LST_%d" % y, "NLST_%d" % y, "NDVI_%d" % y, "NDBI_%d" % y]
    for f in flds:
        if f not in existing:
            arcpy.AddField_management(grid, f, "DOUBLE")
            existing.append(f)

    missing = 0
    with arcpy.da.UpdateCursor(grid, ["GID"] + flds) as cur:
        for row in cur:
            g = row[0]
            v = [lsce.get(g), vals["LST"].get(g), nlst.get(g),
                 vals["NDVI"].get(g), vals["NDBI"].get(g)]
            if any(is_bad(x) for x in v):
                missing += 1
            cur.updateRow([g] + [NODATA if is_bad(x) else x for x in v])

    all_fields += flds
    lsv = list(lsce.values())
    print("%d | missing cells=%d | LSCE %.1f to %.1f t/km2/yr | cell LST %.2f to %.2f C"
          % (y, missing, min(lsv), max(lsv), lo, hi))

# ---------- 3. Export CSV ----------
csv_path = os.path.join(GRID_DIR, "RCC_grid_values.csv")
with open(csv_path, "wb") as f:
    w = csv.writer(f)
    w.writerow(["GID", "AREA_KM2"] + all_fields)
    with arcpy.da.SearchCursor(grid, ["GID", "AREA_KM2"] + all_fields) as cur:
        for row in cur:
            w.writerow(row)

print("DONE! Grid and CSV saved in 04_outputs\\grid")
