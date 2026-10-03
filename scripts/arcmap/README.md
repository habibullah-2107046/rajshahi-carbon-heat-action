# ArcMap scripts (Option A)

These are the scripts used in the study. They run inside **ArcMap 10.x** (tested with 10.8) and need the **Spatial Analyst** extension.

| Script | Step | Guide |
|---|---|---|
| `02_lsce.py` | Area of each LULC class and land-specific carbon emission | [docs/02](../../docs/02_lulc_and_lsce.md) |
| `03_grid.py` | 240 m grid with LSCE, LST, NLST, NDVI, NDBI | [docs/04](../../docs/04_grid_integration.md) |
| `04_hotspot.py` | Gi* hotspots and carbon–heat stress zones | [docs/05](../../docs/05_hotspot_and_zones.md) |

## How to run any script

1. Open the script in Notepad and change `FOLDER` (and `BOUNDARY` in `03_grid.py`) in the **SETTINGS** block at the top. Keep the `r` before the quotation marks: `r"C:\RCC_project"`.
2. In ArcMap open **Geoprocessing → Python**.
3. Right-click inside the Python window → **Load…** → select the script.
4. Click at the end of the loaded code and press **Enter** (twice if needed).
5. Wait until `DONE!` appears (or `>>>` returns).

## Tips

- ArcMap uses **Python 2.7**. Keep comments in English and always divide with decimals (`44.0/12.0`).
- Remove output layers from the map before running a script again, otherwise the files are locked.
- If a raster cannot be opened, move the project to a folder path without spaces.
- More solutions: [FAQ](../../docs/FAQ_troubleshooting.md).

The Google Earth Engine script for Step 3 is in [`../gee/`](../gee/), and the free Python version of these steps is in [`../opensource/`](../opensource/).
