library(raster)
library(rgdal)

HUC8_dir      <- '/operations/gisrs/data/common/raster/'
HUC8_filename <- 'HUCs_8_US.tif'

cat('Reading HUC Raster\n')
HUC8_raster   <- raster(file.path(HUC8_dir, HUC8_filename))
HUC8_raster   <- crop(HUC8_raster, SWE_percent_normal)
HUC8_raster[HUC8_raster==0] <- NA
poly_percent_normal <- function(x,y){
  ifelse(y < nThreshold & x < dThreshold, -49999,
  ifelse(y == 0 & x > dThreshold, 99999,100*x/y ))
}

cat('Calculating Zonal mean on Daily Data\n')
SWE_daily_HUC <- zonal(SWEGrid, HUC8_raster, mean, digits=8)

cat('Calculating Zonal mean on Normals Data\n')
SWE_normal_HUC <-zonal(normalsGrid, HUC8_raster, mean, digits=8)

cat('Reclassifying HUC to zonal results\n')
SWE_daily_HUC <- reclassify(HUC8_raster, SWE_daily_HUC)
SWE_normal_HUC <- reclassify(HUC8_raster, SWE_normal_HUC)

cat('Calculating Departure from Mean\n')
grids <- stack(SWE_daily_HUC, SWE_normal_HUC)


HUC8_percent_SWE <- overlay(grids, fun=poly_percent_normal)
