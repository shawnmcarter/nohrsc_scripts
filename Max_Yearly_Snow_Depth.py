from qgis.core import *
from qgis.utils import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import processing as pro 
import os, csv 
from osgeo import gdal, osr
import urllib, tarfile, gzip, glob
import numpy as np 
from datetime import datetime, timedelta

# Set up Folders
Save_to_Folder = 'C:/Users/shawn.carter/Desktop'
folder_name = 'snodas'

if not os.path.exists(os.path.join(Save_to_Folder, folder_name)):
    os.mkdir(os.path.join(Save_to_Folder, folder_name))

if not os.path.exists(os.path.join(Save_to_Folder, folder_name, 'nudging_layers')):
    os.mkdir(os.path.join(Save_to_Folder, folder_name, 'nudging_layers'))
    
os.chdir(os.path.join(Save_to_Folder, folder_name))
gis_files = 'C:/Users/shawn.carter/.qgis2/processing/scripts/gis_files'

# Download the SNODAS Model Results
def get_rasters(date):
    """Downloads SNODAS data from NSIDC and converts data to formatted GeoTIFF"""
    year = date[0:4]
    mn = date[4:6]
    month = {"01":"01_Jan", "02":"02_Feb", "03":"03_Mar", "04":"04_Apr", "05":"05_May","06":"06_Jun",
             "07":"07_Jul", "08":"08_Aug", "09":"09_Sep", "10":"10_Oct", "11":"11_Nov","12":"12_Dec"}

    url = "ftp://sidads.colorado.edu/DATASETS/NOAA/G02158/unmasked/%s/%s/SNODAS_unmasked_%s.tar" % (year, month[mn], date)
    file_name = url.split('/')[-1:][0]

    print("Downloading %s" % file_name)
    urllib.urlretrieve(url, file_name)

    # Decompress the Tar, unzip the SWE Layers
    print("Decompressing %s" % file_name)
    tar = tarfile.open(file_name)
    tar.extractall()
    tar.close()
    
    
    for f in glob.glob("zz_ssmv11036tS*%s*" % date):
        inF = gzip.GzipFile(f, 'rb')
        inF_contents = inF.read()
        outF = open(f[:-3], 'wb')
        outF.write(inF_contents)
        inF.close()
        os.remove(f)
        outF.close()
    
    # Dictionary of data units to scale the output tiffs
    data_units = {}

    # Rename dat files to bil files
    for f in glob.glob('zz_ssmv11036tS*%s*.dat' % date):
        old_dat = f[:-3] + 'dat'
        new_dat = f[:-3] + 'bil'
        os.rename(old_dat, new_dat)

    for f in glob.glob('zz_ssmv11036tS*%s*.Hdr' % date):
        hdr_values = {}
        new_hdr = f[:-3] + 'hdr'
        root_name = f[:-4]
        old_header = open(f, 'rb')
        
        for row in old_header:
            hdr_values[row.split(':')[0]] = row.split(':')[1].rstrip('\n').strip()
        data_units[root_name] = hdr_values['Data units']
        if data_units[root_name] == 'Kelvins':
            data_units[root_name] = 'Kelvins / 1'
        old_header.close()
        hdr_contents = {"1":"byteorder M", "2":"layout bil", "3":"nbands 1", "4":"nbits 16",
                        "5":"ncols %s" % hdr_values['Number of columns'],
                        "6":"nrows %s" % hdr_values['Number of rows'],
                        "7":"ulxmap %s" % hdr_values['Benchmark x-axis coordinate'],
                        "8":"ulymap %s" % hdr_values['Benchmark y-axis coordinate'],
                        "9":"xdim %s" % hdr_values['X-axis resolution'],
                        "10":"ydim %s" % hdr_values['Y-axis resolution']}
        os.remove(f)
        with open(new_hdr, 'wb') as outF:
            for i in range(1, len(hdr_contents)+1):
                outF.write(hdr_contents[str(i)] + '\n')
    
    
        

    for f in glob.glob('zz_ssmv11036tS*%s*.bil' % date):
        # Dictionary by which to rename the rasters to something meaningful
        output_names = {'zz_ssmv11036tS__T0001TTNATS%s05HP001' % date: 'SNODAS_Snow_Depth_%s.tif' % date}

        root_name = f[:-4]

        # Convert the bil rasters to geoTIFF, assign NoData Values and Scale Appropriately
        ds = gdal.Open(f)
        band = ds.GetRasterBand(1)

        # Convert the raster to a numpy array
        array = band.ReadAsArray()
        #array = array.astype(float)

        # Assign the NoData value to the Array - commented out to reduce array memory size
        #array[array==55537] = np.nan 

        # Scale the array - commented out to reduce array memory size
        #array = array / float(data_units[root_name].split('/')[1])

        # Write the array to a new geoTIFF file
        driver = gdal.GetDriverByName('GTiff')
        dst_ds = driver.Create(output_names[root_name],
            ds.RasterXSize,
            ds.RasterYSize,
            1,
            gdal.GDT_Int32)
        outband = dst_ds.GetRasterBand(1)
        outband.WriteArray(array, 0, 0)
        outband.FlushCache()
        proj = osr.SpatialReference()
        proj.SetWellKnownGeogCS("EPSG:4326")
        dst_ds.SetGeoTransform(ds.GetGeoTransform())
        dst_ds.SetProjection(proj.ExportToWkt())
        
        del array
        ds = None
        
    # Delete unneccessary files 
    del_ext = ['.bil', '.hdr', '.gz', '.tar']
    for i in os.listdir(os.getcwd()):
        if i.endswith(tuple(del_ext)):
            os.remove(i)
    

def write_raster(ds, max_array):
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create('Maximum_Snow_Depth_WY_2017.tif',
        ds.RasterXSize,
        ds.RasterYSize,
        1,
        gdal.GDT_Int32)
    outband = dst_ds.GetRasterBand(1)
    outband.WriteArray(max_array, 0, 0)
    outband.FlushCache()
    proj = osr.SpatialReference()
    proj.SetWellKnownGeogCS("EPSG:4326")
    dst_ds.SetGeoTransform(ds.GetGeoTransform())
    dst_ds.SetProjection(proj.ExportToWkt())

# Meat of the tool, this is what we're here to do
def calculate_max_depth(raster_a, raster_b):
    """Return a numpy array of element wise maxima between two numpy arrays read from geotiffs"""
    if isinstance(raster_a, gdal.Dataset):
        array_a = raster_a.ReadAsArray()
    elif isinstance(raster_a, np.ndarray):
        array_a = raster_a 
    array_b = raster_b.ReadAsArray()
    max_array = np.maximum(array_a, array_b)

    return max_array

def readTiff(date):
    """Open a geotiff as a gdal dataset"""
    ds = gdal.Open('SNODAS_Snow_Depth_%s.tif' % date)
    return ds

def calculateDate(days_since_sowy):
    """Return a string representing the date to retrieve model results"""
    start_date = datetime(2016,10,01,00,00)
    new_day = start_date + timedelta(days = days_since_sowy)
    if new_day.month < 10:
        month = '0' + str(new_day.month)
    else:
        month = new_day.month
    if new_day.day < 10:
        day = '0' + str(new_day.day)
    else:
        day = new_day.day

    date = '%s%s%s' % (new_day.year, month, day)
    return date 
    
def main():
    x = 0
    date_a = calculateDate(x)
    date_b = calculateDate(x+1)

    [get_rasters(i) for i in [date_a, date_b]]
    ds_a = readTiff(date_a)
    ds_b = readTiff(date_b)

    max_depth = calculate_max_depth(ds_a, ds_b)

    x += 2
    for i in range(0, 273):
        date_b = calculateDate(x+i)
        get_rasters(date_b)
        ds_b = readTiff(date_b)
        max_depth = calculate_max_depth(max_depth, ds_b)
        ds_b = None 
        os.remove('SNODAS_Snow_Depth_%s.tif' % date_b)

    write_raster(ds_a, max_depth)
    ds_a = None
    
        


