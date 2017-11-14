##Start_Date=string YYYYMMDDHH  
##End_Date=string YYYYMMDDHH
##Save_to_Folder=string C:/Users/shawn.carter/Documents/Assim/data 

from qgis.core import *
from qgis.utils import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import processing as pro 
import os, csv 
from osgeo import gdal, osr
import urllib, tarfile, gzip, glob
import numpy as np 

# Change the python working directory 
folder_name = End_Date[:-2]
if not os.path.exists(os.path.join(Save_to_Folder, folder_name)):
    os.mkdir(os.path.join(Save_to_Folder, folder_name))

if not os.path.exists(os.path.join(Save_to_Folder, folder_name, 'nudging_layers')):
    os.mkdir(os.path.join(Save_to_Folder, folder_name, 'nudging_layers'))
    
os.chdir(os.path.join(Save_to_Folder, folder_name))
gis_files = 'C:/Users/shawn.carter/.qgis2/processing/scripts/gis_files'

points_url = 'http://www.nohrsc.noaa.gov/pro/assim_points/%s' % End_Date[:6]
points_basename = 'ssm1054_md_based_%s_%s' % (Start_Date, End_Date)
points_ext = ['.shp', '.shx', '.dbf']
webFolder = points_url + '/' + points_basename

# Download the Assimilation Points from the Web Server
def get_shapes():
	file_getter = urllib.URLopener()
	[file_getter.retrieve(webFolder + i, points_basename + i) for i in points_ext]

# Write a .prj file 
with open(points_basename + '.prj', 'wb') as prj_write:
    prj_write.write('GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]')
    
# Download the SNODAS Model Results
def get_rasters():
    date = End_Date[:-2]
    year = date[0:4]
    mn = date[4:6]
    month = {"01":"01_Jan", "02":"02_Feb", "03":"03_Mar", "04":"04_Apr", "05":"05_May","06":"06_Jun",
             "07":"07_Jul", "08":"08_Aug", "09":"09_Sep", "10":"10_Oct", "11":"11_Nov","12":"12_Dec"}

    url = "ftp://sidads.colorado.edu/DATASETS/NOAA/G02158/masked/%s/%s/SNODAS_%s.tar" % (year, month[mn], date)
    file_name = url.split('/')[-1:][0]

    print("Downloading %s" % file_name)
    urllib.urlretrieve(url, file_name)

    # Decompress the Tar, unzip the SWE Layers
    print("Decompressing %s" % file_name)
    tar = tarfile.open(file_name)
    tar.extractall()
    tar.close()

    for f in glob.glob("us_ssmv*%s*" % date):
        inF = gzip.GzipFile(f, 'rb')
        inF_contents = inF.read()
        outF = open(f[:-3], 'wb')
        outF.write(inF_contents)
        inF.close()
        os.remove(f)
        outF.close()

    # Dictionary of data units to scale the output tiffs
    data_units = {}

    # Rename dat files to bil files
    for f in glob.glob('us_ssmv*%s*.dat' % date):
        old_dat = f[:-3] + 'dat'
        new_dat = f[:-3] + 'bil'
        os.rename(old_dat, new_dat)

    for f in glob.glob('us_ssmv*%s*.Hdr' % date):
        hdr_values = {}
        new_hdr = f[:-3] + 'hdr'
        root_name = f[:-4]
        old_header = open(f, 'rb')
        
        for row in old_header:
            hdr_values[row.split(':')[0]] = row.split(':')[1].rstrip('\n').strip()
        data_units[root_name] = hdr_values['Data units']
        if data_units[root_name] == 'Kelvins':
            data_units[root_name] = 'Kelvins / 1'
        old_header.close()
        hdr_contents = {"1":"byteorder M", "2":"layout bil", "3":"nbands 1", "4":"nbits 16",
                        "5":"ncols %s" % hdr_values['Number of columns'],
                        "6":"nrows %s" % hdr_values['Number of rows'],
                        "7":"ulxmap %s" % hdr_values['Benchmark x-axis coordinate'],
                        "8":"ulymap %s" % hdr_values['Benchmark y-axis coordinate'],
                        "9":"xdim %s" % hdr_values['X-axis resolution'],
                        "10":"ydim %s" % hdr_values['Y-axis resolution']}
        os.remove(f)
        with open(new_hdr, 'wb') as outF:
            for i in range(1, len(hdr_contents)+1):
                outF.write(hdr_contents[str(i)] + '\n')
        

    for f in glob.glob('us_ssmv*%s*.bil' % date):
        output_names = {'us_ssmv01025SlL00T0024TTNATS%s05DP001' % date : 'SNODAS_Liquid_Precip_%s.tif' % date, 
                        'us_ssmv01025SlL01T0024TTNATS%s05DP001' % date : 'SNODAS_Snow_Precip_%s.tif' % date, 
                        'us_ssmv11034tS__T0001TTNATS%s05HP001' % date : 'SNODAS_Snow_Water_Equivalent_%s.tif' % date,
                        'us_ssmv11036tS__T0001TTNATS%s05HP001' % date: 'SNODAS_Snow_Depth_%s.tif' % date,
                        'us_ssmv11038wS__A0024TTNATS%s05DP001' % date : 'SNODAS_Snow_Pack_Avg_Temp_%s.tif' % date,
                        'us_ssmv11039lL00T0024TTNATS%s05DP000' % date : 'SNODAS_Blowing_Snow_Sublimation_%s.tif' % date, 
                        'us_ssmv11044bS__T0024TTNATS%s05DP000' % date : 'SNODAS_Snow_Melt_%s.tif' % date,
                        'us_ssmv11050lL00T0024TTNATS%s05DP000' % date : 'SNODAS_Snow_Pack_Sublimation_%s.tif' % date }

        root_name = f[:-4]

        # Convert the bil rasters to geoTIFF, assign NoData Values and Scale Appropriately
        ds = gdal.Open(f)
        band = ds.GetRasterBand(1)

        # Convert the raster to a numpy array
        array = band.ReadAsArray()
        array = array.astype(float)

        # Assign the NoData value to the Array
        array[array==55537] = np.nan 

        # Scale the array 
        array = array / float(data_units[root_name].split('/')[1])

        # Write the array to a new geoTIFF file
        driver = gdal.GetDriverByName('GTiff')
        dst_ds = driver.Create(output_names[root_name],
            ds.RasterXSize,
            ds.RasterYSize,
            1,
            gdal.GDT_Float64)
        outband = dst_ds.GetRasterBand(1)
        outband.WriteArray(array, 0, 0)
        outband.FlushCache()
        proj = osr.SpatialReference()
        proj.SetWellKnownGeogCS("EPSG:4326")
        dst_ds.SetGeoTransform(ds.GetGeoTransform())
        dst_ds.SetProjection(proj.ExportToWkt())
        
        del array
        ds = None 
        os.remove(root_name + '.bil')
        os.remove(root_name + '.hdr')
    
def load_files():
	# Load the Base Layers
	boundaries = QgsVectorLayer(os.path.join(gis_files, 'bound_l.shp'), 'Boundaries', 'ogr')
	dem = QgsRasterLayer(os.path.join(gis_files, 'SRTM_elevation_average.tif'), 'DEM')
	points = QgsVectorLayer(points_basename + '.shp', points_basename, 'ogr')
	swe = QgsRasterLayer('SNODAS_Snow_Water_Equivalent_%s.tif' % End_Date[:-2], 'Snow Water Equivalent %s' % End_Date[:-2])
	sd = QgsRasterLayer('SNODAS_Snow_Depth_%s.tif' % End_Date[:-2], 'Snow Depth %s' % End_Date[:-2])
	sm = QgsRasterLayer('SNODAS_Snow_Melt_%s.tif' % End_Date[:-2], 'Snow Melt % s' % End_Date[:-2])
	temp = QgsRasterLayer('SNODAS_Snow_Pack_Avg_Temp_%s.tif' % End_Date[:-2], 'Snow Pack Average Temperature %s' % End_Date[:-2])
    
	# Add Percent Difference Field to the Points
	points.dataProvider().addAttributes([QgsField("Per_Diff", QVariant.String)])
	points.updateFields()

	features = points.getFeatures()
	with edit(points):
		for feat in features:
			if feat['OB_SWE'] > 0:
				perDiff = feat['D_SWE_OM'] / feat['OB_SWE']
			else:
				perDiff = feat['D_SWE_OM'] / 0.000025

			feat['Per_Diff'] = perDiff 
			points.updateFeature(feat)



	# Delete the bad points
	badStyles = [u'"OB_SWE" = 0 and "OB_DEPTH" != 0', u'"OB_DENSITY" < 40', u'"OB_DENSITY" > 6500 and "OB_DENSITY" < 3000 and not ("STATION_TY" = \'COCORAH\' and "OB_DENSITY" = 1000)']
	with edit(points):
		for x in range(0, len(badStyles)):
			listOfIDs = [feat.id() for feat in points.getFeatures(QgsFeatureRequest().setFilterExpression(badStyles[x]))]
			points.deleteFeatures(listOfIDs)

	# Insert the query definition to avoid displaying known bad sites
	with open(os.path.join(gis_files, 'SSM_points_Query_Definition.txt'), 'rb') as query_defn:
		subset = query_defn.read()

	points.setSubsetString(subset)

	# Clear the map document 
	QgsMapLayerRegistry.instance().removeAllMapLayers()
	iface.mapCanvas().refresh()

	# Insert the layers into the map document
	QgsMapLayerRegistry.instance().addMapLayers([boundaries, points, swe, sd, sm, temp, dem])

	# Hide the SNODAS Results except for SWE
	legend = iface.legendInterface()
	layers = [sd, sm, temp]
	for x in layers:
		legend.setLayerVisible(x, False)
	
	# Style the Layers
	boundaries.loadNamedStyle(os.path.join(gis_files, 'boundaries_style.qml'))
	points.loadNamedStyle(os.path.join(gis_files, 'point_delta_style.qml'))
	swe.loadNamedStyle(os.path.join(gis_files, 'swe.qml'))
	dem.loadNamedStyle(os.path.join(gis_files, 'demStyle.qml'))
	sd.loadNamedStyle(os.path.join(gis_files, 'snow_depth_style.qml'))
	sm.loadNamedStyle(os.path.join(gis_files, 'snow_melt_style.qml'))
	temp.loadNamedStyle(os.path.join(gis_files, 'snow_temp_style.qml'))


	# Reset the view
	extent = swe.extent()
	iface.mapCanvas().setExtent(extent)
	iface.mapCanvas().refresh()








get_shapes()
get_rasters()
load_files()
