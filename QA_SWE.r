library(RPostgreSQL)
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname="web_data", user="guest", password="guest",
                 host="192.46.108.8", port=5432)

# Get a list of sites from a command line argument
siteIDs <-c("LUKO3")

# Switch device to convert the script between snow depth and snow water equivalent based on available data
snow_type <- c('Snow Depth', 'SWE')

# From the number of sites we are selecting, create a grid to which the plots will be appended
number_of_graphs <- length(siteIDs)

number_of_cols   <- ifelse(number_of_graphs > 1, 2, 1)
number_of_rows   <- ifelse(number_of_graphs > 2, ceiling(number_of_graphs/2), 1)

par(mfrow=c(number_of_rows, number_of_cols))

# Retrieve SWE/SD values from database for each SiteID

### This command makes the point database schema is the active schema
dbSendStatement(con, "set search_path to point;")
dbClearResult(dbListResults(con)[[1]])

currentDate <- as.Date(Sys.Date())
startDate   <- as.Date(Sys.Date()-14)
raster_type <- '_sm_swe'

for(i in 1:length(siteIDs)){
  get_OBS_SWE <- dbSendQuery(con, paste("select s.station_id as station_id, o.value as swe, o.date as date from allstation as s, obs_swe as o where ",
                                   " o.obj_identifier in (select obj_identifier from allstation where station_id = '",
                                   siteIDs[i],
                                   "') and o.obj_identifier = s.obj_identifier and date > '", startDate, "';", sep=''))
  assign(siteIDs[i], dbFetch(get_OBS_SWE))
  x <- 2
  raster_type <- '_sm_swe'
  dbClearResult(get_OBS_SWE)
  
  if (nrow(get(siteIDs[i]))==0){
    
    get_OBS_SWE <- dbSendQuery(con, paste("select s.station_id as station_id, o.value as swe, o.date as date from allstation as s, obs_snow_depth as o where ",
                                          " o.obj_identifier in (select obj_identifier from allstation where station_id = '",
                                          siteIDs[i],
                                          "') and o.obj_identifier = s.obj_identifier and date > '", startDate, "';", sep=''))
    
    assign(siteIDs[i], dbFetch(get_OBS_SWE))
    raster_type <- '_sm_snow_thickness'
    x <- 1
    dbClearResult(get_OBS_SWE)
  }
  
   
  get_MD_SWE <- dbSendQuery(con, paste("select s.station_id station_id, o.value", raster_type, " as swe, o.date as date from allstation as s, rasters_sm as o where ",
                                       "o.obj_identifier in (select obj_identifier from allstation where station_id = '",
                                       siteIDs[i],
                                       "') and o.obj_identifier = s.obj_identifier and date >'", startDate, "';", sep=''))
  
  assign(paste('modeled', siteIDs[i], sep='_'), dbFetch(get_MD_SWE))
  dbClearResult(get_MD_SWE)

}

dbDisconnect(con)

# Controlling the plots

for (i in 1:length(siteIDs)){
  x_max <- max(c(max(get(siteIDs[i])$swe, na.rm=T), max(get(paste('modeled', siteIDs[i], sep='_'))$swe, na.rm=T)) )
  plot(get(siteIDs[i])$date, get(siteIDs[i])$swe, xlab='Date', ylab=paste('Meters of', snow_type[x]), main=paste('Site:', siteIDs[i]), col='blue', pch = 6, ylim = c(0, x_max))
  lines(get(paste('modeled', siteIDs[i], sep='_'))$date, get(paste('modeled', siteIDs[i], sep='_'))$swe, xlab='Date', ylab=paste('Meters of', snow_type[x]), main=paste('Site:', siteIDs[i]), col='red', lwd=0.6, type='h')

}


