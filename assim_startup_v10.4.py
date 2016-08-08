import arcpy
import os

arcpy.AddMessage( "NOHRSC Assimilation Layers ArcGIS 10.4 Loading Script\nVersion 1.5\nPurpose: This script is used to upload the necessary\ndatasets used for NOHRSC Assimilation.\n\n" )


''' Edited and updated to ArcPy 10.4 by Shawn Carter '''


## Set ArcPy Environmental Conditions
arcpy.overwriteOutput = True

## Define the ArcMap Project
mxd = arcpy.mapping.MapDocument("CURRENT")
df =  arcpy.mapping.ListDataFrames(mxd, "*")[0]

## Variables
start_date =      arcpy.GetParameterAsText(0)
start_hour =      arcpy.GetParameterAsText(1) 
end_date =        arcpy.GetParameterAsText(2)
end_hour =        arcpy.GetParameterAsText(3)
keep_old_layers = arcpy.GetParameterAsText(4)

## Directories
sourceFolder    = r'C:/Users/shawn.carter/Desktop/GIS_Files' #Change Me when Installed
workingFolder   = r'C:/assimilation'                         #Change Me when Installed
symbologyFolder = r'C:/Users/shawn.carter/Documents/Assim/symbology' #Change Me when Installed
vectorSymbology = r'/shapefile' + '/'
rasterSymbology = r'/raster' + '/'
vectorData      = r'/point_data_shape' + '/'
rasterData      = r'/snow_line_raster' + '/'

source_vectorData = sourceFolder + vectorData
source_rasterData = sourceFolder + rasterData

working_vectorData = workingFolder + vectorData
working_rasterData = workingFolder + rasterData


arcpy.AddMessage("Assimilation Start Time: " + start_date + start_hour + '00Z')
arcpy.AddMessage("Assimilation End Time: " + end_date + end_hour+'00Z\n\n')

## Create Nudging Layers Directory
try:
    assimDir = 'C:/assimilation/nudging_layers/swe/' + end_date + '/'
    os.makedirs(assimDir)
    arcpy.AddMessage('SWE Nudging Folder for ' + end_date + ' created.')
    arcpy.AddMessage(assimDir)

except:
    arcpy.AddMessage('SWE Nudging folder already exists or cannot be created.')   


## List of Raster Names and Their Associated Raster Style Layers (in Dictionary form for ease or retrieval)
rasters = {'SWE_' + start_date +'05.tif':[symbologyFolder + rasterSymbology + 'MASTER_Raster_BIG.lyr', 'SWE_*'],
           'SC_SWE_' + start_date + '05.tif': [symbologyFolder + rasterSymbology + 'SC_SWE_MASTER.lyr', 'SC_SWE_*'],
           'SC_NESDIS_' + start_date + '.tif': [symbologyFolder + rasterSymbology + 'SC_NESDIS_MASTER.lyr', 'SC_NES*']}

## Clear the map from previous assimilation data
def clearTheMap(layerName):
    for layer in layerName:
        for lyr in arcpy.mapping.ListLayers(mxd, layer, df):
            if arcpy.Exists(lyr):
                arcpy.AddMessage('Removed ' + str(lyr) + ' from the map.')
                arcpy.mapping.RemoveLayer(df, lyr)

            else:
                arcpy.AddMessage('No %s layer present' % layer)

    arcpy.RefreshTOC()
    arcpy.RefreshActiveView()


## Load and Style the Delta Points Shapefile
def loadDeltaPoints():
    deltaSHP = 'ssm1054_md_based_' + start_date + start_hour + '_' + end_date + end_hour + '.shp'
    if os.path.isfile(os.path.join(source_vectorData + deltaSHP)):
        arcpy.Copy_management(source_vectorData + deltaSHP, working_vectorData + deltaSHP)
        
        deltaLayer    = arcpy.mapping.Layer(working_vectorData + deltaSHP)
        arcpy.mapping.AddLayer(df, deltaLayer, "AUTO_ARRANGE")
        
        deltaList     = arcpy.mapping.ListLayers(mxd, '*', df)[0] 
        deltaStyle    = symbologyFolder + vectorSymbology + 'ssm1054_md_based_MASTER.lyr'
        
        arcpy.ApplySymbologyFromLayer_management(deltaList, deltaStyle)
        arcpy.AddMessage(deltaSHP[:-4] + ' shapefile loaded....')

    else:
        arcpy.AddMessage(deltaSHP + ' Does Not Exist.')

def loadRasters(raster, rasterStyle, layerName):
    if os.path.isfile(os.path.join(source_rasterData, raster)):
        arcpy.Copy_management(source_rasterData + raster, working_rasterData + raster)

        loadRaster    = arcpy.mapping.Layer(working_rasterData + raster)
        arcpy.mapping.AddLayer(df, loadRaster, "AUTO_ARRANGE")
        
        rasterLayer      = arcpy.mapping.ListLayers(mxd, layerName, df)[0]
        layerStyle      = arcpy.mapping.Layer(rasterStyle)
        arcpy.mapping.UpdateLayer(df, rasterLayer, layerStyle, True)
        arcpy.AddMessage(str(rasterLayer)[:-4] + ' raster file loaded...')
    else:
        arcpy.AddMessage(raster + ' Does Not Exist.')
        
def main():
    if keep_old_layers.lower() == 'no':
        clearTheMap(['ssm*', 'SWE*', 'SC_SWE*', 'SC_NE*'])
    
    loadDeltaPoints()
    
    for raster in rasters:
        loadRasters(raster, rasters[raster][0], rasters[raster][1])

main()





