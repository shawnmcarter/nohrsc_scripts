from osgeo import ogr
import os, urllib, time
import numpy as np
from netCDF4 import Dataset
import gzip, sys
#### Read the point data shapefile

#### File Admin
start_date = sys.argv[1]
end_date = sys.argv[2]

print(start_date,end_date)
point_shape = 'nwm_md_based_%s_%s.shp' % (start_date, end_date)
GIS_Folder = '/net/home/scarter/SNODAS_Development/results/'
shp = os.path.join(GIS_Folder, point_shape)
metadata_loc = '/net/home/scarter/SNODAS_Development/scripts/NWM_nc_tools_v1.1/CONUS_IOC_Spatial_Metadata_Files/WRF_Hydro_NWM_v1.1_geospatial_data_template_land_GIS.nc'

### Get the spatial index
spatialData = Dataset(metadata_loc, 'r')
lats = spatialData.variables['y'][:]
lons = spatialData.variables['x'][:]
lats = lats[::-1]

NWM_Folder = '/net/home/scarter/SNODAS_Development/results/NWM_Deltas/'
if not os.path.exists(NWM_Folder):
    os.mkdir(NWM_Folder)

### Create the new NWM Delta Field
fldDefn = ogr.FieldDefn('D_NWM_SWE', ogr.OFTReal)
fldDefn.SetWidth(250)
fldDefn.SetPrecision(8)
driver = ogr.GetDriverByName("ESRI Shapefile")
print(shp)
dataSource = driver.Open(shp, 1)
layer = dataSource.GetLayer()
layer.CreateField(fldDefn)

### Dictionary for editing the shapefile
shp_edit = {}

### Get observation times from point delta file
observationTimes = []
for feature in layer:
    obs_time = feature.GetField('OB_SWE_T')
    if obs_time not in observationTimes:
        observationTimes.append(obs_time)

### Spatial Index of the NWM Land netCDF
def geo_idx(dd, dd_array):
        geo_idx = (np.abs(dd_array - dd)).argmin()
        return geo_idx


#### Retrieve NWM netCDFs from the NCEP Server
for obs in observationTimes:
    ### Reset the Layer Iterator
    dataSource = driver.Open(shp, 0)
    layer = dataSource.GetLayer()
    start = time.time()
    NWM_Date = obs[:-2].replace('-', '').rstrip()
    NWM_Hour = obs[-2:]
    NWM_Daily_Folder = os.path.join(NWM_Folder, NWM_Date)
    if not os.path.exists(NWM_Daily_Folder):
        os.mkdir(NWM_Daily_Folder)
    
    ### Create the FTP string
    NWM_FTP = 'ftp://ftpprd.ncep.noaa.gov/pub/data/nccf/com/nwm/prod/nwm.%s/analysis_assim/' % NWM_Date
    NWM_File = 'nwm.t%sz.analysis_assim.land.tm00.conus.nc.gz' % NWM_Hour
    url = str(NWM_FTP + NWM_File)
    
    ### Download the NWM File
    urllib.urlretrieve(url, os.path.join(NWM_Daily_Folder, NWM_File))
    print('Downloaded %s in {0:0.1f} seconds.'.format(time.time() - start) % NWM_File)
    
    ### Unzip netCDF
    gz_NC = gzip.open(os.path.join(NWM_Daily_Folder, NWM_File), 'rb')
    NC = open(os.path.join(NWM_Daily_Folder, NWM_File[:-3]), 'wb')
    NC.write( gz_NC.read())
    gz_NC.close()
    NC.close()
    
    ### Load the NWM SWE Values into a numpy array
    inFile = Dataset(os.path.join(NWM_Daily_Folder, NWM_File[:-3]), 'r')
    SNEQV = inFile.variables['SNEQV'][:]
    
    ## Iterate through selected features
    
    for feature in layer:
        if feature.GetField('OB_SWE_T') == obs:        
            geom = feature.GetGeometryRef()
            x = geo_idx(geom.GetX(), lons) # Get the spatial index from the spatial metadata for point longitude
            y = geo_idx(geom.GetY(), lats) # Get the spatial index from the spatial metadata for point latitude
            
            ## Read SWE value at point location
            M_SWE = float(SNEQV[0][y][x])
            OB_SWE = feature.GetField('OB_SWE')
            STATION_ID = feature.GetField('STATION_ID')
            D_NWM_SWE = float(OB_SWE - (M_SWE/1000))  # Value for D_NWM_SWE field.
            
            ## Add values to the shapefile edit dictionary
            shp_edit.update({STATION_ID: D_NWM_SWE})
                
            print(M_SWE/1000, OB_SWE, D_NWM_SWE, feature.GetField('STATION_ID'))
            

## Reset the feature iterator
dataSource = driver.Open(shp, 1)
layer = dataSource.GetLayer()
## Write the new data to the new field
for feature in layer:
    station = feature.GetField('STATION_ID')
    feature.SetField('D_NWM_SWE', shp_edit[station])
    layer.SetFeature(feature)
