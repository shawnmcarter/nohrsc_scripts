library(raster)
library(rgdal)

main_dir <- '/net/home/scarter/NLDAS_SM'
GIS_dir  <- '/net/home/scarter/GIS_Files'

# Change the text file for new mission sets
flights  <- read.csv(file.path(main_dir, 'SM_data_RRB_161013_NLDAS_CMP.txt'), sep='\t', head=T, stringsAsFactors=F)

dates    <- unique(flights$DATE)

for (i in 1:length(dates)){
    selected_flights <- flights[ which(flights$DATE == dates[i]), ]
    date <- paste('20', dates[i], sep='')

    if (! dir.exists(file.path(main_dir, date))){
        print(paste('Warning: ', main_dir, '/', date, ' Does not exist!!!', sep=''))
    } 
    # Change the Working Directory
    
    setwd(file.path(main_dir, date))
    print(paste('Switching to ', getwd(), ' directory.', sep=''))
    # Read Rasters
    mosaic <- raster(paste('mosaic_SM_', date, '.tif', sep=''))
    noah   <- raster(paste('noah_SM_', date, '.tif', sep=''))
    sac    <- raster(paste('sac_SM_', date, '.tif', sep=''))
    vic    <- raster(paste('vic_SM_', date, '.tif', sep=''))
    
    brick  <- brick(mosaic, noah, sac, vic)

    # Read Master Flights Shapefile
    points <- readOGR(dsn=GIS_dir, layer='gamma_missions')

    # Create New Fields
    points$mosaic_SM <- ''
    points$noah_SM   <- ''
    points$sac_SM    <- ''
    points$vic_SM    <- ''
    points$gamma_SM  <- ''
    points$D_mosaic  <- ''
    points$D_noah    <- ''
    points$D_sac     <- ''
    points$D_vic     <- ''
    
    # Empty vector that will hold mission names
    missions         <- c()

    # Iterate through each mission for this date
    for (j in 1:nrow(selected_flights)){
        mission_name <- selected_flights$STATION_ID[j]
        gamma_SM     <- selected_flights$SM[j]
        missions[j]  <- mission_name

        # Get the center coordinates of the mission track
        XY <- coordinates(points[ which(points$name == mission_name), ])
        print(paste('Mission: ', mission_name, ' located at: ', XY, sep=''))
        
        # Extract the Soil Moisture Values from the raster brick at the coordinate location
        soil_moisture <- extract(brick, XY)

        # Apply Soil Moisture Values to Shapefile Attributes
        points$mosaic_SM[ which(points$name == mission_name)]  <- soil_moisture[1]
        points$noah_SM[ which(points$name == mission_name)]    <- soil_moisture[2]
        points$sac_SM[ which(points$name == mission_name)]     <- soil_moisture[3]
        points$vic_SM[ which(points$name == mission_name)]     <- soil_moisture[4]

        # Apply Gamma Soil Moisture value to shapefile attributes
        points$gamma_SM[ which(points$name == mission_name)]   <- gamma_SM

        # Calcuate delta between gamma and modeled soil moisture
        points$D_mosaic[ which(points$name == mission_name)]   <- gamma_SM - soil_moisture[1]
        print(paste('Delta between Gamma Observed and Mosaic Modeled: ', gamma_SM - soil_moisture[1]))
 
        points$D_noah[ which(points$name == mission_name)]     <- gamma_SM - soil_moisture[2]
        print(paste('Delta between Gamma Observed and Noah Modeled: ', gamma_SM - soil_moisture[2]))

        points$D_sac[ which(points$name == mission_name)]      <- gamma_SM - soil_moisture[3]
        print(paste('Delta between Gamma Observed and SAC Modeled: ', gamma_SM - soil_moisture[3]))

        points$D_vic[ which(points$name == mission_name)]      <- gamma_SM - soil_moisture[4]
        print(paste('Delta between Gamma Observed and VIC Modeled: ', gamma_SM - soil_moisture[4]))

        }
    #Write the results to a shapefile
    print(paste('Writing Shapefile: ', getwd(), 'SM_Deltas_', date, '.shp', sep=''))
    points_subset <- subset(points, name %in% missions)
    writeOGR(points_subset, dsn='.', layer=paste('SM_Deltas_', date, sep=''), overwrite_layer=T, driver='ESRI Shapefile') 
}
