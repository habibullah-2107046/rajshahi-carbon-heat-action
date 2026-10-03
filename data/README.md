# Data

## Included

| Folder | Content |
|---|---|
| `RCC_boundary/` | Boundary of Rajshahi City Corporation (polygon shapefile, 46.92 km²), projection WGS 1984 UTM Zone 45N (EPSG:32645) |

Keep all files of the shapefile together (`.shp`, `.shx`, `.dbf`, `.prj`, `.cpg`). To use it in the scripts, copy the folder to `01_boundary/RCC/` in your project folder and rename it to `RCC`, or change the `BOUNDARY` path in the settings.

For Google Earth Engine, upload the same files as a table asset (see [docs/03_lst_in_gee.md](../docs/03_lst_in_gee.md)).

## Not included

| Data | How to obtain |
|---|---|
| Classified LULC rasters (2000–2025) | Available from the authors on reasonable request (habibullah.ruet.urp@gmail.com) |
| Landsat scenes for LULC classification | Free from [USGS EarthExplorer](https://earthexplorer.usgs.gov/), path/row 138/043, dates in [docs/01_data.md](../docs/01_data.md) |
| Landsat scenes for LST | Accessed directly in Google Earth Engine by `scripts/gee/01_lst_ndvi_ndbi.js`; no download needed |

## Processed results

The grid values for every year (LSCE, LST, NLST, NDVI, NDBI) are in [`results/RCC_grid_values.csv`](../results/RCC_grid_values.csv). With this file you can rerun the statistics without repeating the earlier steps.
