##Start_Date=string YYYYMMDDHH
##End_Date=string YYYYMMDDHH
##Processing_Region=string West
##Final_Processing_Region=string US 

from PyQt4.QtCore import *
from PyQt4.QtGui  import *
import processing as pro 
import os 
from qgis.core import * 
from qgis.gui import *


# Variables for the tool 
process_dir = 'C:/Users/shawn.carter/Documents/Assim/data/%s/nudging_layers' % End_Date[:-2]
final_output_region_dir = 'C:/Users/shawn.carter/Documents/Assim/assim_process_regions'
final_points_dir = 'C:/Users/shawn.carter/Documents/Assim/point_data_shape_new'
region = Processing_Region
final_region = Final_Processing_Region

assim_points = 'ssm1054_md_based_%s_%s_%s.shp' % (Start_Date, End_Date, region)
final_assim_points = 'ssm1054_md_based_%s_%s_%s.shp' % (Start_Date, End_Date, final_region)
process_region = 'process_region_%s_%s.shp' % (End_Date[:-2], region)
final_process_region = 'process_region_%s_%s_swe_%s.shp' % (Start_Date, End_Date, final_region)


# Copy the process region to the process_region directory
process_region_layer = QgsVectorLayer(os.path.join(process_dir, process_region), 'process region', 'ogr')
QgsVectorFileWriter.writeAsVectorFormat(process_region_layer, os.path.join(final_output_region_dir, final_process_region), 'UTF-8', None, 'ESRI Shapefile')

# Create a 1,000 meter buffer around the process region 
pro.runalg('qgis:fixeddistancebuffer',
        {'INPUT'     : os.path.join(process_dir, process_region),
         'DISTANCE'  : 0.009,
         'SEGMENTS'  : 5,
         'DISSOLVE'  : False,
         'OUTPUT'    : os.path.join(process_dir, 'full_buffer_' + process_region)
})


# Use geoprocessing to remove the interior of the buffered process region 
pro.runalg('qgis:symmetricaldifference',
        {'INPUT' : os.path.join(process_dir, 'full_buffer_' + process_region), 
          'OVERLAY' : os.path.join(process_dir, process_region),
          'OUTPUT' : os.path.join(process_dir, 'buffer_' + process_region)
          })

# Convert the buffer to a raster 
pro.runalg('gdalogr:rasterize',
                {'INPUT' : os.path.join(process_dir, 'buffer_' + process_region), 
                  'FIELD' : 'Id',
                  'DIMENSIONS' : 1,
                  'WIDTH' : 0.008333333,
                  'HEIGHT' : 0.008333333,
                  'RAST_EXT' : '-130.516666667,-62.25,24.1,58.2333333333',
                  'TFW' : False,
                  'RTYPE': 5,
                  'NO_DATA' : '0',
                  'COMPRESS' : 4,
                  'JPEGCOMPRESSION' : 75,
                  'ZLEVEL' : 6,
                  'PREDICTOR' : 1,
                  'TILED' : False,
                  'BIGTIFF' : 0,
                  'EXTRA' : '',
                  'OUTPUT' : os.path.join(process_dir, 'buffer_process_reg.tif')
                  })
                  
# Convert the raster to points
pro.runalg('grass7:r.to.vect', 
            {'input' : os.path.join(process_dir, 'buffer_process_reg.tif'),
              'type' : 1,
              '-s' : False,
              'GRASS_REGION_PARAMETER' : '-130.516666667,-62.25,24.1,58.2333333333',
              'GRASS_OUTPUT_TYPE_PARAMETER' : 1,
              'output' : os.path.join(process_dir, 'buffer_points_%s_%s.shp' % (End_Date[:-2], region))
              })

# Create a sequential POINTID field in the points layer - delete every 5th point 
points_layer = QgsVectorLayer(os.path.join(process_dir, 'buffer_points_%s_%s.shp' % (End_Date[:-2], region)), 'points', 'ogr')
points_layer.dataProvider().addAttributes([QgsField("POINTID", QVariant.Int)])
points_layer.updateFields()

i=0
with edit(points_layer):
    for feat in points_layer.getFeatures():
        if i % 5 == 0:
            points_layer.deleteFeature(feat.id())
        else:
            feat['POINTID'] = i
            points_layer.updateFeature(feat)
        i += 1
        

# Merge the buffer points and the assim points layers 
pro.runalg('qgis:mergevectorlayers',
            {'LAYERS': (os.path.join(process_dir, assim_points) + ';' + os.path.join(process_dir, 'buffer_points_%s_%s.shp' % (End_Date[:-2], region))), 
              'OUTPUT': os.path.join(final_points_dir, final_assim_points)
              })

# Add XY Fields to the merged dataset 
merged_layer = QgsVectorLayer(os.path.join(final_points_dir, final_assim_points), 'final points', 'ogr')
merged_layer.dataProvider().addAttributes([QgsField("POINT_X", QVariant.Double), QgsField("POINT_Y", QVariant.Double), QgsField("X", QVariant.Double), QgsField("Y",QVariant.Double)])
merged_layer.updateFields()

with edit(merged_layer):
    for feat in merged_layer.getFeatures():
        feat['POINT_X'] = feat.geometry().asPoint()[0]
        feat['POINT_Y'] = feat.geometry().asPoint()[1]
        feat['X'] = feat.geometry().asPoint()[0]
        feat['Y'] = feat.geometry().asPoint()[1]
        merged_layer.updateFeature(feat)


