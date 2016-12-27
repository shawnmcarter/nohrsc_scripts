library(rgdal)
library(raster)


##########################################################################################################
#                                    Setup and Variable Assignments                                      #
##########################################################################################################
# Surpress warnings and set the tmp directory to the scratch disk
startTime <- Sys.time()
options(warn = -1)
rasterOptions(tmpdir="/disks/scratch") #make sure we don't fill up home
rasterOptions(maxmemory=1e+09)         #increase available memory to speed up raster operations

# Directory Variables
swe_dir         <- '/net/ftp/pub/products/collaborators'
swe_normals_dir <- '/net/lfs0data5/SNODAS_normals_2016/SNODAS_SWE_normals_2016'
#sd_normals_dir  <- '/net/lfs0data5/SNODAS_normals_2016/SNODAS_SD_normals_2016'

# Arguments from environment variables
args            <- commandArgs(TRUE)
date_YYYYMMDD   <- args[1] 

# Get system time or receive time from input argument
if (is.na(date_YYYYMMDD)){
    date_YYYYMMDD       <- as.POSIXlt(Sys.Date())
    date_YYYYMMDD_str   <- format(date_YYYYMMDD, format = '%Y%m%d')

    cat(paste('Environment variable DATE_YYYYMMDD not provided.\n', 
            'Using default system date:', date_YYYYMMDD_str, '\n'))
}

# Check to make sure command line argument date input is correctly formatted
tryCatch({
    date_YYYYMMDD       <- as.POSIXlt(date_YYYYMMDD, format='%Y%m%d')
    date_YYYYMMDD_str   <- format(date_YYYYMMDD, format = '%Y%m%d')},
    error = function(e) {
        stop(paste('Environment variable DATE_YYYYMMDD provided in wrong format\n',
             'Format is YYYYMMDD. ', date_YYYYMMDD_str, ' is invalid.\n'))
})

# Calculate the day of water year (DOWY)
source('calculate_DOWY.r')
dowy <- get_dowy(date_YYYYMMDD)[[1]]
date_HH = '05'
water_year <- getStartYear(date_YYYYMMDD)

############################################################################################################
#                                     Reading the Input Layers                                             #
############################################################################################################
# Concatenate the filename structure with date variables 
SWELayer_file <- paste('zz_ssmv11034tS__T0001TTNATS', date_YYYYMMDD_str, date_HH, 'HP001.nc', sep='')
cat(paste('\n\nReading SWE Layer: ', SWELayer_file, '\n'))

# Read the SWE daily layer as a R raster, with a little bit of error handling.
tryCatch({
    SWELayer <- raster(file.path(swe_dir, SWELayer_file))},
    error = function(e) {
        stop(paste('SWE Layer', SWELayer_file, 'Not Found!\n'))
})

cat(paste('Finished reading SWE Layer:', SWELayer_file, '\n'))

# Concatenate the filename structure with the date variables for the normals mean layer
normalmean_file <-paste('us_ssmv11034_SWE_mean_DOWY', dowy, '_WYs2005-2016.nc', sep='')
cat(paste('\n\nReading the Normal Layer: ', normalmean_file, '\n'))

# Read the Normals Mean layer as a R raster, with a little bit of error handling
tryCatch({
    meanSWE <- raster(file.path(swe_normals_dir, normalmean_file), varname='Data' )},
    error = function(e){
        stop(paste('Normals SWE Mean Layer:', normalmean_file, 'Not Found!\n'))
})

cat(paste('Finished reading Normals Layer:', normalmean_file, '\n'))

SDLayer_file <- paste('zz_ssmv11036tS__T0001TTNATS', date_YYYYMMDD_str, date_HH, 'HP001.nc', sep='')
cat(paste('\n\nReading SD Layer: ', SDLayer_file, '\n'))

# Read the SD daily layer as a R raster, with a little bit of error handling.
tryCatch({
    SDLayer <- raster(file.path(swe_dir, SDLayer_file))},
    error = function(e){
      stop(paste('SD Layer', SDLayer_file, 'Not Found!\n'))
})

############################################################################################################
#                                          Sanity Check Function                                           #
############################################################################################################
# Data sanity check:  Checking to see if raster received scaling factor or if it was constructed
# from the raw stored values.  If values are floating point, the scaling factor was applied,
# and SWE values are meters of water equivalent, otherwise, if values are integer, the SWE
# values are measuring millimeters of water equivalent.

netCDF_handler <- function(x, x_name){
    # Calculate minimum non-zero value(if minimum is integer, layer is measuring millimeters, if double, then meters
    cat(paste('\nCalculating Raster statistics for', x_name, '\n'))
    x_min <- cellStats(x, 'min')

    # Create NoData if raster object is missing it
    if (x_min < 0){
        cat(paste('\nApplying NoData value:', x_min, 'to: ', x_name, '\n'))
        x <- calc(x, function(x){x[x == x_min] <- NA; return(x)})
    }

    # Determine if raster is measuring meters or millimeters, convert to millimeters if necessary
    if (typeof(x_min) == 'double') {
        cat(paste('\nConverting', x_name, 'from measuring meters to millimeters.\n'))
        x <- calc(x, function(x){x <- x * 1000; return(x)})
       
    }
    
    # Destroy the non-zero rater object

    return(x)
}

##############################################################################################################
#                                Calculate the Departure from Normal Function                                #
##############################################################################################################
# Pass the daily and mean normal layers through the sanity check function
SWEGrid <- netCDF_handler(SWELayer, SWELayer_file)
normalsGrid <- netCDF_handler(meanSWE, normalmean_file)
SDGrid <- netCDF_handler(SDLayer, SDLayer_file)

# Round the SWE Grid to integers (nearest mm)
storage.mode(SWEGrid[]) = 'integer'
storage.mode(normalsGrid[]) = 'integer'

# Normals and SWE Daily have slightly different CRS that cause R to fail when comparing them.
# Reproject SWE Daily to the Normals layer CRS
normals_crs <- crs(normalsGrid)
crs(SWEGrid) <- normals_crs

# Normals Grid is slightly different than the Daily Grid.  Here we resample the daily to match the normals
x <- Sys.time()
cat('\n\nResampling the Daily Grid to the Normals Grid.\nThis make take a while.\n')
SWEGrid <- resample(SWEGrid, normalsGrid, resample='bilinear')
cat(paste('\n\nResampling took: ', round(Sys.time()-x, 2), ' seconds\n\n', sep=''))

# Stack the Normal and Daily Values
grids <- stack(SWEGrid, normalsGrid)

# Function to calculate difference and apply pseudo-NA values
diff_function <- function(x,y){
    ifelse( is.na(x) & is.na(y), NA, 
    ifelse( x == 0 & y == 0, -49999, (x-y)/25.4))}

cat('Calculating the difference between the daily and normals grid.\n')
SWE_diff <- overlay(grids, fun=diff_function)


###############################################################################################################
#                                 Calculate the percent of departure from mean                                #
###############################################################################################################
# Set threshold variable (in mm of SWE)
dThreshold <- 5
nThreshold <- 5

# Where both normal and daily amount are at or below their established thresholds, set to -499999
# Wherever the daily amount or the normal is > threshold just do the math, with the caveat that the %
# normal is set to 99999 if the normal is zero.

cat('Calculating the percent difference between daily and normals values.\n')

# Function to calculate the percent of normal and apply pseudo-NA Values
percent_normal <- function(x,y){
    ifelse(is.na(x) & is.na(y), NA,
    ifelse(x < dThreshold & y < nThreshold, -49999,
    ifelse(x > dThreshold & y == 0, 99999,
    100 * x/y)))}
    
SWE_percent_normal <- overlay(grids, fun=percent_normal)


#################################################################################################################
#                                  Calculate the HUC8 Percent Normal of SWE                                     #
#################################################################################################################
source('huc8Analysis.r')


#################################################################################################################
#                                               Export the Tiffs                                                 #
##################################################################################################################
#writeRaster(SWE_diff, paste('/net/home/scarter/Departures/SNODAS_SWE_diff_from_normal_', date_YYYYMMDD_str, '.tif', sep=''), format='GTiff', overwrite=T)

#writeRaster(SWE_percent_normal, paste('/net/home/scarter/Departures/SNODAS_SWE_percent_normal_', date_YYYYMMDD_str, '.tif', sep=''), format='GTiff', overwrite=T)



#################################################################################################################
#                                   Diff From Normals Map                                                       #
#################################################################################################################
source('makePNGMap.r')
source('ColorRamps.r')
cat('Writing the Difference from Normals map.\n')
makeMap(
    paste('/net/home/scarter/Departures/SNODAS_SWE_diff_from_normal_', date_YYYYMMDD_str, '.png', sep=''),
    SWE_diff,
    breaks_diff_SWE,
    colors_diff_SWE,
    labels_diff_SWE,
    'Inches of Snow Water Equivalent',
    paste('SNODAS SWE, Difference from', water_year - 104, '-year Mean,', date_YYYYMMDD),
    'No'
    )
#################################################################################################################
#                                    Percent of Normal Map                                                      #
################################################################################################################
cat('Writing the Percent of Normals map.\n')
makeMap(paste('/net/home/scarter/Departures/SNODAS_SWE_percent_normal_', date_YYYYMMDD_str, '.png', sep=''),
    SWE_percent_normal,
    breaks_percent_SWE,
    colors_percent_SWE,
    labels_percent_SWE,
    'Percent of Mean SWE',
    paste('SNODAS SWE, Percent of ', water_year - 104, '-Year Mean,', date_YYYYMMDD),
    'No'
    )

makeMap(paste('/net/home/scarter/Departures/SNODAS_SWE_percent_normal_HUC8_', date_YYYYMMDD_str, '.png', sep=''),
    HUC8_percent_SWE,
    breaks_percent_SWE,
    colors_percent_SWE,
    labels_percent_SWE,
    'Percent of Mean SWE',
    paste('SNODAS SWE, Percent of ', water_year - 104, '-Year Mean (by 8-digit HUC)', date_YYYYMMDD),
    'Yes'
    )
####################################################################################################################
#                                       Daily SWE Map                                                              #
####################################################################################################################
cat('Writing the Daily SWE Map.\n')
makeMap(paste('/net/home/scarter/Departures/SNODAS_SWE_', date_YYYYMMDD_str, '.png', sep=''),
    SWEGrid,
    breaks_SWE,
    colors_SWE,
    labels_SWE,
    'Millimeters',
    paste('SNODAS SWE, Millimeters of Snow Water Equivalent,', date_YYYYMMDD_str),
    'No'
    )
    
####################################################################################################################
#                                       Daily Normals SWE Map                                                      #
####################################################################################################################
cat('Writing the Daily Normal SWE Map.\n')
makeMap(paste('/net/home/scarter/Departures/SNODAS_SWE_normal_', date_YYYYMMDD_str, '.png', sep=''),
        normalsGrid,
        breaks_SWE,
        colors_SWE,
        labels_SWE,
        'Millimeters',
        paste('SNODAS SWE,', water_year - 104, 'Year Mean, Millimeters of Snow Water Equivalent,', date_YYYYMMDD_str),
        'No')


####################################################################################################################
#                                     SD map                                                              #
####################################################################################################################
cat('Writing the Daily Normal Snow Depth Map.\n')
makeMap(paste('/net/home/scarter/Departures/SNODAS_SD_normal_', date_YYYYMMDD_str, '.png', sep=''),
        SDGrid,
        breaks_SD,
        colors_SD,
        labels_SD,
        'Millimeters',
        paste('SNODAS Snow Depth,', water_year - 104, 'Year Mean, Millimeters, ', date_YYYYMMDD_str),
        'No')

cat(paste('\n\n\nCompleted program in :', round(Sys.time()-startTime, 2), ' minutes.\n', sep=''))
