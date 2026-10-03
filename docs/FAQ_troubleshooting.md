# FAQ and troubleshooting

These are the problems we met while doing the study, with their solutions.

### ArcMap: `ERROR 000732: Dataset ... does not exist or is not supported`
**Cause 1 – spaces in the folder path.** ArcMap's GRID raster format cannot always open files in a path with spaces (e.g. `Paper Submission\Book Chapter`).
**Fix:** move the project to a path without spaces, e.g. `C:\RCC_project`, or save rasters as `.tif`.

**Cause 2 – the raster is inside a sub-folder.** Extract by Mask sometimes saves a GRID raster inside a folder of the same name: `04_outputs\RCC_LULC_2000\rcc_lulc_2000`. The script then finds the folder instead of the raster.
**Fix:** the scripts in this repository search both locations automatically. If you write your own, point to the inner raster.

### ArcMap: `DescribeData: Method meanCellWidth does not exist`
**Cause:** the path points to a folder, not a raster (see Cause 2 above).
**Fix:** use `arcpy.Raster(path).meanCellWidth`, which is what the repository scripts do.

### ArcMap: `ERROR 000865: Input value raster ...\Band_1 does not exist`
**Cause:** GeoTIFFs exported from Earth Engine keep the band names (`LST`, `NDVI`, `NDBI`) instead of `Band_1`, `Band_2`, `Band_3`.
**Fix:** the scripts read the real band names with `arcpy.Describe(tif).children`.

### ArcMap: `RuntimeError: The field is not nullable`
**Cause:** some grid cells received no value. Two reasons: (a) the temperature GeoTIFF stores empty pixels as **NaN**, which ArcMap does not treat as NoData, so the mean of any edge cell becomes NaN; (b) a year has cloud gaps.
**Fix:** the scripts convert NaN pixels to NoData with `Con(band > -1000, band)` before averaging and write −9999 for any remaining empty cell. Check the "missing cells" count; it should be 0.

### Almost all cells are missing for one year
**Cause:** the temperature composite for that year is mostly masked by clouds. In our case, 850 of 861 cells were empty in 2000 because the only Landsat 5 scene was cloudy over the city.
**Fix:** add more scenes. For 2000 we added Landsat 7 ETM+ (`LANDSAT/LE07/C02/T1_L2`). For other years you can widen the date window slightly or raise the scene cloud limit; the pixel cloud mask still removes the clouds.

### One year has a few more pixels than the others after clipping
**Cause:** the raster was clipped without a Snap Raster, so it sits on a slightly shifted grid.
**Fix:** set Geoprocessing → Environments → Snap Raster to the 2000 LULC raster and clip again.

### ArcMap: "cannot acquire a lock" or the script cannot overwrite a file
**Fix:** remove the layer from the map (right-click → Remove) or close ArcMap, then run again.

### ArcMap: the Python window shows no printed results
If `>>>` returns and no red error appears, the script finished. Check the output files directly.

### Why does Python 2 give `44/12 = 3`?
ArcMap uses Python 2.7, where dividing two integers gives an integer. Always write `44.0/12.0`.

### My class codes are different every year
That is common. The scripts identify classes by the **text** in the `CLASS_NAME` field, not by the code number. Make sure each class name contains one of: `water`, `veg`, `settle`/`built`, `bare`/`char`, `crop`.

### Can I compare LST between years?
Not directly, if the scene dates differ between years. Use normalised LST and the within-year hotspots, as explained in [Step 3](03_lst_in_gee.md).

### Where do I ask a question?
Open an **Issue** in this repository or email the corresponding author.
