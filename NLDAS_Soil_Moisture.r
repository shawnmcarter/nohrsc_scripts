# This R Script will download NLDAS grib files and calculate the soil moisture content
# (kg/m^2) in the first 20cm of the soil column derived from the mosaic, noah, sac, and vic
# models.  To run this script, edit the 'dates' vector to contain the dates in YYYYMMDD format
# and then from the command line run: Rscript NLDAS_Soil_Moisture.r

####################################################################################
# Snow Analysis and Remote Sensing Center - Office of Water Prediction             #
# Shawn M. Carter                                                                  #
# shawn.carter@noaa.gov                                                            #
####################################################################################

# Required Libraries
library(raster)
library(rgdal)

# Top level folder where all results will be stored
main_dir <- '/net/home/scarter/NLDAS_SM'
# Edit this vector to contain the dates of interests
dates <- c('20161016') 

# Filenames of the grib products to download from the NLDAS ftp site:
mosaic <- 'mosaic.t12z.grbf00'
noah   <- 'noah.t12z.grbf00'
sac    <- 'sac.t12z.grbf00'
vic    <- 'vic.t12z.grbf00'


# Iterate through the dates
for (i in 1:length(dates)){
    # ftp address
    ftp_addr   <- paste('ftp://ldas.ncep.noaa.gov/nldas2/nco_nldas/',
                        substr(dates[i],1,4),
                        '/nldas.', dates[i], sep="")

    # Check for pre-existing folders, if none exists create one.
    if (! dir.exists(file.path(main_dir, dates[i]))){
        dir.create(file.path(main_dir, dates[i])) }
    
    # Move the working folder to the newly created folder
    setwd(file.path(main_dir,dates[i]))

    # Download the files
    download.file(file.path(ftp_addr, mosaic), destfile=mosaic, method='wget', mode='wb')
    download.file(file.path(ftp_addr, noah), destfile=noah, method='wget', mode='wb')
    download.file(file.path(ftp_addr, sac), destfile=sac, method='wget', mode='wb')
    download.file(file.path(ftp_addr, vic), destfile=vic, method='wget', mode='wb')
 
    # Read grib files into a Raster Brick
    mosaic_grid <- readGDAL(mosaic)
    mosaic_grid <- brick(mosaic_grid)

    noah_grid   <- readGDAL(noah)
    noah_grid   <- brick(noah_grid)

    sac_grid    <- readGDAL(sac)
    sac_grid    <- brick(sac_grid)

    vic_grid    <- readGDAL(vic)
    vic_grid    <- brick(vic_grid)

    # Calculate the Soil Moisture in 0-20cm soil column
    mosaic_SM   <- mosaic_grid$band20 + (mosaic_grid$band21 * 0.333333)
    noah_SM     <- noah_grid$band26   + (noah_grid$band27   * 0.333333)
    sac_SM      <- sac_grid$band7     + (sac_grid$band8     * 0.333333)
    vic_SM      <- vic_grid$band27    + (vic_grid$band28    * 0.333333)

    # We need to rotate the rasters to get them in 0-180 longitude versus the 0-360 longitude they are in
    mosaic_SM   <- rotate(mosaic_SM)
    noah_SM     <- rotate(noah_SM)
    sac_SM      <- rotate(sac_SM)
    vic_SM      <- rotate(vic_SM)

    # Project the data into WGS84
    crs <- CRS('+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84')
    crs(mosaic_SM) <- crs
    crs(noah_SM)   <- crs
    crs(sac_SM)    <- crs
    crs(vic_SM)    <- crs

    # Write Soil Moisture Results to GeoTiffs
    writeRaster(mosaic_SM, paste('mosaic_SM_', dates[i], '.tif', sep=""))
    writeRaster(noah_SM, paste('noah_SM_', dates[i], '.tif', sep=""))
    writeRaster(sac_SM, paste('sac_SM_', dates[i], '.tif', sep=""))
    writeRaster(vic_SM, paste('vic_SM_', dates[i], '.tif', sep=""))
}
