# Step 2 – LULC clipping and land-specific carbon emission (LSCE)

## What this step does

1. Clips each LULC raster to the city boundary.
2. Measures the area of each class.
3. Converts the areas into carbon emission or absorption with fixed coefficients.

## The method in plain words

Each land-cover type either releases carbon (source) or absorbs it (sink). The amount per square metre is given by a coefficient:

| Class | Coefficient δ (kg C m⁻² yr⁻¹) | Role |
|---|---|---|
| Water body | −0.0459 | Sink |
| Vegetation | −0.0645 | Sink |
| Crop land | +0.0497 | Source |
| Built-up area | +0.0742 | Source |
| Bare / char land | −0.0527 | Sink |

For each class:

```
E_i = S_i × δ_i × 44/12
```

- `S_i` = area of the class
- `δ_i` = coefficient of the class
- `44/12` converts carbon (C) to carbon dioxide (CO₂)

With area in km², the result is in **10³ t CO₂ per year**.

- **Total emission (TE)** = sum of positive values
- **Total absorption (TA)** = sum of negative values
- **Net emission (NE)** = TE + TA. A negative NE means the city is still a net sink.

> **Unit note:** the coefficients are in **kg C m⁻² yr⁻¹** (equivalent to 10 t C ha⁻¹ yr⁻¹ per 1 kg C m⁻² yr⁻¹). Using the wrong unit changes the results by a factor of 10.

---

## Option A – ArcMap

### 2A.1 Clip the LULC rasters

1. Enable the extension: **Customize → Extensions → Spatial Analyst** ✔.
2. Set the environment once: **Geoprocessing → Environments**
   - *Processing Extent → Extent*: same as the boundary layer
   - *Processing Extent → Snap Raster*: the 2000 LULC raster (keeps every year on the same pixel grid)
   - *Raster Analysis → Cell Size*: 30
3. Open **ArcToolbox → Spatial Analyst Tools → Extraction → Extract by Mask**, right-click → **Batch**.
4. Add six rows (one per year). Input raster = LULC raster, mask = boundary, output = `04_outputs\RCC_LULC_2000.tif` and so on. Click **OK**.

**Check:** all six outputs should have exactly the same number of pixels. In our study every year had **52,145 pixels** (46.93 km²). If one year differs, it was not snapped; clip it again with the Snap Raster set.

### 2A.2 Calculate LSCE

1. Open `scripts/arcmap/02_lsce.py` in Notepad and set the `folder` path at the top.
2. In ArcMap: **Geoprocessing → Python**. Right-click in the Python window → **Load…** → choose the script → press **Enter**.

---

## Option B – Open source

```bash
cd scripts/opensource
# edit the paths in config.py first
python 02_lsce.py
```

The script clips the rasters with the boundary, counts the pixels of each class and writes the same tables as the ArcMap version.

---

## Expected output (Rajshahi)

The script prints one line per year and saves `RCC_LSCE_by_class.csv` and `RCC_LSCE_summary.csv`.

```
2000 | Pixels=52145 | Area=46.93 km2 | TE=4.76 | TA=-6.40 | NE=-1.64
2005 | Pixels=52145 | Area=46.93 km2 | TE=5.08 | TA=-6.10 | NE=-1.02
2010 | Pixels=52145 | Area=46.93 km2 | TE=5.39 | TA=-5.90 | NE=-0.52
2015 | Pixels=52145 | Area=46.93 km2 | TE=7.01 | TA=-4.36 | NE=2.65
2020 | Pixels=52145 | Area=46.93 km2 | TE=6.02 | TA=-5.39 | NE=0.63
2025 | Pixels=52145 | Area=46.93 km2 | TE=7.70 | TA=-3.98 | NE=3.71
```

Values are in 10³ t CO₂ yr⁻¹. The sign change of NE between 2010 and 2015 is the key finding: the city moved from a net carbon sink to a net carbon source.

Problems? See [FAQ](FAQ_troubleshooting.md).
