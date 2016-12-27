# This function calculates the day number of the water year (DOWY).  Input to the function
# must be in the as.POSIXlt date format

get_dowy <- function(inputDate){
    if (class(inputDate)[1] == 'POSIXlt') {
        if (inputDate$mo >= 9 & inputDate$mo <=11){
            start_of_water_year <- as.POSIXlt(paste(inputDate$year + 1900, '-10-01', sep=''))
            } else {start_of_water_year <- as.POSIXlt(paste(inputDate$year - 1 + 1900, '-10-01', sep=''))}
            } else {stop(paste('Input Date:', inputDate, 'is not in the proper date-time format!\n\n'))}

    dowy <- (inputDate$yday - start_of_water_year$yday) + 1
    
    
    if(dowy<100){dowy <- paste('0', dowy, sep='')}
    
    
}

getStartYear <- function(inputDate){
    if (class(inputDate) == 'POSIXlt'){
      if (inputDate$mo >= 9 & inputDate$mo <=11){
        start_of_water_year <- inputDate$year
      } else {start_of_water_year <- inputDate$year -1 }
    }
  
}