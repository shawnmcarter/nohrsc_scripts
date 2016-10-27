import arcpy
from arcpy.sa import *
import os


arcpy.CheckOutExtension("spatial")

arcpy.AddMessage( "Snow Analysis and Remote Sensing Center Assimilation Layers ArcGIS 10.4 Loading Script\nVersion 1.5\nPurpose: This script is used to upload the necessary\ndatasets used for SNODAS Assimilation.\n\n" +\
	"This tool should be run with an active SNODAS Assimilation .mxd.")


''' Edited and updated to ArcPy 10.4 by Shawn Carter '''

## Set Arcpy Environmental Conditions
arcpy.overwriteOutput = True

## Define the ArcMap Project
mxd = arcpy.mapping.MapDocument("CURRENT")
df  = arcpy.mapping.ListDataFrames(mxd, "*")[0]

## Variables
start_date      = arcpy.GetParameterAsText(0)
end_date        = arcpy.GetParameterAsText(1)
keep_old_layers = arcpy.GetParameterAsText(2)


if start_date[-2:] == '06':
	rasterTime = '05'
elif start_date[-2:] == '12':
	rasterTime = '12'


## Directories - These need to be edited in a new machine / Environmental
sourceFolder    = 'Z:/data' 										# Location that contains the snow_line_raster and point_data_shape folders
workingFolder   = 'C:/assimilation'                        			# Location where copies of files are stored locally
symbologyFolder = 'C:/assimilation/symbology' 						# Location that the various layer styles are maintained

## Directories II - These should not need to be edited if you follow the standard file structure
vectorSymbology    = os.path.join(symbologyFolder, 'shapefile')
rasterSymbology    = os.path.join(symbologyFolder, 'raster')
vectorData         = os.path.join(sourceFolder, 'point_data_shape')
rasterData         = os.path.join(sourceFolder, 'snow_line_raster')
rasterData_NWM     = os.path.join(sourceFolder, 'snow_line_raster_NWM')
vectorData_NWM	   = os.path.join(sourceFolder, 'point_data_shape.NWM')
working_vectorData = os.path.join(workingFolder, 'point_data_shape')
working_rasterData = os.path.join(workingFolder, 'snow_line_raster')

arcpy.AddMessage('Assimilation Start Time: %s00Z' % start_date)
arcpy.AddMessage('Assimilation End Time: %s00Z' % end_date)

## Create Nudging Layers Directory
try:
	assimDir = 'C:/assimilation/nudging_layers/swe/%s' % end_date
	os.makedirs(assimDir)
	arcpy.AddMessage('SWE Nudging Folder for %s created' % end_date)
	arcpy.AddMessage(assimDir)

except:
	arcpy.AddMessage('SWE Nudging Folder already exists or cannot be created.')

## List of raster names and their associated raster style layers (in dictionary form for ease of retrieval)
snodas_rasters = {  'SWE_%s%s.tif' % (end_date[:-2], rasterTime)   : [os.path.join(rasterSymbology, 'MASTER_Raster_BIG.lyr'), 'SWE_*'], 
					'SC_SWE_%s%s.tif' % (end_date[:-2], rasterTime)   : [os.path.join(rasterSymbology, 'SC_SWE_MASTER.lyr'), 'SC_SWE_*' ],
					'SC_NESDIS_%s.tif' % start_date[:-2] : [os.path.join(rasterSymbology, 'SC_NESDIS_MASTER.lyr'), 'SC_NES*' ],
					'SNOWH_%s.tif' % end_date[:-2]   : [os.path.join(rasterSymbology, 'SNOWH_MASTER.lyr'), 'SNOWH*'],
					'SNOWT_AVG_%s.tif' % end_date[:-2]   : [os.path.join(rasterSymbology, 'SNOWT_AVG_MASTER.lyr'), 'SNOWT*'],
					'SOILSAT_TOP_%s.tif' % end_date[:-02]  : [os.path.join(rasterSymbology, 'SOILSAT_TOP.lyr'), 'SOILSAT*'],
					'SNEQV_%s.tif' % end_date[:-2] : [os.path.join(rasterSymbology, 'SNEQV_MASTER.lyr'), 'SNEQV*']}

## Clear the map from previous assimilation point_data_shape
def clearTheMap(layerName):
	for layer in layerName:
		for lyr in arcpy.mapping.ListLayers(mxd, layer, df):
			if arcpy.Exists(lyr):
				arcpy.AddMessage('Removed %s layer from the map' % str(lyr))
				arcpy.mapping.RemoveLayer(df, lyr)

			else:
				arcpy.AddMessage('No %s layer present' % layer)

	arcpy.RefreshTOC()
	arcpy.RefreshActiveView()


## Load and Style the Delta Points shapefile
def loadDeltaPoints():
	deltaSHP = 'ssm1054_md_based_%s_%s.shp' % (start_date, end_date)
	deltaNWM = 'nwm_md_based_%s_%s.shp' % (start_date, end_date)
	for i in (deltaSHP, deltaNWM):
		if os.path.isfile(os.path.join(vectorData, deltaSHP)):
			arcpy.Copy_management(os.path.join(vectorData, deltaSHP), os.path.join(working_vectorData, deltaSHP))

			deltaLayer = arcpy.mapping.Layer(os.path.join(working_vectorData, deltaSHP))
			arcpy.mapping.AddLayer(df, deltaLayer, "AUTO_ARRANGE")

			deltaList  = arcpy.mapping.ListLayers(mxd, '*', df)[0]
			deltaStyle = os.path.join(vectorSymbology, 'ssm1054_md_based_MASTER.lyr')

			arcpy.ApplySymbologyFromLayer_management(deltaList, deltaStyle)
			arcpy.AddMessage('%s shapefile loaded' % deltaSHP[:-4])

		elif os.path.isfile(os.path.join(vectorData_NWM, deltaNWM)):
			arcpy.Copy_management(os.path.join(vectorData, deltaNWM), os.path.join(working_vectorData, deltaNWM))
			
			deltaNWM_Layer = arcpy.mapping.Layer(os.path.join(working_vectorData, deltaNWM))
			arcpy.mapping.AddLayer(df, deltaNWM_Layer, "AUTO_ARRANGE")

			deltaNWMList = arcpy.mapping.ListLayers(mxd, '*', df)[0]
			deltaNWMStyle = os.path.join(vectorSymbology, 'nwm_md_based_MASTER.lyr')

			arcpy.ApplySymbologyFromLayer_management(deltaNWMList, deltaNWMSTyle)
			arcpy.AddMessage('%s shapefile loaded' % deltasNWM[:-4])
			
		else:
			arcpy.AddMessage('%s does not exist' % deltaSHP[:-4])

## Load and Style the Raster Data 
def loadRasters(raster, rasterStyle, layerName, visible):
	if os.path.isfile(os.path.join(rasterData, raster)):
		arcpy.Copy_management(os.path.join(rasterData, raster), os.path.join(working_rasterData, raster))
		arcpy.CalculateStatistics_management(os.path.join(working_rasterData, raster))
		loadRaster    = arcpy.mapping.Layer(os.path.join(working_rasterData, raster))
		arcpy.mapping.AddLayer(df, loadRaster, "AUTO_ARRANGE")
		arcpy.AddMessage('Loading %s' % raster[:-4])
		rasterLayer   = arcpy.mapping.ListLayers(mxd, layerName, df)[0]
		layerStyle    = arcpy.mapping.Layer(rasterStyle)
		arcpy.mapping.UpdateLayer(df, rasterLayer, layerStyle, True)
		rasterLayer.visible = visible
		arcpy.AddMessage('%s raster file loaded.....' % str(rasterLayer)[:-4])

	elif os.path.isfile(os.path.join(rasterData_NWM, raster)):
		arcpy.Copy_management(os.path.join(rasterData_NWM, raster), os.path.join(working_rasterData, raster))
		arcpy.CalculateStatistics_management(os.path.join(working_rasterData, raster))
		loadRaster = arcpy.mapping.Layer(os.path.join(working_rasterData, raster))
		arcpy.mapping.AddLayer(df, loadRaster, "AUTO_ARRANGE")
		arcpy.AddMessage('Loading %s' % raster[:-4])
		rasterLayer = arcpy.mapping.ListLayers(mxd, layerName, df)[0]
		layerStyle = arcpy.mapping.Layer(rasterStyle)
		arcpy.mapping.UpdateLayer(df, rasterLayer, layerStyle, True)
		rasterLayer.visible = visible
		arcpy.AddMessage('%s raster file loaded.....' % str(rasterLayer)[:-4])
	else:
		arcpy.AddMessage('%s Does Not Exist' % raster)

def main():
	if keep_old_layers.lower() == 'no':
		clearTheMap(['ssm*', 'SWE*', 'SC_SWE*', 'SC_NE*', 'SNEQV*', 'SNOW*', 'SOIL*'])
	
	loadDeltaPoints()

	## Load the SNODAS Rasters
	for raster in snodas_rasters:
		loadRasters(raster, snodas_rasters[raster][0], snodas_rasters[raster][1], True)

	## Calculate Model Deltas
	swe = Raster(os.path.join(working_rasterData, 'SWE_%s05.tif' % end_date[0:-2]))
	sneqv = Raster(os.path.join(working_rasterData, 'SNEQV_%s.tif' % end_date[0:-2]))
	delta = swe-sneqv
	delta.save(os.path.join(working_rasterData, 'Model_Deltas_%s-%s.tif' % (start_date, end_date)))
	delta_tif = 'Model_Deltas_%s-%s.tif' % (start_date, end_date)
	arcpy.CalculateStatistics_management(os.path.join(working_rasterData, delta_tif))
	delta_layer = arcpy.mapping.Layer(os.path.join(working_rasterData, delta_tif))
	arcpy.mapping.AddLayer(df, delta_layer, "AUTO_ARRANGE")
	rasterLayer = arcpy.mapping.ListLayers(mxd, 'Model_Deltas*', df)[0]
	layerStyle = arcpy.mapping.Layer(os.path.join(rasterSymbology, 'Model_Deltas.lyr'))
	arcpy.mapping.UpdateLayer(df, rasterLayer, layerStyle, True)
	rasterLayer.visible = True

	

main()
