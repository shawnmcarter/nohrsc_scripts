#!/bin/bash

# This script downloads the SNODAS assimilation layers to a temporary folder.
# This script must be run from the ow1 shell.

DATE1=$1
DATE2=$2
#GAMMA=$3

if [ -z "$DATE1" ]
then 
    printf "Script Usage:  ./getSWE.sh DTG1 DTG2 \n Format: YYYYMMDDHH YYYYMMDDHH\n"
    exit 1
fi

# File and Directory Variables
DELTAS="ssm1054_md_based_${DATE1}_${DATE2}.*"
TEMP_DIR="/net/home/scarter/SNODAS_Development/temp/"
SWE_DIR="/net/assim/data/snow_line_raster/"
DELTA_DIR="/operations/ssm/assimilation/point_data_shape/"
#GAMMA_DIR="/operations/gamma/SURVEY2017/dbase.d/"
NET_ASSIM="/net/assim/data/point_data_shape/"
SNOWFALL_DIR="/nwcdev/nsadev/snowfall_v2_devel/sfav2/sfav2_${DATE2:0:8}/"
SNOWFALL="sfav2_CONUS_${DATE2:0:8}12.tif"
# Exectution Code
# Delete old files in the temp directory copy new files into it.
if [ "$(ls -A $TEMP_DIR)" ]; then
    printf "\nDeleting old Temp Directory\n"
    rm ${TEMP_DIR}*
    printf "\nCopying files\n"
    cp ${SWE_DIR}AssimLayers_${DATE2:0:8}05.tar.gz ${TEMP_DIR}
    cp ${DELTA_DIR}${DELTAS} ${TEMP_DIR}
    cp ${DELTA_DIR}${DELTAS} ${NET_ASSIM}
    #cp ${SNOWFALL_DIR}${SNOWFALL} ${TEMP_DIR}
#    if ! [ ${GAMMA} == "No" ]; then
#        cp ${GAMMA_DIR}*${DATE2:2}*.dbase ${TEMP_DIR}
#    fi
else
    cp ${SWE_DIR}AssimLayers_${DATE2:0:8}.tar.gz ${TEMP_DIR}
    cp ${DELTA_DIR}${DELTAS} ${TEMP_DIR}
    cp ${DELTA_DIR}${DELTAS} ${NET_ASSIM}
    #cp ${SNOWFALL_DIR}${SNOWFALL} ${TEMP_DIR}
#    if ! [ ${GAMMA} == "No" ]; then
#        cp ${GAMMA_DIR}*${DATE2:2}*.dbase ${TEMP_DIR}
#    fi
fi

# Untar the Assim Layers
printf "\nUntar the Assim Layers\n\n"
tar -xvf ${TEMP_DIR}AssimLayers_${DATE2:0:8}05.tar.gz -C ${TEMP_DIR}
