# Step 3 – Land surface temperature, NDVI and NDBI in Google Earth Engine

## What this step does

For each benchmark year, the script:

1. Finds all Landsat Collection 2 Level-2 scenes over the city from **1 March to 31 May** (the pre-monsoon hot season) with scene cloud cover below 30%.
2. Removes clouds, dilated clouds and cloud shadows with the `QA_PIXEL` band.
3. Converts the surface-temperature band to °C: `LST = DN × 0.00341802 + 149.0 − 273.15`.
4. Calculates NDVI and NDBI from surface reflectance (`reflectance = DN × 0.0000275 − 0.2`).
5. Takes the **median** of all clean scenes (a seasonal composite).
6. Exports a 3-band GeoTIFF per year to Google Drive: **Band 1 = LST, Band 2 = NDVI, Band 3 = NDBI**.

| Years | Sensor collection | Red | NIR | SWIR1 | Thermal |
|---|---|---|---|---|---|
| 2000–2010 | Landsat 5 TM (`LT05/C02/T1_L2`) | SR_B3 | SR_B4 | SR_B5 | ST_B6 |
| 2000 only (added) | Landsat 7 ETM+ (`LE07/C02/T1_L2`) | SR_B3 | SR_B4 | SR_B5 | ST_B6 |
| 2015–2025 | Landsat 8 and 9 (`LC08`, `LC09/C02/T1_L2`) | SR_B4 | SR_B5 | SR_B6 | ST_B10 |

Landsat 7 was added for 2000 because the only Landsat 5 scene was cloudy over the city. Landsat 7 is safe for 2000 because its scan-line corrector failed only in 2003.

## How to run

### 3.1 Create a free account
Go to <https://code.earthengine.google.com> and sign in. On first use, register a Cloud project for **noncommercial / research** use.

### 3.2 Upload the city boundary
1. In the Code Editor, open the **Assets** tab (top left) → **NEW → Shape files**.
2. Select the `.shp`, `.shx`, `.dbf` and `.prj` files together.
3. Name the asset `RCC_boundary` and click **UPLOAD**. Progress appears in the **Tasks** tab.
4. When finished, click the asset and copy its **Table ID**, for example `projects/your-project/assets/RCC_boundary`.

### 3.3 Run the script
1. Open `scripts/gee/01_lst_ndvi_ndbi.js`, copy everything and paste it into the Code Editor.
2. Replace the asset path on the first line of the settings with your Table ID.
3. Click **Run**.

### 3.4 Export
1. Open the **Tasks** tab. Six tasks appear, one per year.
2. Click **RUN** on each, then **Run** in the dialog box.
3. The files appear in the Google Drive folder **RCC_LST**. Download them into `03_Landsat_hot_season/`.

## Expected output (Rajshahi)

The **Console** lists the scenes used and the temperature statistics.

| Year | Scenes (dates) | Mean LST (°C) | Max LST (°C) |
|---|---|---|---|
| 2000 | 7 Apr (L7), 15 Apr (L5), 9 May (L7) | 37.31 | 46.69 |
| 2005 | 13 Apr, 15 May, 31 May | 34.68 | 40.84 |
| 2010 | 11 Apr | 39.34 | 46.23 |
| 2015 | 8 Mar, 24 Mar, 11 May, 27 May | 35.18 | 44.02 |
| 2020 | 21 Mar, 6 Apr, 8 May | 37.52 | 47.17 |
| 2025 | 3, 11, 19, 27 Mar | 34.05 | 42.37 |

## Important: comparing years

The scene dates differ between years (2025 only had clear scenes in March, which is cooler than April–May). Therefore, **do not compare absolute LST between years**. The later steps use:

- **Normalised LST** = (LST − LST_min) / (LST_max − LST_min) within each year, and
- **hotspot analysis**, which compares cells within the same year.

## Check before moving on

- Open one GeoTIFF in ArcMap or QGIS. It should have three bands named LST, NDVI and NDBI and should cover the whole city without large empty areas.
- If one year has holes, clouds were present; see the [FAQ](FAQ_troubleshooting.md).
