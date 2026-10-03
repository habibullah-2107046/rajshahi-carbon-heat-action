# Step 5 – Hotspot analysis and carbon–heat stress zones

## What is a hotspot?

A single hot cell could be random. A **hotspot** is a group of neighbouring cells whose values are high together, more than would be expected by chance. The **Getis-Ord Gi\*** statistic tests this for every cell and gives a confidence level.

| Gi_Bin | Meaning |
|---|---|
| +3 / +2 / +1 | Hotspot at 99% / 95% / 90% confidence |
| 0 | Not significant |
| −1 / −2 / −3 | Coldspot at 90% / 95% / 99% confidence |

## Settings used

| Setting | Value |
|---|---|
| Neighbourhood | Fixed distance band of 480 m (two cell widths) |
| Distance | Euclidean |
| Weights | Row standardisation (recommended for a grid imposed on the data) |
| Multiple testing | False Discovery Rate (FDR) correction |

The analysis is run separately for LSCE and for LST in each year (12 runs).

## From hotspots to stress zones

Using the 95% level (Gi_Bin ≥ 2 or ≤ −2), each cell is assigned to a zone:

| Zone code | Zone | Rule |
|---|---|---|
| 1 | **Dual stress** | LSCE hotspot **and** LST hotspot |
| 2 | Carbon hotspot only | LSCE hotspot, LST not a hotspot |
| 3 | Heat hotspot only | LST hotspot, LSCE not a hotspot |
| 4 | **Cool sink** | LSCE coldspot **and** LST coldspot |
| 0 | Not significant | All other cells |

## How to run

**Option A – ArcMap:** set the `folder` path in `scripts/arcmap/04_hotspot.py`, remove the grid layer from the map, then load and run the script. The tool *Hot Spot Analysis (Getis-Ord Gi\*)* is part of the Spatial Statistics toolbox and needs no extra licence.

**Option B – Open source:**
```bash
python 04_hotspot.py
```
The open-source version calculates Gi* with the same formula as ArcGIS. On the Rajshahi data it gives identical zone areas to ArcMap in all six years.

## Expected output (Rajshahi)

`hotspot_zone_summary.csv` (areas in km²):

| Year | Dual stress | Carbon only | Heat only | Cool sink | Not significant |
|---|---|---|---|---|---|
| 2000 | 1.06 | 10.43 | 2.82 | 0.66 | 31.53 |
| 2005 | 2.40 | 7.17 | 3.47 | 3.35 | 30.11 |
| 2010 | 0.00 | 10.51 | 2.67 | 0.75 | 32.58 |
| 2015 | 4.32 | 6.43 | 0.52 | 2.22 | 33.00 |
| 2020 | 2.25 | 9.40 | 1.69 | 1.93 | 31.24 |
| 2025 | 2.18 | 9.59 | 1.95 | 3.53 | 29.24 |

The grid shapefile receives new fields: `HSC_YYYY` (carbon Gi_Bin), `HSH_YYYY` (heat Gi_Bin) and `ZONE_YYYY` (zone code).

> **Note:** In the ArcMap Python window the printed summary sometimes does not appear even though the script finished. If `>>>` returns and the twelve `HS_` layers are added to the map, the run was successful; open `hotspot_zone_summary.csv` to see the results.

The two versions agree for 99.8–100% of cells; a difference of one or two cells at a significance boundary is normal.
