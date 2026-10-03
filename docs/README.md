# Step-by-step guides

Follow the guides in order. Each guide explains **what** the step does, **why** it is needed, **how** to run it, and **what output you should see**.

| # | Guide | What you will produce |
|---|---|---|
| 1 | [Input data](01_data.md) | Study boundary, LULC rasters and folder structure |
| 2 | [LULC and land-specific carbon emission](02_lulc_and_lsce.md) | Clipped LULC maps and LSCE totals per year |
| 3 | [LST, NDVI and NDBI in Google Earth Engine](03_lst_in_gee.md) | Six 3-band GeoTIFFs (LST, NDVI, NDBI) |
| 4 | [Grid integration](04_grid_integration.md) | 240 m grid with all variables for every year |
| 5 | [Hotspots and carbon–heat zones](05_hotspot_and_zones.md) | Gi* hotspot layers and stress-zone areas |
| 6 | [Statistics and maps](06_statistics_and_maps.md) | Correlation tables and publication figures |
| – | [FAQ and troubleshooting](FAQ_troubleshooting.md) | Solutions to common errors |

## Two ways to run steps 2, 4 and 5

- **Option A – ArcMap** (`scripts/arcmap/`): the scripts used in the published study. Requires ArcMap 10.x with Spatial Analyst. Scripts are run in the ArcMap Python window (Python 2.7).
- **Option B – Open source** (`scripts/opensource/`): the same calculations with free Python packages. Requires Python 3.9+ and `pip install -r requirements.txt`.

Steps 3 (Google Earth Engine) and 6 (statistics and maps) are the same for both options.

## Recommended working folder

Keep the same structure on your computer as in the repository. Avoid spaces in folder names (for example use `C:\RCC_Chapter` rather than `C:\My Files\RCC Chapter`), because ArcMap's GRID raster format does not handle spaces in paths reliably.

```
RCC_project/
├── 01_boundary/            ← city boundary shapefile
├── 02_LULC_existing/       ← your classified LULC rasters (one per year)
├── 03_Landsat_hot_season/  ← GeoTIFFs exported from Google Earth Engine
├── 04_outputs/             ← everything the scripts create
└── 05_figures/             ← final maps and charts
```
