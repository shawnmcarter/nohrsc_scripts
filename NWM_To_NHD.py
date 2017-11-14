##Date=string YYYYMMDD
##Hour=string HH
##Model_Type=string analysis_assim
##NHD_Flowlines=vector
##Save_Directory_For_NetCDF=folder 
 

from netCDF4 import Dataset 
from PyQt4.QtCore import *
import urllib2
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
url = ('http://nwcal-dstore.nwc.nws.noaa.gov/nwm'
        '/nwm.%s/%s/nwm.t%sz.%s.channel_rt.tm00.conus.nc' % (Date, Model_Type, 
        Hour, Model_Type))

filename = url.split('/')[-1]
txt_filename = filename[:-2] + 'txt'
nc_file = urllib2.urlopen(url)
with open(os.path.join(Save_Directory_For_NetCDF, filename), 'wb') as output:
    output.write(nc_file.read())

root = Dataset(os.path.join(Save_Directory_For_NetCDF, filename))
flow = root.variables['streamflow'][:]
comids = root.variables['feature_id'][:]
with open(os.path.join(Save_Directory_For_NetCDF, txt_filename), 'wb') as out_file:
    out_file.write('COMID,FLOW\n')
    for i in range(0, len(comids)):
        out_file.write('%s,%s\n' % (comids[i], flow[i]))

csv_file = ('file:///' + os.path.join(Save_Directory_For_NetCDF, txt_filename) + 
                '?type=csv&geomType=none&subsetIndex=no&watchFile=no')
csv = QgsVectorLayer(csv_file, filename[:-4], 'delimitedtext')
QgsMapLayerRegistry.instance().addMapLayer(csv)
layers = QgsMapLayerRegistry.instance().mapLayers()
for layer in layers:
    if 'NHDFlowline_Network' in layer:
        nhd = layers[layer]
join_field = 'COMID'
joinObject = QgsVectorJoinInfo()
joinObject.joinLayerId = csv.id()
joinObject.joinFieldName = join_field
joinObject.targetFieldName = join_field
joinObject.memoryCach = True
nhd.addJoin(joinObject)
