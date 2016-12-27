library(maptools)
bkgrnd_poly <- readShapePoly('/net/home/scarter/GIS_Files/northAmerica.shp')
newProjection <- "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs"
HUC8_poly   <- readShapePoly('/operations/gisrs/data/common/shapefiles/HUCs_8_digit_Coterminous_US.shp')

makeMap <- function(outPNG, inRaster, inBreaks, inColors, inLabels, legendText, inTitle, HUC){

    # Reproject the data
#    proj4string(bkgrnd_poly) <- newProjection
#    bkgrnd_poly <- spTransform(bkgrnd_poly, CRS("+init=epsg:2163"))

    png(outPNG, heigh=nrow(inRaster)+500, width=ncol(inRaster)+500)

    par(ps=100, cex=1, cex.main=1, bg='gray90')
  
    plot(bkgrnd_poly, xlim=c(-125, -66), ylim=c(24,53), col='gray80')

    plot(inRaster, breaks=inBreaks, col=inColors, add=TRUE, legend=FALSE)

    plot(inRaster, zlim=seq(0, length(inColors)), legend.only=TRUE,
        col=inColors, legend.width=25,
        breaks=seq(0, length(inColors)),
        axis.args = list(at=seq(0, length(inColors)),labels=inLabels, cex.axis=0.65),
        legend.args = list(text=legendText, side=4, font=2, line=20, cex=0.75),
        smallplot = c(0.92, 0.93, 0.25, 0.55))
    
    plot(bkgrnd_poly, col='#00000000', lwd=5, add=TRUE)

    if(HUC == 'Yes'){
      plot(HUC8_poly, add=T, lwd=2)
    } 

    title(main=inTitle, line=-10)

    dev.off()

    # Re-scale image (original is very large)
    mogrify_scale <- 'mogrify -scale 1500x834'
    system(paste(mogrify_scale, ' ', outPNG))

    }
