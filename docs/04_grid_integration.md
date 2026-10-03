# Step 4 – Grid integration

## Why a grid?

A single 30 m pixel belongs to only one land-cover class, so its LSCE can take only five possible values. That is not enough to describe a mixed neighbourhood. A regular grid solves this: each grid cell contains many pixels of different classes, and its value reflects the real mixture. The grid also puts LSCE, LST, NDVI and NDBI into the same units of space so they can be compared.

## Grid design

| Setting | Value | Reason |
|---|---|---|
| Cell size | 240 m × 240 m | Exactly 8 × 8 Landsat pixels, so no pixel is split between cells; close to the 350 m scale at which urban carbon emissions show the strongest spatial autocorrelation (Liu et al., 2024) |
| Alignment | Snapped to the LULC pixel grid | Keeps pixels and cells aligned |
| Edge cells | Removed if smaller than 25% of a full cell | Very small slivers give unreliable averages |
| Result | 861 cells covering 46.5 km² | |

## Variables calculated for every cell and year

| Field | Meaning | Unit |
|---|---|---|
| `LSCE_YYYY` | Area-weighted carbon emission density | t CO₂ km⁻² yr⁻¹ |
| `LST_YYYY` | Mean land surface temperature | °C |
| `NLST_YYYY` | Normalised LST within the year (0 to 1) | – |
| `NDVI_YYYY` | Mean NDVI | – |
| `NDBI_YYYY` | Mean NDBI | – |

LSCE density is calculated as:

```
LSCE density = (Σ area_i × δ_i / Σ area_i) × 1000 × 44/12
```

A fully built-up cell gives **+272.1** and a fully vegetated cell gives **−236.5** t CO₂ km⁻² yr⁻¹. Mixed cells fall in between.

## How to run

**Option A – ArcMap:** set the `folder` and `boundary` paths in `scripts/arcmap/03_grid.py`, then load and run it in the ArcMap Python window. Close or remove any grid layer from the map before running, otherwise the file is locked.

**Option B – Open source:**
```bash
python 03_grid.py
```

## Expected output (Rajshahi)

```
Grid cells: 861
2000 | missing cells=0 | LSCE -236.5 to 272.1 t/km2/yr | cell LST 28.31 to 42.67 C
2005 | missing cells=0 | LSCE -236.5 to 272.1 t/km2/yr | cell LST 27.81 to 39.26 C
2010 | missing cells=0 | LSCE -236.5 to 272.1 t/km2/yr | cell LST 30.17 to 45.18 C
2015 | missing cells=0 | LSCE -202.8 to 272.1 t/km2/yr | cell LST 27.27 to 43.29 C
2020 | missing cells=0 | LSCE -236.5 to 272.1 t/km2/yr | cell LST 27.99 to 46.73 C
2025 | missing cells=0 | LSCE -228.6 to 272.1 t/km2/yr | cell LST 27.61 to 42.13 C
DONE! Grid and CSV saved in 04_outputs\grid
```

Outputs: `04_outputs/grid/RCC_grid_240m.shp` and `RCC_grid_values.csv` (the same file is in `results/`).

**"missing cells" must be 0 or very small.** A large number means the temperature image has gaps for that year (see the [FAQ](FAQ_troubleshooting.md)).
