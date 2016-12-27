
args <-commandArgs(trailingOnly = T)

swe_max <- readRDS(file='~/SWE_point_normals/swe_max_all.Rda')
swe_min <- readRDS(file='~/SWE_point_normals/swe_min_all.Rda')
swe_normals <- readRDS(file='~/SWE_point_normals/swe_normals_all.Rda')

station_id <- args[2]

if (length(args)==0){
  stop("Script Usage:  $ Rscript ./Swe_Climagraphs.r <Station ID>", call.=FALSE)
}

title <- paste('SWE Normals: Station -', station_id)
x_label <- 'Date'
y_label <- 'Meters of SWE'

x_ticks <- seq(as.Date('2010/10/01'), as.Date('2011/09/29'), by='day')


if (args[1] == 'show'){
  X11()
  plot(as.Date(x_ticks), swe_max[grep(station_id, swe_max$Station_ID, ignore.case = T), 2:ncol(swe_max)], 
     main=title,
     xlab=x_label,
     ylab=y_label,
     type='l',
     col='red')

  lines(as.Date(x_ticks, na.rm=T), swe_min[grep(station_id, swe_min$Station_ID, ignore.case = T), 2:ncol(swe_min)],
      col='blue')

  lines(as.Date(x_ticks), swe_normals[grep(station_id, swe_min$Station_ID, ignore.case = T), 2:ncol(swe_normals)],
      col='black', lty=1)

  legend('topright', legend=c('Maximum SWE', 'Mean SWE', 'Minimum SWE'), 
       col=c('red', 'black', 'blue'),
       lty=1:1)
  cat('Close the plotting window to return.\n')
  while (!is.null(dev.list())) Sys.sleep(1)
} else if (args[2] == 'save'){
  png(paste('~/', station_id, '_swe_normals.png'))
  
  plot(as.Date(x_ticks, na.rm=T), swe_max[grep(station_id, swe_max$Station_ID, ignore.case = T), 2:ncol(swe_max)], 
       main=title,
       xlab=x_label,
       ylab=y_label,
       type='l',
       col='red')
  
  lines(as.Date(x_ticks), swe_min[grep(station_id, swe_min$Station_ID, ignore.case = T), 2:ncol(swe_min)],
        col='blue')
  
  lines(as.Date(x_ticks), swe_normals[grep(station_id, swe_min$Station_ID, ignore.case = T), 2:ncol(swe_normals)],
        col='black', lty=1)
  
  legend('topright', legend=c('Maximum SWE', 'Mean SWE', 'Minimum SWE'), 
         col=c('red', 'black', 'blue'),
         lty=1:1)
  dev.off()
}