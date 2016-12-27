Water_Year <- seq(1,364)
swe_normals <- data.frame()
swe_min <- data.frame()
swe_max <- data.frame()

for (i in Water_Year){
  DOWY <- i
  if (DOWY < 10){DOWY = paste('00', DOWY, sep='')
  } else if (DOWY > 9 & DOWY < 100){DOWY = paste('0', DOWY, sep='')
  } else {DOWY <- DOWY}
  
  colname_list <- c(paste('DOWY', DOWY, '_mean_obs_swe', sep=''),
                    paste('DOWY', DOWY, '_min_obs_swe', sep=''),
                    paste('DOWY', DOWY, '_max_obs_swe', sep=''),
                    'Station_ID', 
                    paste('DOWY', DOWY, '_number_of_observations'))
  
  x <- readLines(paste('DOWY', DOWY, '_all.txt', sep=''))
  x <- x[-2]
  y <- read.csv(textConnection(x), header=T, stringsAsFactors = T, sep = '|', nrows=length(x)-3)
  y <- data.frame(y)
  colnames(y) <- colname_list
  
  x0 <- data.frame(y[['Station_ID']], y[[paste('DOWY', DOWY, '_mean_obs_swe', sep='')]])
  x1 <- data.frame(y[['Station_ID']], y[[paste('DOWY', DOWY, '_min_obs_swe', sep='')]])
  x2 <- data.frame(y[['Station_ID']], y[[paste('DOWY', DOWY, '_max_obs_swe', sep='')]])
  
  colnames(x0) <- c(colname_list[4], colname_list[1])
  colnames(x1) <- c(colname_list[4], colname_list[2])
  colnames(x2) <- c(colname_list[4], colname_list[3])
  
  if (i == 1){ swe_normals <- rbind(swe_normals, x0)
  swe_min <- rbind(swe_min, x1)
  swe_max <- rbind(swe_max, x2)
  } else { swe_normals <- merge(swe_normals, x0, by='Station_ID')
           swe_min <- merge(swe_min, x1, by='Station_ID')
           swe_max <- merge(swe_max, x2, by='Station_ID')}
  
}
