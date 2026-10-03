# Step 6 – Statistics and publication maps

## Statistics (`05_statistics.py`)

For each year, using all 861 grid cells:

| Measure | What it tells you |
|---|---|
| Pearson r and Spearman ρ between LSCE and LST | Whether carbon-emitting cells are also hotter |
| R² of LST ~ NDVI + NDBI | How much of the temperature pattern is explained by greenness and built-up intensity |
| ΔLST = mean LST of source cells − mean LST of sink cells | The temperature penalty of being a carbon source |
| Share of net-source cells | How much of the city emits more carbon than it absorbs |

Run:
```bash
python 05_statistics.py
```
Output: `RCC_LSCE_LST_statistics.csv`, `Fig_LSCE_vs_LST_scatter.png`, `Fig_correlation_and_dLST.png`.

### Expected values (Rajshahi)

| Year | r (LSCE–LST) | r (NDBI–LST) | ΔLST (°C) | Net-source cells |
|---|---|---|---|---|
| 2000 | 0.19 | 0.75 | 0.55 | 35.2% |
| 2005 | 0.51 | 0.65 | 1.08 | 38.6% |
| 2010 | 0.18 | 0.85 | 0.40 | 41.5% |
| 2015 | 0.58 | 0.86 | 1.42 | 64.0% |
| 2020 | 0.42 | 0.78 | 1.35 | 49.6% |
| 2025 | 0.51 | 0.83 | 1.33 | 67.0% |

> Neighbouring cells are spatially autocorrelated, so conventional p-values overstate significance. Report r, ρ, R² and ΔLST as effect sizes.

## Maps (`06_maps.py`)

The script reads the grid shapefile and produces five six-panel maps (2000–2025) in a publication style: north arrow and scale bar in every panel, coordinates on all four sides, legend or colour bar, 300 dpi.

| Output | Content |
|---|---|
| `Map1_Carbon_Heat_Zones.png` | Five stress zones |
| `Map2_LSCE_Hotspots.png` | LSCE hot and cold spots |
| `Map3_LST_Hotspots.png` | LST hot and cold spots |
| `Map4_LSCE_Density.png` | LSCE density (diverging colours, 0 = neutral) |
| `Map5_Normalized_LST.png` | Normalised LST |

Run:
```bash
python 06_maps.py
```

To remove the title from the maps (for example when the caption is given in the paper), set `SHOW_TITLE = False` in `config.py`.
