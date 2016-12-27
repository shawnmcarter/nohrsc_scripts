library(RPostgreSQL)
ptm <- proc.time()

# PostgreSQL Database connection parameters
drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname="web_data", user="guest", password="guest",
                 host="192.46.108.8", port=5432)

# Edit this field to create the graph of the site you want
siteName <- 'CORM1'

# Empty data frames
swe_data <- data.frame()
swe_md_data <- data.frame()

# Switch device to convert the script between snow depth and snow water equivalent based on available data
snow_type <- c('Snow Depth', 'SWE')

# This command makes the point database schema is the active schema
dbSendStatement(con, "set search_path to point;")
dbClearResult(dbListResults(con)[[1]])

# Select the Current Water Year SWE Values.  If 0 rows are returned, tool will shift to Snow Depth Mode

get_Current_SWE <- dbSendQuery(con, paste("select avg(value) as value, date_trunc('day', date) as date from obs_swe where obj_identifier in (select obj_identifier from allstation where station_id ='", siteName, "') and date > '2016-10-01' group by date_trunc('day', date) order by date_trunc('day', date)", sep=''))
current_swe <- dbFetch(get_Current_SWE)
dbClearResult(get_Current_SWE)

# Configure the switch
if (nrow(current_swe)==0){
    x <- 1
    get_Current_SWE <- dbSendQuery(con, paste("select avg(value) as value, date_trunc('day', date) as date from obs_snow_depth where obj_identifier in (select obj_identifier from allstation where station_id ='", siteName, "') and date > '2016-10-01' group by date_trunc('day', date) order by date_trunc('day', date)", sep=''))

    current_swe <- dbFetch(get_Current_SWE)
    dbClearResult(get_Current_SWE)
    } else { x <- 2}

# Function to select the data from the postgre sql database
if (x==1){
    md_type <- 'snow_thickness'
    ob_type <- 'snow_depth'
} else {
     md_type <- 'swe'
     ob_type <- 'swe'}

data_query <- dbSendQuery(con, paste("SELECT avg(o.value) as obs_mean, 
                                             min(o.value) as obs_min,  
                                             max(o.value) as obs_max,
                                             extract('month' from o.date) as month,
                                             extract('day' from o.date) as day
                                      FROM  obs_", ob_type, " as o 
                                      WHERE o.obj_identifier in (SELECT obj_identifier from allstation where station_id = '", siteName, "') 
                                      GROUP BY month, day
                                      ORDER BY month, day;", sep=''))

snow_data <- dbFetch(data_query)
dbClearResult(data_query)
data_query1 <- dbSendQuery(con, paste("SELECT avg(o.value_sm_", md_type, ") as obs_mean, 
                                              min(o.value_sm_", md_type, ") as obs_min,  
                                              max(o.value_sm_", md_type, ") as obs_max,
                                              extract('month' from o.date) as month,
                                              extract('day' from o.date) as day
                                       FROM  rasters_sm  as o 
                                       WHERE o.obj_identifier in (SELECT obj_identifier from allstation where station_id = '", siteName, "') 
                                       GROUP BY month, day
                                       ORDER BY month, day;", sep=''))
model_data <- dbFetch(data_query1)
dbClearResult(data_query1)

snow_data[['date']] <- ifelse(snow_data[['month']] > 9, paste('2016', snow_data$month, snow_data$day, sep='-'), paste('2017', snow_data$month, snow_data$day, sep='-'))

model_data[['date']] <- ifelse(model_data[['month']] > 9, paste('2016', model_data$month, model_data$day, sep='-'), paste('2017', model_data$month, model_data$day, sep='-'))



snow_data <- snow_data[order(as.Date(snow_data$date, format='%Y-%m-%d')), ]
model_data <- model_data[order(as.Date(model_data$date, format='%Y-%m-%d')),]

#Plotting Commands
y_label <- ifelse(x == 1, 'Centimeters of Snow Depth', 'Centimeters of Snow Water Equivalent')
max_y <- max(c(max(snow_data$obs_max, na.rm=T), max(model_data$obs_max, na.rm=T)))*100
plot(as.Date(snow_data$date, format='%Y-%m-%d'), as.numeric(snow_data$obs_max), type='l', col='red', 
            main=paste(snow_type[x], "Profile for Observation Station:", siteName), 
            xlab='Date', ylab=y_label, ylim=c(0, max_y))

  lines(as.Date(model_data$date, format='%Y-%m-%d'), as.numeric(model_data$obs_max)*100, type='h', col='firebrick4', lwd=0.5)
  lines(as.Date(model_data$date, format='%Y-%m-%d'), as.numeric(model_data$obs_mean)*100, type='h', col='darkgrey', lwd=0.95)  
  lines(as.Date(model_data$date, format='%Y-%m-%d'), as.numeric(model_data$obs_min)*100,type='h', col='cadetblue1', lwd=1)  
  lines(as.Date(snow_data$date, format='%Y-%m-%d'), as.numeric(snow_data$obs_max)*100, type='l', col='red')
  lines(as.Date(snow_data$date, format='%Y-%m-%d'), as.numeric(snow_data$obs_mean)*100, type='l', col='black')
  lines(as.Date(snow_data$date, format='%Y-%m-%d'), as.numeric(snow_data$obs_min)*100, type='l', col='blue')
  lines(as.Date(current_swe$date), current_swe$value*100, type='l', col='slateblue4', lwd=5)
  legend('topright', xpd=T,bty='n', legend=c('Maximum SWE', 'Mean SWE', 'Minimum SWE', 'Current Year Observed SWE'), col=c('red', 'black', 'blue', 'slateblue4'), lty=1:1, lwd=c(1,1,1,5), cex=0.75)
#
## Just a timing function to see how long this thing takes.
cat(proc.time() - ptm)

dbDisconnect(con)
