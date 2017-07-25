##AHPS_Gauges=boolean True 
##CPC_6_to_10_Day_Temperatures=boolean True
##CPC_6_to_10_Day_Precipitation=boolean True 
##QPF_24_Hours_Day_1=boolean True 
##QPF_24_Hours_Day_2=boolean True 
##QPF_24_Hours_Day_3=boolean True 
##Watches_Warnings=boolean True 
##Current_Warnings=boolean True 

import urllib2  
import os 
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
temp_dir = 'C:/Users/shawn.carter/.qgis2/processing/scripts/temp'
style_dir = 'C:/Users/shawn.carter/.qgis2/processing/scripts/gis_files'
temp_files = ['AHPS_temp.geojson', 'CPC_temp_temp.geojson', 'CPC_precip_temp.geojson',
                     'QPF_1_temp.geojson', 'QPF_2_temp.geojson', 'QPF_3_temp.geojson', 'watchwarn_temp.geojson',
                     'currentwarn_temp.geojson']
styles = ['ahps_gages.qml', 'qpc_6-10-temps.qml', 'qpc_6-10-precip.qml', 'qpf_24_hour_day_1.qml', 'qpf_24_hour_day_1.qml', 'qpf_24_hour_day_1.qml', 'watcheswarnings.qml', 'watcheswarnings.qml']
layer_names = ['AHPS Gauges', 'CPC 6-10 Day Temperature', 'CPC 6-10 Day Precipitation', 'QPF 24-hour Day 1', 'QPF 24-hour Day 2', 'QPF 24-hour Day 3', 'Watches/Warnings', 'Current Warnings']
    

gages_url = 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Observations/ahps_riv_gauges/MapServer/0/query?where=1%3D1&text=&objectIds=&time=&geometry=&geometryType=esriGeometryPoint&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=objectid%2C+location%2C+waterbody%2C+observed%2C+url%2C+status%2C+forecast%2C+obstime&returnGeometry=true&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&f=pjson'
cpc_temp_url = 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Climate_Outlooks/cpc_6_10_day_outlk/MapServer/0/query?where=1%3D1&text=&objectIds=&time=&geometry=&geometryType=esriGeometryPolygon&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=objectid%2C+prob%2C+cat&returnGeometry=true&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&f=pjson'
cpc_precip_url = 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Climate_Outlooks/cpc_6_10_day_outlk/MapServer/1/query?where=1%3D1&text=&objectIds=&time=&geometry=&geometryType=esriGeometryPolygon&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=objectid%2C+prob%2C+cat&returnGeometry=true&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&f=pjson'
qpf_1_url = 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Forecasts_Guidance_Warnings/wpc_qpf/MapServer/1/query?where=1%3D1&text=&objectIds=&time=&geometry=&geometryType=esriGeometryPolygon&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=objectid%2C+product%2C+valid_time%2C+qpf%2C+units%2C+issue_time%2C+start_time%2C+end_time&returnGeometry=true&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&f=pjson'
qpf_2_url = 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Forecasts_Guidance_Warnings/wpc_qpf/MapServer/2/query?where=1%3D1&text=&objectIds=&time=&geometry=&geometryType=esriGeometryPolygon&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=objectid%2C+product%2C+valid_time%2C+qpf%2C+units%2C+issue_time%2C+start_time%2C+end_time&returnGeometry=true&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&f=pjson'
qpf_3_url = 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Forecasts_Guidance_Warnings/wpc_qpf/MapServer/3/query?where=1%3D1&text=&objectIds=&time=&geometry=&geometryType=esriGeometryPolygon&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=objectid%2C+product%2C+valid_time%2C+qpf%2C+units%2C+issue_time%2C+start_time%2C+end_time&returnGeometry=true&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&f=pjson'
watchwarn_url = 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Forecasts_Guidance_Warnings/watch_warn_adv/MapServer/1/query?where=1%3D1&text=&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=objectid%2C+issuance%2C+expiration%2C+url%2C+prod_type%2C++&returnGeometry=true&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&f=pjson'
currentwarn_url = 'https://idpgis.ncep.noaa.gov/arcgis/rest/services/NWS_Forecasts_Guidance_Warnings/watch_warn_adv/MapServer/0/query?where=1%3D1&text=&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=objectid%2C+issuance%2C+expiration%2C+url%2C+prod_type%2C++&returnGeometry=true&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&f=pjson'

# Main Function
def get_layer(url, temp_layer):
    response = urllib2.urlopen(url)
    json = response.read()
    with open(os.path.join(temp_dir, temp_layer), 'wb') as outFile:
        outFile.write(json)
    
    layer = QgsVectorLayer(os.path.join(temp_dir, temp_layer), layer_names[temp_files.index(temp_layer)], 'ogr')
    QgsMapLayerRegistry.instance().addMapLayer(layer)
    layer.loadNamedStyle(os.path.join(style_dir, styles[temp_files.index(temp_layer)]))    
    legend = iface.legendInterface()
    legend.setLayerVisible(layer, False)

# List of URLs and Variables to Retrieve from NWS Servers 
urls = [gages_url, cpc_temp_url, cpc_precip_url, qpf_1_url, qpf_2_url, qpf_3_url, watchwarn_url, currentwarn_url]
get_em = [AHPS_Gauges,CPC_6_to_10_Day_Temperatures, CPC_6_to_10_Day_Precipitation, QPF_24_Hours_Day_1,
                  QPF_24_Hours_Day_2, QPF_24_Hours_Day_3, Watches_Warnings, Current_Warnings]
                
# Remove old layers
for layer in QgsMapLayerRegistry.instance().mapLayers().values():
    if layer.name() in layer_names:
        QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

for url in urls[::-1]:
    if get_em[urls.index(url)] == True:
        get_layer(url, temp_files[urls.index(url)])