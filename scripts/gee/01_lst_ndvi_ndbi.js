/*******************************************************************************
 * 01_lst_ndvi_ndbi.js  —  Google Earth Engine script
 *
 * Study : Carbon-Conscious Urban Heat Action in Rajshahi, Bangladesh
 * Step  : 3 of 6 (see docs/03_lst_in_gee.md)
 *
 * WHAT IT DOES
 *   For each benchmark year it builds a pre-monsoon (March–May) median
 *   composite of cloud-masked Landsat Collection 2 Level-2 scenes and exports
 *   one 3-band GeoTIFF:  Band 1 = LST (°C), Band 2 = NDVI, Band 3 = NDBI.
 *
 * HOW TO USE
 *   1. Upload your city boundary as an asset (Assets > NEW > Shape files).
 *   2. Paste the asset Table ID into BOUNDARY_ASSET below.
 *   3. Click Run. Check the Console, then start the six export tasks
 *      in the Tasks tab. Files go to the Google Drive folder EXPORT_FOLDER.
 ******************************************************************************/

// ============================== SETTINGS ===================================
var BOUNDARY_ASSET = 'projects/ee-2107046habibullah/assets/RCC_boundary';
var YEARS          = [2000, 2005, 2010, 2015, 2020, 2025];
var WRS_PATH       = 138;          // Landsat path covering the city
var WRS_ROW        = 43;           // Landsat row covering the city
var START_MMDD     = '-03-01';     // start of hot season
var END_MMDD       = '-06-01';     // end of hot season (exclusive)
var MAX_CLOUD      = 30;           // scene-level cloud cover limit (%)
var ADD_L7_YEARS   = [2000];       // years where Landsat 7 is added (only before 2003!)
var EXPORT_FOLDER  = 'RCC_LST';
var EXPORT_CRS     = 'EPSG:32645'; // WGS 84 / UTM zone 45N
// ===========================================================================

var city = ee.FeatureCollection(BOUNDARY_ASSET);
var region = city.geometry();
Map.centerObject(city, 12);

// Collect raw scenes for one year
function getRaw(year) {
  var start = year + START_MMDD;
  var end = year + END_MMDD;
  var filt = function (c) {
    return c.filterBounds(region)
      .filterDate(start, end)
      .filter(ee.Filter.eq('WRS_PATH', WRS_PATH))
      .filter(ee.Filter.eq('WRS_ROW', WRS_ROW))
      .filter(ee.Filter.lt('CLOUD_COVER', MAX_CLOUD));
  };
  if (year <= 2012) {
    var col = filt(ee.ImageCollection('LANDSAT/LT05/C02/T1_L2'));
    if (ADD_L7_YEARS.indexOf(year) !== -1) {
      col = col.merge(filt(ee.ImageCollection('LANDSAT/LE07/C02/T1_L2')));
    }
    return col;
  }
  var l8 = filt(ee.ImageCollection('LANDSAT/LC08/C02/T1_L2'));
  var l9 = filt(ee.ImageCollection('LANDSAT/LC09/C02/T1_L2'));
  return l8.merge(l9);
}

// Cloud mask + scaling + LST for a given set of band names
function makePrep(redB, nirB, swirB, stB) {
  return function (img) {
    var qa = img.select('QA_PIXEL');
    var clear = qa.bitwiseAnd(1 << 1).eq(0)        // dilated cloud
      .and(qa.bitwiseAnd(1 << 3).eq(0))            // cloud
      .and(qa.bitwiseAnd(1 << 4).eq(0));           // cloud shadow
    var sr = img.select([redB, nirB, swirB])
      .multiply(0.0000275).add(-0.2)
      .rename(['RED', 'NIR', 'SWIR1']);
    var lst = img.select(stB)
      .multiply(0.00341802).add(149.0)             // to Kelvin
      .subtract(273.15)                            // to Celsius
      .rename('LST');
    var valid = img.select(stB).gt(0);
    return ee.Image(lst.addBands(sr).updateMask(clear).updateMask(valid));
  };
}

YEARS.forEach(function (y) {
  var raw = getRaw(y);

  // Scene information for the methods table
  print(y + ' | scene count', raw.size());
  print(y + ' | dates', raw.aggregate_array('DATE_ACQUIRED'));
  print(y + ' | sensors', raw.aggregate_array('SPACECRAFT_ID'));
  print(y + ' | cloud %', raw.aggregate_array('CLOUD_COVER'));

  // Landsat 5 and 7 share band names; Landsat 8 and 9 share band names
  var prep = (y <= 2012)
    ? makePrep('SR_B3', 'SR_B4', 'SR_B5', 'ST_B6')
    : makePrep('SR_B4', 'SR_B5', 'SR_B6', 'ST_B10');

  var comp = raw.map(prep).median();
  var lst  = comp.select('LST');
  var ndvi = comp.normalizedDifference(['NIR', 'RED']).rename('NDVI');
  var ndbi = comp.normalizedDifference(['SWIR1', 'NIR']).rename('NDBI');
  var out  = ee.Image.cat([lst, ndvi, ndbi]).toFloat().clip(city);

  print(y + ' | LST stats (°C)', lst.reduceRegion({
    reducer: ee.Reducer.minMax().combine(ee.Reducer.mean(), '', true),
    geometry: region, scale: 30, maxPixels: 1e13
  }));

  Map.addLayer(out.select('LST'),
    {min: 25, max: 45, palette: ['blue', 'cyan', 'yellow', 'orange', 'red']},
    'LST ' + y, y === YEARS[YEARS.length - 1]);

  Export.image.toDrive({
    image: out,
    description: 'RCC_LST_NDVI_NDBI_' + y,
    folder: EXPORT_FOLDER,
    fileNamePrefix: 'RCC_LST_NDVI_NDBI_' + y,
    region: region,
    scale: 30,
    crs: EXPORT_CRS,
    maxPixels: 1e13
  });
});

Map.addLayer(city.style({color: 'black', fillColor: '00000000'}), {}, 'City boundary');
