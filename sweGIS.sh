#!/bin/bash

# This script converts the SNODAS SWE NetCDF file and converts it into a GeoTIFF.
# Following GeoTIFF conversion, it initiates the gammaShapefile python script.
# The last step is to compress the resultant files into a tar folder.

# Location of a files
TEMP_DIR="/net/home/scarter/SNODAS_Development/temp"

# Date variable can be explicitly set with a command line argument.
# If command line argument is not used, the script will use today's date

DATE=$1

if [ -z ${DATE} ]; then
    DATE=$(date +"%Y%m%d")
fi

SWE="zz_ssmv11034tS__T0001TTNATS${DATE}05HP001.nc"
SWE_TIFF="${SWE:0:(-3)}.tif"
gdal_translate  NETCDF:"${TEMP_DIR}/${SWE}":Snow_Water_Equivalent -a_srs EPSG:4326  ${TEMP_DIR}/${SWE_TIFF}
