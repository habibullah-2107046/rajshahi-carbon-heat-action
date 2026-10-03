# Step 1 – Input data

## What you need

| Input | Source | Used in |
|---|---|---|
| City boundary (polygon shapefile) | `data/RCC_boundary/` in this repository, or your own city | All steps |
| LULC rasters for 2000, 2005, 2010, 2015, 2020, 2025 | Your own classification of Landsat imagery (see below) | Step 2 |
| Landsat Collection 2 Level-2 scenes (March–May) | Accessed directly in Google Earth Engine; no download needed | Step 3 |

All Landsat data are free from the U.S. Geological Survey.

## 1. City boundary

The boundary of Rajshahi City Corporation (46.92 km²) is provided in `data/`. It is projected in **WGS 1984 UTM Zone 45N (EPSG:32645)**. Every layer you use must be in the same coordinate system.

A shapefile is made of several files with the same name. Keep all of them together: `.shp`, `.shx`, `.dbf`, `.prj` (and optionally `.cpg`, `.sbn`, `.sbx`). The `.prj` file is essential because it stores the projection.

## 2. LULC rasters

The study used Landsat scenes from **February** of each benchmark year (path/row 138/043), classified with a support vector machine into five classes:

| Class | Includes |
|---|---|
| Water body | Rivers, ponds, canals, marshes |
| Vegetation | Trees, orchards, urban green space |
| Crop land | Agricultural land and grassland |
| Built-up area | Buildings, roads, other infrastructure |
| Bare / char land | Open soil, playgrounds, char and sand bars |

| Year | Sensor | Acquisition date |
|---|---|---|
| 2000 | Landsat 5 TM | 11 Feb 2000 |
| 2005 | Landsat 5 TM | 24 Feb 2005 |
| 2010 | Landsat 5 TM | 06 Feb 2010 |
| 2015 | Landsat 8 OLI | 04 Feb 2015 |
| 2020 | Landsat 8 OLI | 02 Feb 2020 |
| 2025 | Landsat 9 OLI-2 | 07 Feb 2025 |

**Requirements for your LULC rasters**

1. Integer raster with one value per class.
2. An attribute table with a text field **`CLASS_NAME`** containing the class name. The scripts read the class from this text, not from the code number, because class codes may differ between years (in our data, code 1 meant *Vegetation* in most years but *Crop land* in 2005).
3. The class names must contain one of these words (upper or lower case): `water`, `veg`, `settle` or `built`, `bare` or `char`, `crop`.
4. Cell size 30 m, projection EPSG:32645.

The classified rasters are not stored in this repository because of their size. They are available from the authors on reasonable request.

If you are working on another city, you can classify Landsat imagery yourself in ArcMap (Image Classification toolbar → Training Sample Manager → Support Vector Machine), QGIS (Semi-Automatic Classification Plugin) or Google Earth Engine (`ee.Classifier.libsvm`). Report the overall accuracy and kappa coefficient from an independent validation sample.

## 3. Landsat scenes for temperature

No download is needed. The Google Earth Engine script in Step 3 selects all cloud-screened scenes from March to May of each year automatically.

## Checklist before moving on

- [ ] Boundary shapefile with `.prj` is in `01_boundary/`
- [ ] Six LULC rasters are in `02_LULC_existing/` and each has a `CLASS_NAME` field
- [ ] All layers are in EPSG:32645 (check in ArcMap: right-click layer → Properties → Source)
