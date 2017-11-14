##Survey_Name=string Svy01
##Type_of_Survey=string SM
##Survey_Start_Date=string 01/01/2017
##Survey_End_Date=string 01/02/2017
##Requesting_RFC=string NCRFC
##Survey_Requirements=string <input free text>
##Priority_1_Lines=string AA101
##Priority_2_Lines=string None
##Collect_Snow_Free_Lines=boolean True 
##Photography_Requirements=string <input free text>
##Data_Transmission_Instructions=string Email  to carrie.olheiser@noaa.gov
##Special_Requirements_or_Instructions=string <input free text>
##Area_of_Interest=string <input free text>
##Ice_Jam_Requirements=string <input free text>
##Save_Air_Tasking_Order_To=folder 
##Master_Flight_Lines_Shapefile=vector 

from qgis.core import *
from qgis.utils import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import processing as pro 
import os, time, csv 
from qgis.gui import QgsMapCanvas, QgsLayerTreeMapCanvasBridge
from qgis.PyQt.QtXml import QDomDocument

# Shorten variable names 
pri_flines = Priority_1_Lines.split('\n')

if Priority_2_Lines == 'None':
    sec_flines = ''
else:
    sec_flines = Priority_2_Lines.split('\n')

out_folder = Save_Air_Tasking_Order_To
layer = pro.getObject(Master_Flight_Lines_Shapefile)

gis_files = r'C:/Users/shawn.carter/.qgis2/processing/scripts/gis_files'
os.mkdir(os.path.join(out_folder, Survey_Name))
os.chdir(os.path.join(out_folder, Survey_Name))

# Retrieve the Nav Remarks for the flight lines 

all_features_layer = QgsVectorLayer(layer.source(), 'all lines', layer.providerType())
all_features = all_features_layer.getFeatures()
all_line_remarks = {feature['name'] : feature['remarks'] for feature in all_features}

# Make a list of any flight lines that don't exist in the master flight line shapefile
missing_pri_flines = [i for i in pri_flines if i not in all_line_remarks]
missing_sec_flines = [i for i in sec_flines if i not in all_line_remarks]

# Add the Flight Lines to the Map
def add_flines(flines, text, style):
    if len(flines) > 0:
        definition_query = '"name" in ('
        for i in range(0, len(flines)):
            if i + 1 < len(flines):
                definition_query += "'%s', " % flines[i]
            elif i + 2 >  len(flines):
                definition_query += "'%s'" % flines[i]
        definition_query += ')'
    else:
        definition_query = '"name"' + " in ('')"

    new_layer = QgsVectorLayer(layer.source(), text, layer.providerType())
    new_layer.setSubsetString(definition_query)
    QgsMapLayerRegistry.instance().addMapLayer(new_layer)
    new_layer.loadNamedStyle(os.path.join(gis_files, style))

    return new_layer

pri_flines_layer = add_flines(pri_flines, 'Primary 1 Lines', 'pri_style.qml')

primary_flight_line_remarks = {feature['name']:feature['remarks'] for feature in pri_flines_layer.getFeatures()}
for i in primary_flight_line_remarks:
    if primary_flight_line_remarks[i] == NULL:
        primary_flight_line_remarks[i] = ''

if len(sec_flines) > 0:
    sec_flines_layer = add_flines(sec_flines, 'Primary 2 Lines', 'sec_style.qml')
    secondary_flight_line_remarks = {feature['name']:feature['remarks'] for feature in sec_flines_layer.getFeatures()}
    for i in secondary_flight_line_remarks:
        if secondary_flight_line_remarks[i] == NULL:
            secondary_flight_line_remarks[i] = ''

def makeOrder():
    # Create the text of the Air Tasking Order from input variables.
    tasking = 'Survey Name:  %s \n' % Survey_Name
    tasking += 'Type of Survey: %s \n' % Type_of_Survey
    tasking += 'Survey Dates: %s - %s \n' % (Survey_Start_Date, Survey_End_Date)
    tasking += 'Requesting RFC: %s \n' % Requesting_RFC
    tasking += 'Survey Requirements: \n%s\n' % Survey_Requirements
    tasking += '---------------------------------------------------------------\n\n'
    tasking += 'Priority 1 Lines: \n'
    
    # Iterate through the Flight Line Number for Priority 1 Lines
    i = 0
    while i < len(pri_flines):
        if i + 1 < len(pri_flines):
            tasking += '%s  %s     %s  %s\n' % (pri_flines[i], primary_flight_line_remarks[pri_flines[i]], pri_flines[i+1], primary_flight_line_remarks[pri_flines[i+1]])
        else:
            tasking += '%s  %s\n\n' % (pri_flines[i], primary_flight_line_remarks[pri_flines[i]])
            
        i += 2
        
    tasking += '\nPriority 2 Lines: \n'
    
    # Iterate thought the Fline Line Numbers for Pritority 2 Lines
    i = 0
    while i < len(sec_flines):
        if i + 1 < len(sec_flines):
            tasking += '%s  %s     %s  %s\n' % (sec_flines[i], secondary_flight_line_remarks[sec_flines[i]], sec_flines[i+1], secondary_flight_line_remarks[sec_flines[i]])
        else:
            tasking += '%s\n\n' % (sec_flines[i], secondary_flight_line_remarks[sec_flines[i]])
        i += 2
        
    tasking += '---------------------------------------------------------------\n\n'
    if Collect_Snow_Free_Lines is True:
        snow_lines = 'Yes'
    else:
        snow_lines = 'No'
    tasking += '\nCollect Snow Free Lines:\n%s\n\n' % snow_lines
    tasking += 'Photography Requirements:\n%s\n\n' % Photography_Requirements
    tasking += 'Data Transmission Instructions:\n%s\n\n' % Data_Transmission_Instructions
    tasking += 'Special Requirements / Instructions:\n%s\n\n' % Special_Requirements_or_Instructions
    tasking += 'Area of Interest:\n%s\n\n' % Area_of_Interest
    tasking += 'Ice Jam Requirements:\n%s' % Ice_Jam_Requirements
    
    # Write the order to a text file
    with open(Survey_Name + '.txt', 'wb') as out_tasking:
        out_tasking.write(tasking)
    
def makeKML(flight_lines, priority):
    kml = open(Survey_Name + priority +'.kml', 'wb') 
    if priority == '_Priority_1_Lines':
        color = 'fffa5002'
    elif priority == '_Priority_2_Lines':
        color = 'ff150dff'
    # Create the header of the KML file
    header = '<?xml version="1.0" encoding="utf-8" ?>\n'
    header += '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
    header += '<Document id="root_doc">\n'
    header += '  <Style id="Lines">\n'
    header += '    <LineStyle>\n'
    header += '      <color>%s</color>\n' % color 
    header += '      <width>4</width>\n'
    header += '    </LineStyle>\n'
    header += '  </Style>\n'
    header += '  <Style id="Points">\n'
    header += '    <IconStyle>\n'
    header += '      <scale>0</scale>\n'
    header += '    </IconStyle>\n'
    header += '  </Style>\n'
    header += '  <Style id="LinePolys">\n'
    header += '    <LineStyle>\n'
    header += '      <color>%s</color>\n' % color
    header += '      <width>4</width>\n'
    header += '     </LineStyle>\n'
    header += '     <PolyStyle>\n'
    header += '        <color>%s</color>\n' % color
    header += '     </PolyStyle>\n'
    header += '  </Style>\n'
    header += '  <Schema name="Survey" id="Survey">\n'
    header += '      <SimpleField name="length" type="float"></SimpleField>\n'
    header += '      <SimpleField name="RIVER_BASI" type="string"></SimpleField>\n'
    header += '      <SimpleField name="STATE" type="string"></SimpleField>\n'
    header += '      <SimpleField name="RFC" type="string"></SimpleField>\n'
    header += '      <SimpleField name="STATUS" type="string"></SimpleField>\n'
    header += '      <SimpleField name="WSFO" type="string"></SimpleField>\n'
    header += '      <SimpleField name="CWA_1" type="string"></SimpleField>\n'
    header += '      <SimpleField name="CWA_2" type="string"></SimpleField>\n'
    header += '      <SimpleField name="CWA_1 Name" type="string"></SimpleField>\n'
    header += '      <SimpleField name="CWA_2 Name" type="string"></SimpleField>\n'
    header += '      <SimpleField name="MAPNUM1" type="string"></SimpleField>\n'
    header += '      <SimpleField name="MAPNUM2" type="string"></SimpleField>\n'
    header += '      <SimpleField name="Remarks" type="string"></SimpleField>\n'
    header += '      <SimpleField name="ELEV_FT (Ft)" type="float"></SimpleField>\n'
    header += '      <SimpleField name="LAT_MIDPNT" type="float"></SimpleField>\n'
    header += '      <SimpleField name="LON_MIDPNT" type="float"></SimpleField>\n'
    header += '  </Schema>\n'
    header += '  <Folder><name>Survey</name>\n'
    
    kml.write(header)
    
    for feature in flight_lines.getFeatures():
        kml.write('   <Placemark>\n')
        kml.write('      <name>%s</name>\n' % feature['name'])
        kml.write('      <styleUrl>#LinePolys</styleUrl>\n')
        kml.write('      <ExtendedData><SchemaData SchemaUrl="Survey">\n')
        kml.write('        <SimpleData name="length">%s</SimpleData>\n' % feature['length'])
        kml.write('        <SimpleData name="RIVER_BASI">%s</SimpleData>\n' % feature['RIVER_BASI'])
        kml.write('        <SimpleData name="RFC">%s</SimpleData>\n' % feature['rfc'])
        kml.write('        <SimpleData name="STATUS">%s</SimpleData>\n' % feature['status'])
        kml.write('        <SimpleData name="WSFO">%s</SimpleData>\n' % feature['wsfo'])
        kml.write('        <SimpleData name="CWA_1">%s</SimpleData>\n' % feature['cwa_1'])
        kml.write('        <SimpleData name="CWA_2">%s</SimpleData>\n' % feature['cwa_2'])
        kml.write('        <SimpleData name="CWA_1 Name">%s</SimpleData>\n' % feature['CWANAME_1'])
        kml.write('        <SimpleData name="CWA_2 Name">%s</SimpleData>\n' % feature['CWANAME_2'])
        kml.write('        <SimpleData name="MAPNUM1">%s</SimpleData>\n' % feature['mapnum1'])
        kml.write('        <SimpleData name="MAPNUM2">%s</SimpleData>\n' % feature['mapnum2'])
        kml.write('        <SimpleData name="Remarks">%s</SimpleData>\n' % feature['remarks'])
        kml.write('        <SimpleData name="ELEV_FT (Ft)">%s</SimpleData>\n' % feature['elev_ft'])
        kml.write('        <SimpleData name="LAT_MIDPNT">%s</SimpleData>\n' % feature['LAT_MIDPNT'])
        kml.write('        <SimpleData name="LON_MIDPNT">%s</SimpleData>\n' % feature['LON_MIDPNT'])
        kml.write('      </SchemaData></ExtendedData>\n')
        kml.write('      <LineString>\n')
        kml.write('        <extrude>1</extrude><tesselate>1</tesselate>\n') # Comment out this line for non-extruded lines
        kml.write('        <altitudeMode>relativeToGround</altitudeMode>\n') # Comment out this line for non-extruded lines
        kml.write('        <coordinates>\n')
        
        geom = feature.geometry().asPolyline()
        for geo in geom:
            kml.write('        %s,%s,500\n' % (geo[0], geo[1]))
            
        kml.write('      </coordinates></LineString>\n')
        kml.write('    </Placemark>\n')
        kml.write('    <Placemark>\n')
        kml.write('      <name>%s</name>\n' % feature['name'])
        kml.write('      <styleUrl>#Points</styleUrl>\n')
        kml.write('      <description>%s</description>\n' % feature['name'])
        kml.write('      <Point>\n')
        kml.write('        <coordinates>%s,%s</coordinates>\n' % (feature['LON_MIDPNT'], feature['LAT_MIDPNT']))
        kml.write('      </Point>\n')
        kml.write('    </Placemark>\n')
    
    kml.write('</Folder>\n')
    kml.write('</Document></kml>')

    kml.close()

def makeCSV(flines_layer, priority):
    fields = [field.name() for field in flines_layer.pendingFields()]
    with open(Survey_Name + priority + '.csv', 'wb') as outCSV:
        writer = csv.writer(outCSV, delimiter= ',')
        writer.writerow(fields)
        for feature in flines_layer.getFeatures():
            writer.writerow(feature.attributes())

# Make the Missing Flight Line File
try:
    missing_sec_flines
except NameError:
    missing_sec_flines = ''
else:
    missing_sec_flines = missing_sec_flines 

if len(missing_pri_flines) > 0 or len(missing_sec_flines) > 0:
    with open(os.path.join(out_folder, Survey_Name, 'Flight_Line_Errors.txt'), 'wb') as outErrors:
        outErrors.write('Non-existent primary flight lines:\n\n')
        for i in missing_pri_flines:
            outErrors.write(i + '\n')
        if len(missing_sec_flines) > 0:
            outErrors.write('Non-existent secondary flight lines:\n\n')
            for i in missing_sec_flines:
                outErrors.write(i + '\n')

# Hide the Master Flight Lines shapefile
legend = iface.legendInterface()
legend.setLayerVisible(layer, False)

# Write the Shapefile(s) and KML(s) file(s)
makeKML(pri_flines_layer, '_Priority_1_Lines')
QgsVectorFileWriter.writeAsVectorFormat(pri_flines_layer, Survey_Name + '_Priority_1_Lines.shp', 'UTF-8', None, 'ESRI Shapefile')

if len(sec_flines) > 0:
    makeKML(sec_flines_layer, '_Priority_2_Lines')
    QgsVectorFileWriter.writeAsVectorFormat(sec_flines_layer, Survey_Name + '_Priority_2_Lines.shp', 'UTF-8', None, 'ESRI Shapefile')

# Zoom to the Survey Area
pri_extent = pri_flines_layer.extent().toString().split(':')
if sec_flines != '':
    sec_extent = sec_flines_layer.extent().toString().split(':')

    # QGIS Extent is Lower Left: Upper Right
    # Find the Westernmost Extent
    if float(pri_extent[0].split(',')[0]) < float(sec_extent[0].split(',')[0]):
        left = float(pri_extent[0].split(',')[0])
    else:
        left = float(sec_extent[0].split(',')[0])

    # Find the Southernmost Extent
    if float(pri_extent[0].split(',')[1]) < float(sec_extent[0].split(',')[1]):
        bottom = float(pri_extent[0].split(',')[1])
    else:
        bottom = float(sec_extent[0].split(',')[1])
    
    # Find the Easternmost Extent
    if float(pri_extent[1].split(',')[0]) > float(sec_extent[1].split(',')[0]):
        right = float(pri_extent[1].split(',')[0])
    else:
        right = float(sec_extent[1].split(',')[0])
    
    # Find the Northernomst Extent
    if float(pri_extent[1].split(',')[1]) > float(sec_extent[1].split(',')[1]):
        top = float(pri_extent[1].split(',')[1])
    else:
        top = float(sec_extent[1].split(',')[1])

    raw_extent = QgsRectangle(left, bottom, right, top)
else:
    raw_extent = pri_flines_layer.extent()
# Add an extent buffer to the extent of the Flight Lines
extent_str = raw_extent.toString().split(':')
left = float(extent_str[0].split(',')[0])
right = float(extent_str[1].split(',')[0])
top = float(extent_str[1].split(',')[1])
bottom = float(extent_str[0].split(',')[1])

east_west = right - left
north_south = top - bottom 

left = left - (east_west * 0.2)
right = right + (east_west * 0.2)
top = top + (north_south * 0.2)
bottom = bottom - (north_south * 0.2)

new_extent = QgsRectangle(left, bottom, right, top)

canvas = iface.mapCanvas()
canvas.setExtent(new_extent)
canvas.refresh()

# Write the Air Tasking Order
makeOrder()
QgsProject.instance().write(QFileInfo(os.path.join(gis_files, 'air_tasking_order.qgs')))

# Write the CSV File
makeCSV(pri_flines_layer, '_Priority_1_Lines')
if len(sec_flines) > 0:
    makeCSV(sec_flines_layer, '_Priority_2_Lines')

# Print a PDF Map of the Survey Area
# Create the Map Render and Composition Objects
canvas = iface.mapCanvas()
project_path = os.path.join(gis_files, 'air_tasking_order.qgs')
QgsProject.instance().read(QFileInfo(project_path))
bridge = QgsLayerTreeMapCanvasBridge(
    QgsProject.instance().layerTreeRoot(), canvas)
bridge.setCanvasLayers()

template_file = file(r'/net/home/scarter/.qgis2/processing/scripts/gis_files/airborne_survey.qpt')
template_content = template_file.read()
template_file.close()

document = QDomDocument()
document.setContent(template_content)
ms = iface.mapCanvas().mapSettings()
composition = QgsComposition(ms)
composition.loadFromTemplate(document, {})

map_item = composition.getComposerItemById('the_map')
map_item.setMapCanvas(canvas)
map_item.zoomToExtent(canvas.extent())

map_text_box = '<font face="Arial">%s Tasking <br /> %s - %s <br /> %s' % (Requesting_RFC, Survey_Start_Date, Survey_End_Date, Survey_Name)
map_text = composition.getComposerItemById('Map_ID_Text')
map_text.setText(map_text_box)

composition.refreshItems()

dpi = 300
dpmm = dpi / 25.4
width = int(dpmm * composition.paperWidth())
height = int(dpmm * composition.paperHeight())

# create output image and initialize it
image = QImage(QSize(width, height), QImage.Format_ARGB32)
image.setDotsPerMeterX(dpmm * 1000)
image.setDotsPerMeterY(dpmm * 1000)
image.fill(0)

# render the composition
imagePainter = QPainter(image)
composition.renderPage(imagePainter, 0)
imagePainter.end()

image.save(os.path.join(out_folder, Survey_Name, Survey_Name + '.png'), 'png')

# Reset the Map --- This is a hack because I can't figure out why QGIS is deleting everything
allLayers = QgsMapLayerRegistry.instance().mapLayers()
for layer in allLayers:
    QgsMapLayerRegistry.instance().removeMapLayer(allLayers[layer])


boundaries_file = os.path.join(gis_files, 'bound_l.shp')
airports_file = os.path.join(gis_files, 'airports.shp')
master_flines_file = os.path.join(gis_files, 'lines.shp')
pri_1_flines_file = os.path.join(out_folder, Survey_Name, Survey_Name + '_Priority_1_Lines.shp')
if sec_flines != '':
    pri_2_flines_file = os.path.join(out_folder, Survey_Name, Survey_Name + '_Priority_2_Lines.shp')

boundaries = QgsVectorLayer(boundaries_file, 'Boundaries', 'ogr')
airports = QgsVectorLayer(airports_file, 'Airports', 'ogr')
master_flines = QgsVectorLayer(master_flines_file, 'Master Flight Lines', 'ogr')
pri_flines = QgsVectorLayer(pri_1_flines_file, 'Priority 1 Flight Lines', 'ogr')
if sec_flines != '':
    sec_flines = QgsVectorLayer(pri_2_flines_file, 'Priority 2 Flight Lines', 'ogr')

QgsMapLayerRegistry.instance().addMapLayers([boundaries, airports, master_flines, pri_flines])
if sec_flines !='':
    QgsMapLayerRegistry.instance().addMapLayer(sec_flines)


boundaries.loadNamedStyle(os.path.join(gis_files, 'boundaries_style.qml'))
airports.loadNamedStyle(os.path.join(gis_files, 'airports_style.qml'))
master_flines.loadNamedStyle(os.path.join(gis_files, 'Master_Flines.qml'))
pri_flines.loadNamedStyle(os.path.join(gis_files, 'pri_style.qml'))
if sec_flines != '':
    sec_flines.loadNamedStyle(os.path.join(gis_files, 'sec_style.qml'))

QgsProject.instance().write(QFileInfo(os.path.join(gis_files, 'air_tasking_order.qgs')))

legend = iface.legendInterface()
legend.setLayerVisible(master_flines, False)

canvas.setExtent(new_extent)
canvas.refresh()
