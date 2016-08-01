from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from qgis.analysis import *
from PyQt4.QtCore import *
from PyQt4.QtCore import QFileInfo
from PyQt4.QtXml import QDomDocument
from PyQt4.QtGui import *
from zipfile import ZipFile 
import os, shutil, time

# Directory variables
SWEdir = u'C:/SNODAS'
bkgrndDir = u'C:/SNODAS/Bkgrnds'
inputDir = u'C:/SNODAS/inputs'
dailyDir = u'C:/SNODAS/daily'
mapDir = u'C:/SNODAS/outputs'

# Unzip Daily Files inot the daily directory.  The SNODAS raster and Gamma point
# file should be located in the inputDir folder

def unZip():
    for files in os.listdir(dailyDir): # Hack to avoid having to deal with multiple files to manipulate
        filePath = os.path.join(dailyDir, files)
        try:
            if os.path.isfile(filePath):
                os.remove(filePath)
        except Exception as e:
            print(e)

    dates = []  # Get the date of the input files 
    for x in os.listdir(inputDir):  
        dates.append(int(x[7:-4]))
        
    
    date = str(max(dates))


    # Unzip the files in the input directory
    with ZipFile(os.path.join(inputDir, 'SNODAS_'+ date + '.zip'), 'r') as dailyZip:
        dailyZip.extractall(inputDir)
    
    for i in os.listdir(inputDir):
        if 'gamma_points' in i:
            survey = i[25:29]
            newName = 'gamma_points.' + i[-3:]
            shutil.move(os.path.join(inputDir, i), os.path.join(dailyDir, newName))

    return date, survey

def convertToMeters(date):
    # Function to convert SNODAS data into meters
    uri = os.path.join(inputDir, 'zz_ssmv11034tS__T0001TTNATS' + date + '05HP001.tif')
    rasterName = 'SWE_Raw'
    output = os.path.join(dailyDir, 'SNODAS.tif')

    raw_swe = QgsRasterLayer(uri, rasterName)

    swe = QgsRasterCalculatorEntry()
    swe.raster = raw_swe
    swe.bandNumber = 1
    swe.ref = rasterName + '@1'
    exp = '%s * 0.001' % swe.ref

    e = raw_swe.extent()
    w = raw_swe.width()
    h = raw_swe.height()
    entries = [swe]

    scale = QgsRasterCalculator(exp, output, 'GTiff', e, w, h, entries)
    scale. processCalculation()
    del raw_swe

    
    os.remove(os.path.join(inputDir,uri))

def makeMapTitle(date, survey):
    expression = """<html>
<head>
<style> h2 {font-family:"Arial"; font-size:16}</style>
</head>
<body>
<h2>Gamma Flight Survey #""" + survey + """ Status: """ + date + """</h2>
</body>
</html>"""


    with open(os.path.join(bkgrndDir, 'title.html'), 'wb') as titleFile:
        titleFile.write(expression)

def exportPDF():
    # Location of the saved QGIS project and Composer Template
    project_path = os.path.join(SWEdir,'swe.qgs')
    template_path = os.path.join(SWEdir,'print.qpt')

    # Set output DPI
    dpi = 300

    canvas = QgsMapCanvas()
    # Load the SWE Project
    QgsProject.instance().read(QFileInfo(project_path))
    time.sleep(5)
    bridge = QgsLayerTreeMapCanvasBridge(QgsProject.instance().layerTreeRoot(), canvas)
    bridge.setCanvasLayers()

    template_file = file(template_path)
    template_content = template_file.read()
    template_file.close()

    document = QDomDocument()
    document.setContent(template_content)
    composition = QgsComposition(canvas.mapSettings())
    composition.loadFromTemplate(document, substitutionMap = None, addUndoCommands = False)
    
    map_item = composition.getComposerItemById('map')
    map_item.setMapCanvas(canvas)
    
    composition.refreshItems()
    composition.exportAsPDF(os.path.join(mapDir, 'daily_' + date + '.pdf'))
    

    
date, survey = unZip()
convertToMeters(date)
makeMapTitle(date, survey)
exportPDF()