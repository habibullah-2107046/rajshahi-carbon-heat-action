"""
config.py  -  settings shared by all open-source scripts.

Edit the paths in this file once; every script reads them from here.
"""
from pathlib import Path

# ============================== PATHS ======================================
# Project folder with the same structure as described in docs/README.md
PROJECT = Path(r"C:\RCC_project")

BOUNDARY = PROJECT / "01_boundary" / "RCC" / "RCC.shp"   # city boundary
LULC_DIR = PROJECT / "02_LULC_existing"                 # classified LULC rasters
LULC_PATTERN = "LULC_{year}.tif"                         # file name of each LULC raster
LST_DIR = PROJECT / "03_Landsat_hot_season"             # GeoTIFFs from Earth Engine
LST_PATTERN = "RCC_LST_NDVI_NDBI_{year}.tif"
OUT_DIR = PROJECT / "04_outputs"                        # everything the scripts create
FIG_DIR = PROJECT / "05_figures"

# ============================== STUDY SETTINGS =============================
YEARS = [2000, 2005, 2010, 2015, 2020, 2025]
CITY_NAME = "Rajshahi City Corporation"

# Carbon emission coefficients (kg C per m2 per year); + = source, - = sink
COEF = {
    "water":      -0.0459,
    "vegetation": -0.0645,
    "crop":        0.0497,
    "builtup":     0.0742,
    "bare":       -0.0527,
}

# Which raster value means which class, for every year.
# GeoTIFFs do not store class names, so they are given here.
# These are the codes of the Rajshahi LULC rasters (note that 2005 differs).
_STANDARD = {0: "water", 1: "vegetation", 2: "builtup", 3: "bare", 4: "crop"}
CLASS_CODES = {
    2000: _STANDARD,
    2005: {0: "water", 1: "crop", 2: "vegetation", 3: "bare", 4: "builtup"},
    2010: _STANDARD,
    2015: _STANDARD,
    2020: _STANDARD,
    2025: _STANDARD,
}

# Grid and hotspot settings
CELL = 240          # grid cell size in metres (8 x 8 Landsat pixels)
MIN_SHARE = 0.25    # drop edge cells smaller than 25% of a full cell
BAND = 480          # Gi* fixed distance band in metres
ZONE_LEVEL = 2      # Gi_Bin threshold for zones (2 = 95% confidence)

# Maps
SHOW_TITLE = True   # set False to remove the title above the six-panel maps


def ensure_dirs():
    for d in (OUT_DIR, OUT_DIR / "grid", OUT_DIR / "hotspots", FIG_DIR):
        d.mkdir(parents=True, exist_ok=True)
