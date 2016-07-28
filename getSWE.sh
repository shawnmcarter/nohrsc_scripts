#!/bin/bash

# This script downloads the SNODAS and Gamma Messages to a temporary folder.
# This script must be run from the ow1 shell.
# Get the date in YYYYMMDD format.  DATE variable is command line argument
# If command line argument is unused, it will use today's date

DATE=$1

if [ -z "$DATE" ]
then
    DATE=$(date +"%Y%m%d")
fi

SWE="zz_ssmv11034tS__T0001TTNATS${DATE}05HP001.nc"

TEMP_DIR="/net/home/scarter/SNODAS_Development/temp"
SWE_DIR="/net/ftp/products/collaborators"
GAMMA_DIR="/operations/gamma/SURVEY2016/testing"

# Execution Code
if [ "$(ls -A $TEMP_DIR)" ]; then
    rm ${TEMP_DIR}/*
    cp ${SWE_DIR}/${SWE} ${TEMP_DIR}
    cp ${GAMMA_DIR}/*${DATE:2}*.dbase ${TEMP_DIR}

else
    cp ${SWE_DIR}/${SWE} ${TEMP_DIR}
    cp ${GAMMA_DIR}/*${DATE:2}*.dbase ${TEMP_DIR}

fi
