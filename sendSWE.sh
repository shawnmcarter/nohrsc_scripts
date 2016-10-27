#!/bin/bash
DATE=$1

RESULTS_DIR='/net/home/scarter/SNODAS_Development/results/'
NWM_RASTER_OUTPUTS='/net/assim/data/snow_line_raster_NWM'
NWM_VECTOR_OUTPUTS='/net/assim/data/point_data_shape_NWM'
SNODAS_RASTER_OUTPUTS='/net/assim/data/snow_line_raster'

# LIST OF NWM FILES
declare -a NWM_FILES=(SNEQV_ SNOWH_ SOILSAT_TOP_ SNOWT_AVG_ )

# LIST OF SNODAS FILES
declare -a SNODAS_FILES=(ACCET_ FSNO_  SD_ SWE_)

# Copy the Files
for i in "${NWM_FILES[@]}"
do
    cp "${RESULTS_DIR}${i}${DATE}.tif"  "${NWM_RASTER_OUTPUTS}"
done

for i in "${SNODAS_FILES[@]}"
do 
    if [ "${i}" = "SD_" ]; then
        cp "${RESULTS_DIR}${i}${DATE}"05.tif "${SNODAS_RASTER_OUTPUTS}"
    
    elif [ "${i}" = "SWE_" ]; then
        cp "${RESULTS_DIR}${i}${DATE}"05.tif "${SNODAS_RASTER_OUTPUTS}"
     
    else 
         cp "${RESULTS_DIR}${i}${DATE}".tif "${SNODAS_RASTER_OUTPUTS}"
    fi
done

cp "${RESULTS_DIR}nwm_md_based*" "${NWM_VECTOR_OUTPUTS}"
