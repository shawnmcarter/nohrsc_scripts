#!/bin/bash

# This script converts the SNODAS SWE NetCDF file and converts it into a GeoTIFF.
# Following GeoTIFF conversion, it initiates the gammaShapefile python script.
# The last step is to compress the resultant files into a tar folder.

# Directory Variables
TEMP_DIR="/net/home/scarter/SNODAS_Development/temp"
RESULTS_DIR="/net/home/scarter/SNODAS_Development/results"
ZIP_DIR="/net/home/scarter/SWE_Results"

# Date variable can be explicitly set with a command line argument.
# If command line argument is not used, the script will use today's date

DATE=$1
SVY=$2

if [ -z ${DATE} ]; then
    DATE=$(date +"%Y%m%d")
fi

if [ -z ${SVY} ]; then
    SVY="xxx"
fi 

# Ensure results folder is empty
if [ "$(ls -A $RESULTS_DIR)" ]; then
    rm ${RESULTS_DIR}/*
fi

# Convert the NetCDF into a TIFF (avoids GDAL issues in Windows with HDF5 formatted NetCDF
SWE="zz_ssmv11034tS__T0001TTNATS${DATE}05HP001.nc"
SWE_TIFF="${SWE:0:(-3)}.tif"
gdal_translate  NETCDF:"${TEMP_DIR}/${SWE}":Snow_Water_Equivalent -a_srs EPSG:4326  ${RESULTS_DIR}/${SWE_TIFF}

# Convert the Gamma Message into a shapefile
python gammaShapefile.py ${DATE} ${SVY}

# Tar the results
cd ${RESULTS_DIR}
zip ${ZIP_DIR}/SNODAS_${DATE} *
