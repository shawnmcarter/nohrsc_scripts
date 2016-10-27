#!/bin/bash

# Test if you are on dw7
if ! [ "$(gdalinfo --version)" ]; then
    printf "Run this script from dw7\n"
fi

# Directory Variables
TEMP_DIR="/net/home/scarter/SNODAS_Development/temp/"
RESULTS_DIR="/net/home/scarter/SNODAS_Development/results/"
ZIP_DIR="/net/home/scarter/SWE_Results/"

# Date Variables
DATE1=$1
DATE2=$2
#GAMMA=$3

if [ -z ${DATE1} ]; then
    printf "Script Usage: ./sweGIS.sh {DTG} {DTG} \nDTG Format YYYYMMDDHH\n"
    exit 1
fi

# Delete the Results Folder
printf "\nDeleting Files in the Results Directory! **************************************************\n\n"
if [ "$(ls -A $RESULTS_DIR)" ]; then
    rm ${RESULTS_DIR}*
fi


# Snow Depth and SWE Rasters do not have NoData Assigned, this step fixes that:
printf "\nAssigning NoData Values to the Snow Depth, Snow Water Equivalent, and Snowfall Rasters ***********************\n\n"
gdal_translate ${TEMP_DIR}SD_${DATE2:0:8}05.tif -a_nodata -99999 ${RESULTS_DIR}SD_${DATE2:0:8}05.tif
gdal_translate ${TEMP_DIR}SWE_${DATE2:0:8}05.tif -a_nodata -99999 ${RESULTS_DIR}SWE_${DATE2:0:8}05.tif
#gdal_translate ${TEMP_DIR}sfav2_CONUS_${DATE2:0:8}12.tif -a_nodata -99999 ${RESULTS_DIR}Snowfall_$DATE2:0:8}12.tif

# Copy the remaining SNODAS Files to the Results Directory
printf "\nCopying the rest of the rasters to the Results Directory ******************************************\n\n"
cp -t ${RESULTS_DIR} SC_NESDIS* SC_SWE* 

# Assign projection and copy the Delta Points File to the Results Directory
printf "\nProjecting the Delta Points Shapefile *************************************************************\n\n"
ogr2ogr -a_srs EPSG:4269 ${RESULTS_DIR} ${TEMP_DIR}ssm1054_md_based_${DATE1}_${DATE2}.shp

# Run the getNWM script
/net/home/scarter/SNODAS_Development/scripts/NWM_nc_tools_v1.1/getNWM.sh ${DATE2:0:8} ${DATE2:8:10}

# Create a NWM LCC projection version of the Points Delta Shapefile
ogr2ogr -t_srs '+proj=lcc +lat_1=30 +lat_2=60 +lat_0=40.0000076294 +lon_0=-97 +x_0=0 +y_0=0 +a=6370000 +b=6370000 +units=m +no_defs' ${RESULTS_DIR}nwm_md_based_${DATE1}_${DATE2}.shp ${RESULTS_DIR}ssm1054_md_based_${DATE1}_${DATE2}.shp

python /net/home/scarter/SNODAS_Development/scripts/NWM_Deltas.py ${DATE1} ${DATE2}

# Zip the Results Files 
printf "\nZipping all the files into the SWE_Results Directory *********************************************\n\n"

# Zip the results for exfil
cd ${RESULTS_DIR}
zip SNODAS_${DATE2}.zip * -x NWM_Deltas/
