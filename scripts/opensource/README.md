# Open-source scripts (Option B)

A free Python version of the workflow that needs **no ArcGIS licence**. It reproduces the ArcMap results: on the Rajshahi data, the carbon–heat zone areas from `04_hotspot.py` are identical to the ArcMap output for all six years, and the hotspot classes agree for 99.8–100% of grid cells.

| Script | Step | What it does |
|---|---|---|
| `config.py` | – | **All paths and settings. Edit this file first.** |
| `02_lsce.py` | 2 | Clips LULC rasters to the city and calculates TE, TA and NE |
| `03_grid.py` | 4 | Builds the 240 m grid and calculates LSCE, LST, NLST, NDVI, NDBI per cell |
| `04_hotspot.py` | 5 | Gi* hotspots (480 m band, FDR) and carbon–heat stress zones |
| `05_statistics.py` | 6 | Correlations, regression, source–sink temperature gap, two charts |
| `06_maps.py` | 6 | Five six-panel publication maps |

Step 3 (LST, NDVI, NDBI) is done in Google Earth Engine: see [`../gee/`](../gee/).

## Setup

1. Install Python 3.9 or newer.
2. From the repository root, install the packages:
   ```bash
   pip install -r requirements.txt
   ```
   On Windows, if `rasterio` or `geopandas` fail to install with pip, use [Miniconda](https://docs.conda.io/en/latest/miniconda.html):
   ```bash
   conda create -n carbonheat -c conda-forge python=3.11 geopandas rasterio rasterstats scipy matplotlib
   conda activate carbonheat
   ```
3. Open `config.py` and set:
   - `PROJECT`: your project folder
   - `BOUNDARY`: your city boundary shapefile
   - `LULC_PATTERN`: the file name of your LULC rasters, e.g. `LULC_{year}.tif`
   - `CLASS_CODES`: which raster value means which class **for each year**

## Run

```bash
cd scripts/opensource
python 02_lsce.py
python 03_grid.py
python 04_hotspot.py
python 05_statistics.py
python 06_maps.py
```

Each script prints a short summary. Compare it with the *Expected output* in the matching guide in [`docs/`](../../docs/).

## About the class codes

GeoTIFF files do not store class names, so `config.py` tells the scripts what each value means. The Rajshahi rasters use the same codes in every year except 2005:

| Value | 2000, 2010, 2015, 2020, 2025 | 2005 |
|---|---|---|
| 0 | water | water |
| 1 | vegetation | crop |
| 2 | builtup | vegetation |
| 3 | bare | bare |
| 4 | crop | builtup |

Always check your own legend; a wrong code silently changes the carbon balance.

## About the Gi* calculation

`04_hotspot.py` calculates the Gi* z-score with the standard formula used by ArcGIS (binary weights within the distance band, including the cell itself), converts it to a two-sided p-value and applies the Benjamini–Hochberg false discovery rate at the 90%, 95% and 99% levels. Generic library functions that compute Gi* as a ratio of sums are not suitable here because LSCE contains negative values, which would reverse the sign of the result in years when the city is a net sink.
