""" NOHRSC Assimilation Layers ArcGIS 10.4 Loading Script\nVersion 1.5\nPurpose: This script is used to load the necessary\ndatasets used for NOHRSC Assimilation data analysis.\n\n """

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import os, shutil

class assimStartup:
    """These directories need to be changed upon new installation (first time run)"""
    if os.path.exists(r'/net/assim/data'):
        sourceFolder = r'home/assim/data'
    else:
        sourceFolder = r'C:/Users/shawn.carter/Desktop/GIS_Files' # Change this directory (First time run)
    
    # Change these next three folders (First Time Run)
    workingFolder = r'C:/assimilation'
    symbologyFolder = r'C:/Users/shawn.carter/Documents/Assim/symbology'
    backgroundFolder = r'C:/Users/shawn.carter/Documents/Assim/common_layer/common_layer'
    
    vectorSymbology = os.path.join(symbologyFolder, 'shapefile')
    rasterSymbology = os.path.join(symbologyFolder, 'raster')
    vectorData = os.path.join(sourceFolder, 'point_data_shape')
    rasterData = os.path.join(sourceFolder, 'snow_line_raster')
    working_vectorData = os.path.join(workingFolder, 'point_data_shape')
    working_rasterData = os.path.join(workingFolder, 'snow_line_raster')
    
    def __init__(self, iface):
        self.iface = iface

    def clearTheMap(self):
        """Clears the Map"""
        layers = QgsMapLayerRegistry.instance().mapLayers()
        for name, layer in layers.iteritems():
            QgsMapLayerRegistry.instance().removeMapLayer(name)
        
        self.iface.mapCanvas().refresh()
    
    def loadDeltaPoints(self):
        # Copy the delta points shapefile to the working directory
        deltaSHP = 'ssm1054_md_based_%s%s_%s%s.shp' % (start_date, start_hour, end_date, end_hour)
        if os.path.isfile(os.path.join(self.vectorData, deltaSHP)):
            for file in os.listdir(self.vectorData):
                if file.startswith(deltaSHP[:-4]):
                    shutil.copy(os.path.join(self.vectorData, file), self.working_vectorData)
         
            # Load the delta points shapefile into the map document
            deltaSHP_file = os.path.join(self.working_vectorData, deltaSHP)
            deltaLayer = QgsVectorLayer(deltaSHP_file, 'Delta Points %s' % end_date, 'ogr')
            deltaLayer.loadNamedStyle(os.path.join(self.vectorSymbology, 'point_delta_style.qml'))
            QgsMapLayerRegistry.instance().addMapLayer(deltaLayer)
        
        else:
            print('ssm1054_md_based_%s%s_%s%s.shp does not exist!' % (start_date, start_hour, end_date, end_hour))
            
    def loadRasters(self, raster, rasterStyle):
        # Copy shapefiles to the working directory
        if os.path.isfile(os.path.join(self.rasterData, raster)):
            for file in os.listdir(self.rasterData):
                if file.startswith(raster):
                    shutil.copy(os.path.join(self.rasterData, file), self.working_rasterData)
                    
            # Load the rasters into the map document
            rasterFileName = os.path.join(self.working_rasterData, raster)
            rasterInfo = QFileInfo(rasterFileName)
            rasterBaseName = rasterInfo.baseName()
            rasterLayer = QgsRasterLayer(rasterFileName, rasterBaseName)
            rasterLayer.loadNamedStyle(rasterStyle)
            QgsMapLayerRegistry.instance().addMapLayer(rasterLayer)
        
        else:
            print('%s does not exist, you will have manually load it' % (raster))

    def loadBaseLayers(self):
        # Location of Background Layer Files
        dem_file = os.path.join(self.backgroundFolder, 'SRTM_elevation_average.tif')
        hillshade_file = os.path.join(self.backgroundFolder, 'hillshading.tif')
        polygons_file = os.path.join(self.backgroundFolder, 'bound_p.shp')
        lines_file = os.path.join(self.backgroundFolder, 'bound_l.shp')
        
        # Create the Qgis Layers
        polygons = QgsVectorLayer(polygons_file, 'Water/Land', 'ogr')
        lines = QgsVectorLayer(lines_file, 'Borders', 'ogr')
        dem = QgsRasterLayer(dem_file, 'SRTM DEM')
        hillshade = QgsRasterLayer(hillshade_file, 'Hillshade')
        
        # Define symbology
        polygons.loadNamedStyle(os.path.join(self.vectorSymbology, 'polybkgrd.qml'))
        lines.loadNamedStyle(os.path.join(self.vectorSymbology, 'linebkrd.qml'))
        dem.loadNamedStyle(os.path.join(self.rasterSymbology, 'demStyle.qml'))
        hillshade.loadNamedStyle(os.path.join(self.rasterSymbology, 'hillshadeStyle.qml'))
        
        # Load the layers onto the map
        layers = [polygons, lines, hillshade, dem]
        QgsMapLayerRegistry.instance().addMapLayers(layers)

def run_script(iface, **args):
    # Instatiate the assimStartup Class
    startup = assimStartup(iface)
    
    # Declare Global Variable Assignments
    global start_date
    global start_hour
    global end_date
    global end_hour
    
    start_date = args['start_date']
    start_hour = args['start_hour']
    end_date = args['end_date']
    end_hour = args['end_hour']
    keep_old_layers = args['keep_old_layers']
    
    # List of rasters from SNODAS 
    rasters = {'SWE_' + start_date +'05.tif':[os.path.join(startup.rasterSymbology,'swe.qml'), 'SWE_*'],
           'SC_SWE_' + start_date + '05.tif': [os.path.join(startup.rasterSymbology,'SC_SWE_Master.qml'), 'SC_SWE_*'],
           'SC_NESDIS_' + start_date + '.tif': [os.path.join(startup.rasterSymbology, 'SC_NESDIS_Master.qml'), 'SC_NES*']}
    
    if keep_old_layers.lower() == 'no':
        startup.clearTheMap()
    
    startup.loadBaseLayers()
    
    for raster in rasters:
        startup.loadRasters(raster, rasters[raster][0])
    
    startup.loadDeltaPoints()
    
    
