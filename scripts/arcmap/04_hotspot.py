# -*- coding: utf-8 -*-
r"""
04_hotspot.py  -  ArcMap (ArcPy, Python 2.7)

Study : Carbon-Conscious Urban Heat Action in Rajshahi, Bangladesh
Step  : 5 of 6 (see docs/05_hotspot_and_zones.md)

WHAT IT DOES
    1. Runs Hot Spot Analysis (Getis-Ord Gi*) on LSCE and on LST for every
       year (fixed distance band 480 m, Euclidean distance, row
       standardisation, FDR correction).
    2. Combines the two results at 95% confidence into carbon-heat zones:
         1 = dual stress      (LSCE hotspot + LST hotspot)
         2 = carbon hotspot only
         3 = heat hotspot only
         4 = cool sink        (LSCE coldspot + LST coldspot)
         0 = not significant
    3. Writes HSC_YYYY, HSH_YYYY and ZONE_YYYY to the grid and saves the
       zone areas to a CSV.

BEFORE RUNNING
    - Step 4 must be finished (04_outputs\grid\RCC_grid_240m.shp).
    - Remove the grid layer from the map. Edit FOLDER below.

NOTE
    The ArcMap Python window sometimes does not print the summary lines.
    If >>> returns without a red error, open hotspot_zone_summary.csv.

OUTPUT (in 04_outputs\hotspots)
    HS_LSCE_YYYY.shp, HS_LST_YYYY.shp, hotspot_zone_summary.csv
"""
import arcpy
import csv
import os

arcpy.env.overwriteOutput = True

# ============================== SETTINGS ===================================
FOLDER = r"C:\RCC_project"
YEARS = [2000, 2005, 2010, 2015, 2020, 2025]
BAND = 480          # fixed distance band in metres (two grid cells)
# ===========================================================================

GRID = os.path.join(FOLDER, "04_outputs", "grid", "RCC_grid_240m.shp")
HS_DIR = os.path.join(FOLDER, "04_outputs", "hotspots")
if not os.path.exists(HS_DIR):
    os.makedirs(HS_DIR)

existing = [f.name for f in arcpy.ListFields(GRID)]


def add_field(name):
    if name not in existing:
        arcpy.AddField_management(GRID, name, "SHORT")
        existing.append(name)


def run_hotspot(field, out_name):
    """Run Gi* on one field and return {grid FID: Gi_Bin}."""
    out = os.path.join(HS_DIR, out_name + ".shp")
    arcpy.HotSpots_stats(GRID, field, out, "FIXED_DISTANCE_BAND",
                         "EUCLIDEAN_DISTANCE", "ROW", BAND, "", "", "APPLY_FDR")
    bins = {}
    with arcpy.da.SearchCursor(out, ["SOURCE_ID", "Gi_Bin"]) as cur:
        for sid, b in cur:
            bins[sid] = b if b is not None else 0
    return bins


summary = []
for y in YEARS:
    c_bins = run_hotspot("LSCE_%d" % y, "HS_LSCE_%d" % y)
    h_bins = run_hotspot("LST_%d" % y, "HS_LST_%d" % y)

    fc, fh, fz = "HSC_%d" % y, "HSH_%d" % y, "ZONE_%d" % y
    for f in (fc, fh, fz):
        add_field(f)

    area = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
    with arcpy.da.UpdateCursor(GRID, ["OID@", "AREA_KM2", fc, fh, fz]) as cur:
        for row in cur:
            c = c_bins.get(row[0], 0)
            h = h_bins.get(row[0], 0)
            if c >= 2 and h >= 2:
                z = 1      # dual stress
            elif c >= 2:
                z = 2      # carbon hotspot only
            elif h >= 2:
                z = 3      # heat hotspot only
            elif c <= -2 and h <= -2:
                z = 4      # cool sink
            else:
                z = 0      # not significant
            area[z] += row[1]
            cur.updateRow([row[0], row[1], c, h, z])

    summary.append([y] + [round(area[k], 2) for k in (1, 2, 3, 4, 0)])
    print("%d | Dual=%.2f | Carbon only=%.2f | Heat only=%.2f | Cool sink=%.2f | Other=%.2f km2"
          % (y, area[1], area[2], area[3], area[4], area[0]))

with open(os.path.join(HS_DIR, "hotspot_zone_summary.csv"), "wb") as f:
    w = csv.writer(f)
    w.writerow(["Year", "Dual_stress_km2", "Carbon_only_km2", "Heat_only_km2",
                "Cool_sink_km2", "Not_significant_km2"])
    w.writerows(summary)

print("DONE! Hotspots saved in 04_outputs\\hotspots")
