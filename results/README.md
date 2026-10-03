# Results: data dictionary

All values refer to Rajshahi City Corporation (46.93 km²). Years are the six benchmark years 2000, 2005, 2010, 2015, 2020 and 2025.

## RCC_LULC_area.csv
Area of each land-use/land-cover class (km²) per year.

## RCC_LSCE_summary.csv
| Column | Meaning | Unit |
|---|---|---|
| TE_1e3_tCO2_yr | Total emission (sum of source classes: built-up, crop land) | 10³ t CO₂ yr⁻¹ |
| TA_1e3_tCO2_yr | Total absorption (sum of sink classes: vegetation, water, bare/char land) | 10³ t CO₂ yr⁻¹ |
| NE_1e3_tCO2_yr | Net emission = TE + TA; negative = net sink, positive = net source | 10³ t CO₂ yr⁻¹ |

## RCC_grid_values.csv
One row per 240 m grid cell (861 cells). `YYYY` stands for the year.

| Column | Meaning | Unit |
|---|---|---|
| GID | Grid cell identifier | – |
| AREA_KM2 | Cell area (edge cells are smaller) | km² |
| LSCE_YYYY | Land-specific carbon emission density; +272.1 = fully built-up, −236.5 = fully vegetated | t CO₂ km⁻² yr⁻¹ |
| LST_YYYY | Mean pre-monsoon land surface temperature | °C |
| NLST_YYYY | Normalised LST within the year (0 = coolest cell, 1 = hottest cell) | – |
| NDVI_YYYY | Mean Normalised Difference Vegetation Index | – |
| NDBI_YYYY | Mean Normalised Difference Built-up Index | – |

## hotspot_zone_summary.csv
Area (km²) of each carbon–heat stress zone per year, based on Getis-Ord Gi* at 95% confidence with FDR correction. Areas sum to 46.5 km² because edge cells smaller than 25% of a full cell were excluded.

## RCC_LSCE_LST_statistics.csv
| Column | Meaning |
|---|---|
| r_LSCE_LST, rho_LSCE_LST | Pearson and Spearman correlation between LSCE and LST |
| R2_LSCE | Variance in LST explained by LSCE alone |
| r_NDVI_LST, r_NDBI_LST | Pearson correlation of NDVI and NDBI with LST |
| R2_NDVI_NDBI | R² of the regression LST ~ NDVI + NDBI |
| r_LSCE_NDVI, r_LSCE_NDBI | Correlation of LSCE with the spectral indices |
| LST_source, LST_sink | Mean LST of net-source (LSCE > 0) and net-sink (LSCE < 0) cells (°C) |
| dLST | LST_source − LST_sink (°C) |
| n_source | Number of net-source cells (out of 861) |
| meanLSCE | Mean LSCE density of all cells (t CO₂ km⁻² yr⁻¹) |

Correlation values are reported as effect sizes. Because neighbouring cells are spatially autocorrelated, conventional p-values would overstate significance and are not reported.
