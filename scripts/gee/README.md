# Google Earth Engine script

`01_lst_ndvi_ndbi.js` creates pre-monsoon (March–May) median composites of land surface temperature, NDVI and NDBI for every benchmark year and exports one 3-band GeoTIFF per year.

1. Upload your city boundary as an Earth Engine asset.
2. Copy the script into the [Code Editor](https://code.earthengine.google.com).
3. Change `BOUNDARY_ASSET` (and, for another city, `WRS_PATH`, `WRS_ROW` and the season dates).
4. Click **Run**, check the Console, then start the export tasks in the **Tasks** tab.

Full instructions: [docs/03_lst_in_gee.md](../../docs/03_lst_in_gee.md).
