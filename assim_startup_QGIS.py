"""NOHRSC QGIS 2.12 Assimilation Layers  Loading Script\nVersion 1.5\nPurpose: This script is used to load the necessary\ndatasets used for NOHRSC Assimilation data analysis.\n\n"""
import os, shutil
from qgis.core import *
from PyQt4.QtCore import QFileInfo

class assimStartup:
    ''' These directories need to be changed upon new installation (first time run) '''
    if os.path.exists(r'/net/assim/data'):
        sourceFolder = r'/home/assim/data'
    else:
        sourceFolder = r'C:/Users/shawn.carter/Desktop/GIS_Files' 
    workingFolder = r'C:/assimilation'
    symbologyFolder = r'C:/Users/shawn.carter/Documents/Assim/symbology' 
    vectorSymbology = r'shapefile'
    rasterSymbology = r'raster'
    vectorData = r'point_data_shape'
    rasterData = r'snow_line_raster'
    
    source_vectorData = os.path.join(sourceFolder, vectorData)
    source_rasterData = os.path.join(sourceFolder, rasterData)
    working_vectorData = os.path.join(workingFolder, vectorData)
    working_rasterData = os.path.join(workingFolder, rasterData)
    backgroundFolder = r'C:/Users/shawn.carter/Documents/Assim/common_layer/common_layer'
    
    def __init__(self, iface):
        self.iface = iface
        

            

    
    """Clears Map of Previous Assimilation Data, controlled by last command line argument """
    def clearTheMap(self):
        layers = QgsMapLayerRegistry.instance().mapLayers()
        for name, layer in layers.iteritems():
            QgsMapLayerRegistry.instance().removeMapLayer(name)
                    
        self.iface.mapCanvas().refresh()   


    """ Loads the Delta Points and applies appropriate symbology for assimilation data analysis """
    def loadDeltaPoints(self):
        ''' Copy shapefile to the working directory '''
        deltaSHP_file = os.path.join(self.source_vectorData, 'ssm1054_md_based_' + start_date + start_hour + '_' + end_date + end_hour + '.shp')
        if os.path.isfile(os.path.join(self.source_vectorData, deltaSHP_file)):
            for file in os.listdir(self.source_vectorData):
                if file.startswith(deltaSHP_file[:-4]):
                    shutil.move(file, self.working_vectorData)
            
            deltaLayer = QgsVectorLayer(deltaSHP_file, 'Delta Points %s' % end_date, 'ogr')
            QgsMapLayerRegistry.instance().addMapLayer(deltaLayer)
            deltaLayer.loadNamedStyle(os.path.join(self.symbologyFolder, self.vectorSymbology, 'point_delta_style.qml'))
            self.iface.mapCanvas().refresh()
        
        else:
            print('ssm1054_md_based_%s%s_%s%s.shp does not exist!' % start_date, start_hour, end_date, end_hour)

    """ Loads the SNODAS/NESDIS rasters and applies appropriate symbology for assimilation data analysis """
    def loadRasters(self, raster, rasterStyle, layerName):
        if os.path.isfile(os.path.join(self.source_rasterData, raster)):
            for file in os.listdir(self.source_rasterData):
                if file.startswith(raster):
                    shutil.copy(os.path.join(self.source_rasterData, file), self.working_rasterData)
                    
            rasterFileName = os.path.join(self.source_rasterData, raster)
            rasterInfo = QFileInfo(rasterFileName)
            rasterBaseName = rasterInfo.baseName()
            raster = QgsRasterLayer(rasterFileName, rasterBaseName)
            QgsMapLayerRegistry.instance().addMapLayer(raster)
            raster.loadNamedStyle(rasterStyle)
            self.iface.mapCanvas().refresh()

    """ Loads the Baselayers """
    def loadBaseLayers(self):
        
        dem_file = os.path.join(self.backgroundFolder, 'SRTM_elevation_average.tif')
        hillshade_file = os.path.join(self.backgroundFolder, 'hillshading.tif')
        polygons_file = os.path.join(self.backgroundFolder, 'bound_p.shp')
        lines_file = os.path.join(self.backgroundFolder, 'bound_l.shp')
        
        polygons = QgsVectorLayer(polygons_file, 'Polygons', 'ogr')
        lines = QgsVectorLayer(lines_file, 'Lines', 'ogr')
        dem = QgsRasterLayer(dem_file, 'SRTM DEM')
        hillshade = QgsRasterLayer(hillshade_file, 'Hillshading')
        
        layers = [polygons, lines, hillshade, dem]
        QgsMapLayerRegistry.instance().addMapLayers(layers)
        
        dem.loadNamedStyle(os.path.join(self.symbologyFolder, self.rasterSymbology, 'demStyle.qml'))
        hillshade.loadNamedStyle(os.path.join(self.symbologyFolder, self.rasterSymbology, 'hillshadeStyle.qml'))
        polygons.loadNamedStyle(os.path.join(self.symbologyFolder, self.vectorSymbology, 'polybkgrd.qml'))
        lines.loadNamedStyle(os.path.join(self.symbologyFolder, self.vectorSymbology, 'linebkgrd.qml'))
        

def run_script(iface, **args):
    '''Keyword Arguments to Start the Script'''
    start = assimStartup(iface)
    
    ''' Global Assignments - These variables cannot be assigned in the __init__ function'''
    global start_date
    global start_hour
    global end_date
    global end_hour
    global keep_old_layers
    
    start_date = args['start_date']
    start_hour = args['start_hour']
    end_date   = args['end_date']
    end_hour   = args['end_hour']
    keep_old_layers = args['keep_old_layers']
    
    print('Assimilation Start Time: %s %s00z' % (start_date, start_hour))
    print('\nAssimilation End Time: %s %s00z' % (end_date, end_hour))

    ''' Create a Nudging Layer Directory '''
    try:
        assimDir = os.path.join(r'C:/assimilation/nudging_layers/swe', end_date)
        os.makedirs(assimDir)
        print('SWE Nudging Folder %s created' % end_date)
        print('\n' + assimDir)

    except:
        print('SWE Nudging Folder already exists or cannot otherwise be created')
        
    ''' List of Rasters, associated raster style definitions, and wildcards '''
    rasters = {'SWE_' + start_date +'05.tif':[os.path.join(start.symbologyFolder, start.rasterSymbology,'swe.qml'), 'SWE_*'],
           'SC_SWE_' + start_date + '05.tif': [os.path.join(start.symbologyFolder,start.rasterSymbology,'SC_SWE_Master.qml'), 'SC_SWE_*'],
           'SC_NESDIS_' + start_date + '.tif': [os.path.join(start.symbologyFolder, start.rasterSymbology, 'SC_NESDIS_Master.qml'), 'SC_NES*']}

    
    if keep_old_layers.lower() == 'no':
        start.clearTheMap()
    
    start.loadBaseLayers()
    
    for raster in rasters:
        start.loadRasters(raster, rasters[raster][0], rasters[raster][1])
    
    start.loadDeltaPoints()