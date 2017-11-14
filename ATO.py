##Survey_Name=string Svy01
##Type_of_Survey=string SM 
##Survey_Start_Date=string 01/01/2017
##Survey_End_Date=string 01/15/2017
##Requesting_RFC=string NCRFC
##Priority_1_Lines=string AA101
##Priority_2_Lines=string None
##Priority_3_Lines=string None
##Survey_Requirements=string <Free Text>
##Collect_Snow_Free=boolean True
##Photography_Requirements=string <Free Text>
##Data_Transmission_Instructions=string Email to carrie.olheiser@noaa.gov
##Special_Requirements_or_Instructions=string <Free Text>
##Area_of_Interest=string <Free Text>
##Ice_Jam_Requirements=string None
##Save_Air_Tasking_Order_To=folder
##Master_Flight_Lines_Shapefile=vector

from qgis.core import *
from qgis.utils import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import processing as pro 
import os
import time
import csv
from qgis.gui import QgsMapCanvas, QgsLayerTreeMapCanvasBridge
from qgis.PyQt.QtXml import QDomDocument

out_folder = Save_Air_Tasking_Order_To
layer = pro.getObject(Master_Flight_Lines_Shapefile)
gis_files = r'C:/Users/shawn.carter/.qgis2/processing/scripts/gis_files'

if not os.path.exists(os.path.join(out_folder, Survey_Name)):
    os.mkdir(os.path.join(out_folder, Survey_Name))
os.chdir(os.path.join(out_folder, Survey_Name))



def get_remarks(lines, layer):
    """Yields input flight lines that are not present in the master 
    flight line shapefile 
    """
    all_features_layer = QgsVectorLayer(layer.source(), 'all lines', 
        layer.providerType())
    all_features = all_features_layer.getFeatures()
    all_remarks = {feature['name']:feature['Remarks'] for feature in all_features}
    missing_lines = [i for i in lines if i not in all_remarks]
    return missing_lines

def add_lines(lines, text, style, layer):
    if lines:
        definition_query = '"name" in ('
        for i in range(0, len(lines)):
            if i + 1 < len(lines):
                definition_query += "'%s'," % lines[i]
            elif i + 2 > len(lines):
                definition_query += "'%s'" % lines[i]
        definition_query += ')'
    else:
        definition_query = '"name"' + " in ('')"

    new_layer = QgsVectorLayer(layer.source(), text, layer.providerType())
    new_layer.setSubsetString(definition_query)
    QgsMapLayerRegistry.instance().addMapLayer(new_layer)
    new_layer.loadNamedStyle(os.path.join(gis_files, style))
    features = new_layer.getFeatures()
    remarks = {feature['name']:feature['Remarks'] for feature in features}
    for i in remarks:
        if remarks[i] is NULL:
            remarks[i] = 'No Remarks'

    return new_layer, remarks 

def order_lines(lines, remarks):
    """Yields formatted lines id's and remarks for air tasking order"""
    i = 0
    group_lines = ''
    while i < len(lines):
        if i + 1 < len(lines):
            group_lines += '%s    %s    %s    %s\n' % (
                lines[i], remarks[lines[i]], lines[i+1], remarks[lines[i+1]])
        else:
            group_lines += '%s    %s\n\n' % (
                lines[i], remarks[lines[i]])
        i +=2 
    return group_lines

def makeOrder(primary_lines, primary_lines_remarks, 
    secondary_lines=None, secondary_lines_remarks=None,
    tertiary_lines=None, tertiary_lines_remarks=None):
    """Yields the Air Tasking Order text file"""
    tasking = 'Survey Name: %s\n' % Survey_Name
    tasking += 'Type of Survey: %s\n' % Type_of_Survey
    tasking += 'Survey Dates: %s - %s\n' % (Survey_Start_Date, Survey_End_Date)
    tasking += 'Requesting RFC: %s\n' % Requesting_RFC
    tasking += 'Survey Requirements: %s\n' % Survey_Requirements
    tasking += '--------------------------------------------------------\n\n'
    tasking += 'Priority 1 Lines:\n'
    tasking += order_lines(primary_lines, primary_lines_remarks)
    if secondary_lines:
        tasking += 'Priority 2 Lines:\n'
        tasking += order_lines(secondary_lines, secondary_lines_remarks)
    if tertiary_lines:
        tasking += 'Priority 3 Lines:\n'
        tasking += order_lines(tertiary_lines, tertiary_lines_remarks)
    tasking += '---------------------------------------------------------\n\n'
    if Collect_Snow_Free is True:
        snow_lines = 'Yes'
    else:
        snow_lines = 'No'
    tasking += 'Collect Snow Free Lines: %s\n' % snow_lines
    tasking += 'Photography Requirements: %s\n' % Photography_Requirements
    tasking += 'Data Transmission Requirements: %s\n' % Data_Transmission_Instructions
    tasking += 'Area of Interest: %s\n' % Area_of_Interest
    tasking += 'Ice Jam Requirements: %s\n' % Ice_Jam_Requirements

    with open(Survey_Name + '.txt', 'wb') as out_tasking:
        out_tasking.write(tasking)

def makeKML(flight_lines, priority):
    """Yields KML of selected flight lines"""
    with open(Survey_Name + priority +'.kml', 'wb') as kml:
        if priority == '_Priority_1_Lines':
            color = 'fffa5002'
        elif priority == '_Priority_2_Lines':
            color = 'ff150dff'
        elif priority == '_Priority_3_Lines':
            color = 'ff189635'
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
        header += '  <Style id="sh_red-circle">\n'
        header += '    <IconStyle>\n'
        header += '      <scale>1.3</scale>\n'
        header += '      <Icon>\n'
        header += '        <href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href>\n'
        header += '      </Icon>\n'
        header += '      <hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>\n'
        header += '    </IconStyle>\n'
        header += '    <ListStyle>\n'
        header += '      <ItemIcon>\n'
        header += '         <href>http://maps.google.com/mapfiles/kml/paddle/red-circle-lv.png</href>\n'
        header += '      </ItemIcon>\n'
        header += '    </ListStyle>\n'
        header += '  </Style>\n'
        header += '  <Style id="sn_ltblu-circle">\n'
        header += '    <IconStyle>\n'
        header += '      <scale>1.3</scale>\n'
        header += '      <Icon>\n'
        header += '        <href>http://maps.google.com/mapfiles/kml/paddle/ltblu-circle.png</href>\n'
        header += '      </Icon>\n'
        header += '      <hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>\n'
        header += '    </IconStyle>\n'
        header += '    <ListStyle>\n'
        header += '      <ItemIcon>\n'
        header += '         <href>http://maps.google.com/mapfiles/kml/paddle/ltblu-circle-lv.png</href>\n'
        header += '      </ItemIcon>\n'
        header += '    </ListStyle>\n'
        header += '  </Style>\n'
        header += '  <Schema name="Survey" id="Survey">\n'
        header += '      <SimpleField name="length" type="float"></SimpleField>\n'
        header += '      <SimpleField name="River Basin" type="string"></SimpleField>\n'
        header += '      <SimpleField name="State" type="string"></SimpleField>\n'
        header += '      <SimpleField name="RFC" type="string"></SimpleField>\n'
        header += '      <SimpleField name="Status" type="string"></SimpleField>\n'
        header += '      <SimpleField name="WSFO" type="string"></SimpleField>\n'
        header += '      <SimpleField name="CWA 1" type="string"></SimpleField>\n'
        header += '      <SimpleField name="CWA 2" type="string"></SimpleField>\n'
        header += '      <SimpleField name="CWA 1 Name" type="string"></SimpleField>\n'
        header += '      <SimpleField name="CWA 2 Name" type="string"></SimpleField>\n'
        header += '      <SimpleField name="Map Num 1" type="string"></SimpleField>\n'
        header += '      <SimpleField name="Map Num 2" type="string"></SimpleField>\n'
        header += '      <SimpleField name="Remarks" type="string"></SimpleField>\n'
        header += '      <SimpleField name="Elevation (Ft)" type="float"></SimpleField>\n'
        header += '      <SimpleField name="Lat Midpoint" type="float"></SimpleField>\n'
        header += '      <SimpleField name="Lon Midpoint" type="float"></SimpleField>\n'
        header += '  </Schema>\n'
        header += '  <Folder><name>Survey</name>\n'
        
        kml.write(header)
        
        for feature in flight_lines.getFeatures():
            kml.write('   <Placemark>\n')
            kml.write('      <name>%s</name>\n' % feature['name'])
            kml.write('      <styleUrl>#LinePolys</styleUrl>\n')
            kml.write('      <ExtendedData><SchemaData SchemaUrl="Survey">\n')
            kml.write('        <SimpleData name="length">%s</SimpleData>\n' % feature['LENGTH'])
            kml.write('        <SimpleData name="River Basin">%s</SimpleData>\n' % feature['RIVER_BASI'])
            kml.write('        <SimpleData name="RFC">%s</SimpleData>\n' % feature['RFC'])
            kml.write('        <SimpleData name="Status">%s</SimpleData>\n' % feature['STATUS'])
            kml.write('        <SimpleData name="WSFO">%s</SimpleData>\n' % feature['WSFO'])
            kml.write('        <SimpleData name="CWA 1">%s</SimpleData>\n' % feature['CWA_1'])
            kml.write('        <SimpleData name="CWA 2">%s</SimpleData>\n' % feature['CWA_2'])
            kml.write('        <SimpleData name="CWA 1 Name">%s</SimpleData>\n' % feature['CWANAME_1'])
            kml.write('        <SimpleData name="CWA 2 Name">%s</SimpleData>\n' % feature['CWANAME_2'])
            kml.write('        <SimpleData name="Map Num 1">%s</SimpleData>\n' % feature['MAPNUM1'])
            kml.write('        <SimpleData name="Map Num 2">%s</SimpleData>\n' % feature['MAPNUM2'])
            kml.write('        <SimpleData name="Remarks">%s</SimpleData>\n' % feature['Remarks'])
            kml.write('        <SimpleData name="Elevation (Ft)">%s</SimpleData>\n' % feature['ELEV_FT'])
            kml.write('        <SimpleData name="Lat Midpoint">%s</SimpleData>\n' % feature['LAT_MIDPNT'])
            kml.write('        <SimpleData name="Lon Midpoint">%s</SimpleData>\n' % feature['LON_MIDPNT'])
            kml.write('      </SchemaData></ExtendedData>\n')
            kml.write('      <LineString>\n>')
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
            if feature['LINE_DIR'] == 'Yes':
                kml.write('    <Placemark>\n')
                kml.write('      <name>Start</name>\n')
                kml.write('      <description>%s</description>\n' %  feature['NAME'])
                kml.write('      <styleUrl>#sn_ltblu-circle</styleUrl>\n')
                kml.write('      <Point>\n')
                kml.write('        <coordinates>%s,%s</coordinates>\n' % (geom[0][0], geom[0][1]))
                kml.write('      </Point>\n')
                kml.write('    </Placemark>\n')
                kml.write('    <Placemark>\n')
                kml.write('      <name>End</name>\n')
                kml.write('      <description>%s</description>\n' %  feature['NAME'])
                kml.write('      <styleUrl>#sh_red-circle</styleUrl>\n')
                kml.write('      <Point>\n')
                kml.write('        <coordinates>%s,%s</coordinates>\n' % (geom[-1][0], geom[-1][1]))
                kml.write('      </Point>\n')
                kml.write('    </Placemark>\n')
        kml.write('</Folder>\n')
        kml.write('</Document></kml>')

def make_CSV(layer, priority):
    """Yields CSV of flight line attributes"""
    fields = [field.name() for field in layer.pendingFields()]
    with open(Survey_Name + priority + '.csv', 'wb') as outCSV:
        writer = csv.writer(outCSV, delimiter=',')
        writer.writerow(fields)
        for feature in layer.getFeatures():
            writer.writerow(feature.attributes())

def missing_lines_file():
    """Yields text file of missing input fields"""
    if primary_lines:
        with open(Survey_Name + '_Flight_Line_Errors.txt', 'wb') as outErrors:
            outErrors.write('Non-existent primary flight lines:\n\n')
            for i in missing_priority_lines:
                outErrors.write('%s\n') % missing_priority_lines[i]
            if missing_secondary_lines:
                outErrors.write('Non-existent secondary flight lines:\n\n')
                for i in missing_secondary_lines:
                    outErrors.write('%s\n') % missing_secondary_lines[i]
            if missing_tertiary_lines:
                outErrors.write('Non-existent tertiary flight lines:\n\n')
                for i in missing_tertiary_lines:
                    outErrors.write('%s\n') % missing_tertiary_lines[i]

def get_extents(layer):
    """Yields the geographical extents of the layers"""
    extent = layer.extent().toString().split(':')
    left = float(extent[0].split(',')[0])
    bottom = float(extent[0].split(',')[1])
    right = float(extent[1].split(',')[0])
    top = float(extent[1].split(',')[1])
    return left, bottom, right, top 

def compare_extents(primary_layer, secondary_layer=None, tertiary_layer=None):
    primary_left, primary_bottom, primary_right, primary_top = get_extents(primary_layer)
    if not secondary_layer:
        secondary_left, secondary_bottom, secondary_right, secondary_top = (
            primary_left, primary_bottom, primary_right, primary_top)
    else:
        secondary_left, secondary_bottom, secondary_right, secondary_top = get_extents(secondary_layer)
    if not tertiary_layer:
        tertiary_left, tertiary_bottom, tertiary_right, tertiary_top = (
            primary_left, primary_bottom, primary_right, primary_top)
    else:
        tertiary_left, tertiary_bottom, tertiary_right, tertiary_top = get_extents(tertiary_layer)

    left = min(primary_left, secondary_left, tertiary_left)
    bottom = min(primary_bottom, secondary_bottom, tertiary_bottom)
    right = max(primary_right,secondary_right, tertiary_right)
    top = max(primary_top, secondary_top, tertiary_top)
    east_west = right - left
    north_south = top - bottom
    left = left - (east_west * 0.2)
    right = right + (east_west * 0.2)
    top = top + (north_south * 0.2)
    bottom = bottom + (north_south * 0.2)
    extent = QgsRectangle(left, bottom, right, top)
    return extent

def export_map(layer, new_extent):
    """This function changes the map extents and creates a exported map image"""
    legend = iface.legendInterface()
    legend.setLayerVisible(layer, False)
    canvas = iface.mapCanvas()
    canvas.setExtent(new_extent)
    canvas.refresh()
    project_path = os.path.join(gis_files, 'air_tasking_order.qgs')
    QgsProject.instance().write(QFileInfo(project_path))    #Save with the flight lines
    QgsProject.instance().read(QFileInfo(project_path))
    bridge = QgsLayerTreeMapCanvasBridge(
        QgsProject.instance().layerTreeRoot(), canvas)
    bridge.setCanvasLayers()
    template_file = file(os.path.join(gis_files, 'airborne_survey.qpt'))
    template_content = template_file.read()
    template_file.close()
    document = QDomDocument()
    document.setContent(template_content)
    ms = canvas.mapSettings()
    composition = QgsComposition(ms)
    composition.loadFromTemplate(document, {})
    map_item = composition.getComposerItemById('the_map')
    map_item.setMapCanvas(canvas)
    map_item.zoomToExtent(canvas.extent())
    map_text_box = '<font face="Arial">%s Tasking <br />%s - %s<br />%s' % (
        Requesting_RFC, Survey_Start_Date, Survey_End_Date, Survey_Name)
    map_text = composition.getComposerItemById('Map_ID_Text')
    map_text.setText(map_text_box)
    composition.refreshItems()
    dpi = 300
    dpmm = dpi / 24.4
    width = int(dpmm * composition.paperWidth())
    height = int(dpmm * composition.paperHeight())
    image = QImage(QSize(width, height), QImage.Format_ARGB32)
    image.setDotsPerMeterX(dpmm * 1000)
    image.setDotsPerMeterY(dpmm * 1000)
    imagePainter = QPainter(image)
    composition.renderPage(imagePainter, 0)
    imagePainter.end()
    image.save(Survey_Name + '.png', 'png')

def reset_map(new_extent):
    allLayers = QgsMapLayerRegistry.instance().mapLayers()
    for layer in allLayers:
        QgsMapLayerRegistry.instance().removeMapLayer(allLayers[layer])

    boundaries_file = os.path.join(gis_files, 'bound_l.shp')
    airports_file = os.path.join(gis_files, 'airports.shp')
    master_flines_file = os.path.join(gis_files, 'flines.shp')
    primary_file = os.path.join(out_folder, Survey_Name, Survey_Name + '_Priority_1_Lines.shp')
    secondary_file = os.path.join(out_folder, Survey_Name, Survey_Name + '_Priority_2_Lines.shp')
    tertiary_file = os.path.join(out_folder, Survey_Name, Survey_Name + '_Priority_3_Lines.shp')
    
    boundaries = QgsVectorLayer(boundaries_file, 'Boundaries', 'ogr')
    airports = QgsVectorLayer(airports_file, 'Airports', 'ogr')
    master_flines = QgsVectorLayer(master_flines_file, 'Master Flight Lines', 'ogr')
    primary_layer = QgsVectorLayer(primary_file, 'Primary Flight Lines', 'ogr')
    secondary_layer = QgsVectorLayer(secondary_file, 'Secondary Flight Lines', 'ogr')
    tertiary_layer = QgsVectorLayer(tertiary_file, 'Tertiary Flight Lines', 'ogr')
    
    QgsMapLayerRegistry.instance().addMapLayer(boundaries)
    QgsMapLayerRegistry.instance().addMapLayer(airports)
    QgsMapLayerRegistry.instance().addMapLayer(master_flines)
    QgsMapLayerRegistry.instance().addMapLayer(primary_layer)
    QgsMapLayerRegistry.instance().addMapLayer(secondary_layer)
    QgsMapLayerRegistry.instance().addMapLayer(tertiary_layer)
            
    boundaries.loadNamedStyle(os.path.join(gis_files, 'boundaries_style.qml'))
    airports.loadNamedStyle(os.path.join(gis_files, 'airports_style.qml'))
    master_flines.loadNamedStyle(os.path.join(gis_files, 'pri_style.qml'))
    secondary_layer.loadNamedStyle(os.path.join(gis_files, 'sec_style.qml'))
    tertiary_layer.loadNamedStyle(os.path.join(gis_files, 'ter_style.qml'))
    QgsProject.instance().write(QFileInfo(os.path.join(gis_files, 'air_tasking_order.qgs')))
    legend = iface.legendInterface()
    legend.setLayerVisible(master_flines, False)
    canvas = iface.mapCanvas()
    canvas.setExtent(new_extent)
    canvas.refresh()

def main():
    priority_lines = Priority_1_Lines.split('\n')
    if Priority_2_Lines == 'None':
        secondary_lines = None
    else: 
        secondary_lines = Priority_2_Lines.split('\n')

    if Priority_3_Lines == 'None':
        tertiary_lines = None
    else:
        tertiary_lines = Priority_3_Lines.split('\n')

    primary_layer, primary_lines_remarks = add_lines(priority_lines, 
        'Primary Flight Lines', 'pri_style.qml', layer)
    missing_priority_lines = get_remarks(priority_lines, layer)
    makeKML(primary_layer, '_Priority_1_Lines')
    QgsVectorFileWriter.writeAsVectorFormat(
        primary_layer, Survey_Name + '_Priority_1_Lines', 'UTF-8', None, 'ESRI Shapefile')
    make_CSV(primary_layer, '_Priority_1_lines')
    primary_left, primary_bottom, primary_right, primary_top = get_extents(primary_layer)

    if secondary_lines:
        secondary_layer, secondary_lines_remarks = add_lines(secondary_lines, 
            'Secondary Flight Lines', 'sec_style.qml', layer)
        missing_secondary_lines = get_remarks(secondary_lines, layer)
        makeKML(secondary_layer, '_Priority_2_Lines')
        QgsVectorFileWriter.writeAsVectorFormat(
            secondary_layer, Survey_Name + '_Priority_2_Lines', 'UTF-8', None, 'ESRI Shapefile')
        make_CSV(secondary_layer, '_Priority_2_Lines')
        secondary_left, secondary_bottom, secondary_right, secondary_top = get_extents(secondary_layer)
        secondary_lines_to_order = secondary_lines
        secondary_remarks_to_order = secondary_lines_remarks
        secondary_extent_func = secondary_layer 
    else:
        secondary_lines_to_order = None
        secondary_remarks_to_order = None
        secondary_extent_func = None 

    if tertiary_lines:
        tertiary_layer, tertiary_lines_remarks = add_lines(tertiary_lines, 
            'Tertiary Flight Lines', 'ter_style.qml', layer)
        missing_tertiary_lines = get_remarks(tertiary_lines, layer)
        makeKML(tertiary_layer, '_Priority_3_Lines')
        QgsVectorFileWriter.writeAsVectorFormat(
            tertiary_layer, Survey_Name + '_Priority_3_Lines', 'UTF-8', None, 'ESRI Shapefile')
        make_CSV(tertiary_layer, '_Priority_3_Lines')
        tertiary_left, tertiary_bottom, tertiary_right, tertiary_top = get_extents(tertiary_layer)
        tertiary_lines_to_order = tertiary_lines 
        tertiary_remarks_to_order = tertiary_lines_remarks
        tertiary_extent_func = tertiary_layer
    else:
        tertiary_lines_to_order = None
        tertiary_remarks_to_order = None
        tertiary_extent_func = None

    makeOrder(priority_lines, primary_lines_remarks,
        secondary_lines_to_order, secondary_remarks_to_order,
        tertiary_lines_to_order, tertiary_remarks_to_order)

    new_extent = compare_extents(primary_layer, secondary_extent_func, tertiary_extent_func)
    export_map(layer, new_extent)
    reset_map(new_extent)

main()