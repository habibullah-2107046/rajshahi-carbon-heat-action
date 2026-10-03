# -*- coding: utf-8 -*-
r"""
02_lsce.py  -  ArcMap (ArcPy, Python 2.7)

Study : Carbon-Conscious Urban Heat Action in Rajshahi, Bangladesh
Step  : 2 of 6 (see docs/02_lulc_and_lsce.md)

WHAT IT DOES
    Reads the six LULC rasters that were clipped to the city boundary,
    counts the area of each class and calculates land-specific carbon
    emission (LSCE): total emission (TE), total absorption (TA) and
    net emission (NE) for every year.

BEFORE RUNNING
    - Clip the LULC rasters with Extract by Mask (docs/02_lulc_and_lsce.md)
      and save them in 04_outputs as RCC_LULC_2000.tif ... RCC_LULC_2025.tif
      (ESRI GRID rasters inside a sub-folder are also found automatically).
    - Each raster needs a text field CLASS_NAME.
    - Edit FOLDER below.

HOW TO RUN
    ArcMap > Geoprocessing > Python > right-click > Load... > Enter

OUTPUT (in 04_outputs)
    RCC_LSCE_by_class.csv   area and LSCE of every class and year
    RCC_LSCE_summary.csv    TE, TA, NE per year (10^3 t CO2 per year)
"""
import arcpy
import csv
import os

# ============================== SETTINGS ===================================
FOLDER = r"C:\RCC_project"          # project folder (avoid spaces if possible)
YEARS = [2000, 2005, 2010, 2015, 2020, 2025]
# ===========================================================================

OUT_DIR = os.path.join(FOLDER, "04_outputs")


def get_class(name):
    """Return (class label, coefficient in kg C m-2 yr-1) from the class name."""
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
    """Find the clipped LULC raster of year y (tif or GRID, flat or in a sub-folder)."""
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


detail_rows = []
summary_rows = []

for y in YEARS:
    ras = find_raster(y)
    if ras is None:
        print("NOT FOUND: LULC raster for %d in %s" % (y, OUT_DIR))
        continue
    print("Using: " + ras)

    r = arcpy.Raster(ras)
    cell_area = r.meanCellWidth * r.meanCellHeight          # m2 per pixel

    te = 0.0
    ta = 0.0
    total_area = 0.0
    total_count = 0

    with arcpy.da.SearchCursor(ras, ["VALUE", "CLASS_NAME", "COUNT"]) as cur:
        for val, cname, cnt in cur:
            info = get_class(cname)
            if info is None:
                print("WARNING %d: unknown class '%s' (Value %d)" % (y, cname, val))
                continue
            name, coef = info
            area = cnt * cell_area / 1000000.0              # km2
            lsce = area * coef * 44.0 / 12.0                # 10^3 t CO2 per year
            total_area += area
            total_count += cnt
            if lsce > 0:
                te += lsce
            else:
                ta += lsce
            detail_rows.append([y, val, name, cnt, round(area, 4), coef, round(lsce, 4)])

    ne = te + ta
    summary_rows.append([y, total_count, round(total_area, 2), round(te, 2), round(ta, 2), round(ne, 2)])
    print("%d | Pixels=%d | Area=%.2f km2 | TE=%.2f | TA=%.2f | NE=%.2f"
          % (y, total_count, total_area, te, ta, ne))

with open(os.path.join(OUT_DIR, "RCC_LSCE_by_class.csv"), "wb") as f:
    w = csv.writer(f)
    w.writerow(["Year", "Value", "Class", "Count", "Area_km2", "Coefficient", "LSCE_1e3_tCO2_yr"])
    w.writerows(detail_rows)

with open(os.path.join(OUT_DIR, "RCC_LSCE_summary.csv"), "wb") as f:
    w = csv.writer(f)
    w.writerow(["Year", "Pixels", "Total_Area_km2", "TE", "TA", "NE"])
    w.writerows(summary_rows)

print("DONE! CSV files saved in 04_outputs")
