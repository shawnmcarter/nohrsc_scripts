# nohrsc_scripts
Bash and Python Scripts for Open Source Geospatial Tasks for use in the Office of Water Prediction, NOAA
Scripts authored by Shawn M. Carter

## getSWE.sh

The getSWE.sh bash script downloads the desired SNODAS Assimilation Layers from the operations server.  Because it is copying files on the operations folder, it needs to be run from an operations machine (e.g. ow1).  ~~The script can be invoked with or without command line arguments.  If invoked without a command line argument, the script will use the current date to copy the data to the temporary folder~~.

If the script is moved into a new location, be sure to edit *TEMP_DIR* variable to point to the appropriate temporary folder you will use for the follow-on script, sweGIS.sh.  To prepare the file in a new location:

    $ chmod +x ./getSWE.sh
    $ ./getSWE.sh 2017113006 2016113106

## sweGIS.sh

sweGIS.sh is the follow-on script to getSWE.sh and has to be run from a development machine (e.g. dw7).  The operations machines do not have the required geospatial data libraries, neccessitating the use of two scripts.  This script needs to have model dates ~~and Gamma Flight Mission Number~~ included with the command line when invoked.  ~~Without the argument, the script will assign the *DATE* variable with today's date and 'xxx' as the survey number.

If the scripts have been moved, ensure you edit the *TEMP_DIR* variable to point to the appropriate folder the getSWE.sh script copied into.  

sweGIS.sh first converts the SNODAS NetCDF into a GeoTIFF file.  This step should be removed if/when we get QGIS functioning on the development server as QGIS in Windows does not properly handle HDF5 style NetCDFs.  The next step is to call the gammaShapefile python script which converts the Gamma Survey message into a point shapefile.  Lastly, the GeoTIFF and Shapefile are compressed into zip archive and saved in the folder the *ZIP_DIR* variable points to.

## gammaShapefile.py

This python (2.7) script is normally invoked with the sweGIS.sh bash script.  However, if run as a stand-alone operation it requires two command line arguments (YYYMMDD and xxx, where YYYYMMDD is the date and xxx is the Gamma Mission Survey Number).  

### Function makeFormattedGamma(date)

This function simply re-writes the original Gamma Survey message to include headers.  

### Function shapeFileMaker(svy)

This function takes the newly formatted message and converts it into a point shapefile using GDAL Python bindings.  

## gammaMap.py

This python script must be run from within QGIS (>= 2.12).  Variables for file storage and manipulation are maintained on lines 13-17. 
*  *SWEdir* should point to the root directory where your SNODAS-Gamma Map folders are located.  

*  *bkgrndDir* should point to the folder where the background layers (DEM, Hillshading, Topographic Openness, and Border layers are maintained).  

*  *inputDir* is where you copy the zipped archive created in the sweGIS.sh script.  

*  *dailyDir* is where the script will save the unzipped files.  This is important because one of the first steps is to convert the SNODAS raster by multiplying by 0.001 (converting its units into meters).

*  *mapDir* is where the output map is stored.  

## assim_startup_QGIS.py
This python script is designed to be run from the [ScriptRunner plugin](http://spatialgalaxy.net/2013/03/18/new-version-of-the-qgis-script-runner-plugin/) for QGIS (versions >= 2.12).  To prepare and install this plugin, edit the source so that the directory location variables in the beginning of the assimStartup() class point to the folder structure on your computer.  Then import the script into the script runner plugin.  This script requires 5 command line arguments that should be used as below in the ScriptRunner plugin dialog:

    start_date='YYYYMMDD', start_hour='HH', end_date='YYYYMMDD', end_hour='06', keep_old_files='no'
    
Be sure to enclose variable values in apostrophes and separate variables with commas.  
