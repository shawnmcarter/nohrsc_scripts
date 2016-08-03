import os, csv, sys
import osgeo.ogr as ogr
import osgeo.osr as osr
import datetime

today = datetime.datetime.now()

## Get Date for the Gamma Msg
## This script should be run with two command line arguments - 
## First the Date in YYYYMMDD format and the Gamma Flight Mission Number.
## For example:  python gammaShapefile.py 20170215 23

date = str(sys.argv[1])
svy = str(sys.argv[2])

# Change the working directory to where the gamma message is copied to.
os.chdir('/net/home/scarter/SNODAS_Development/temp')

''' This function re-writes the gamma message with a header '''

def makeFormattedGamma(date):
    # List of attribute names for the formatted gamma message.
    header = ['FLINE', 'FDATE', 'FTIME', 'DIR', 'HALT', 'HTEMP', 'CODE', 'PALT',
        'SCP', 'PLANE', 'RACK', 'CRYSTAL', 'REMS', 'WSWE', 'KSWE', 'TSWE', 'GSWE',
        'SWE35', 'WSM', 'MSM' , 'KN', 'TN', 'GCN', 'GCAS', 'GCGS', 'GCDR', 'GCUR',
        'LR', 'KR', 'UR', 'TR', 'CDR', 'CUR', 'KCENT', 'AM', 'ALT', 'PSI', 'TEMP',
        'ALTC', 'PRESC', 'TEMPC', 'ACQTIM', 'LTD', 'LTU', 'ErrorFlg']

    # Find the gamma msg (a bit of a hack because message formatting is airframe dependent
    for i in os.listdir(os.getcwd()):
        if date[2:]+'a' in i:
            gammaMSG = i

    # where the new formatted message will be kept
    newGammaMsg = os.path.join(os.getcwd(), 'formattedGammaMsg.csv')

    with open(newGammaMsg, 'w') as outFile:
        writer = csv.writer(outFile, delimiter = '|')
        writer.writerow(header)
        with open(gammaMSG, 'r') as inFile:
            reader = csv.reader(inFile, delimiter = '|')
            for row in reader:
                writer.writerow(row)
    
    return newGammaMsg, header


''' This function converts the newly formatted gamma message into a shapefile'''

def shapeFileMaker(svy):
    # Shapefile Name
    shp = 'gamma_points_' + date + '_svy' + str(svy) + '.shp'
    fileDir = '/net/home/scarter/SNODAS_Development/results'
    # If a shapefile is present with same name and mission number, delete it:
    if os.path.isfile(os.path.join(fileDir, shp)) == True:
        os.remove(os.path.join(fileDir, shp))

    # Dictionaries to access values
    # where the flight names and location look-up table is maintained

    values, header = makeFormattedGamma(date)

    valuesReader = csv.DictReader(open(values, 'r'), delimiter = '|')

    # store flight names and location look-up table as a dictionary
    points = '/net/home/scarter/SNODAS_Development/scripts/flightLines.csv'
    pointDict = {}
    flinePoints = csv.reader(open(points, 'r'), delimiter =  '|')
    for line in flinePoints:
        key = line[0]
        values = line[1:]
        pointDict[key] = values

    # Set up the shapefile driver
    driver = ogr.GetDriverByName("ESRI Shapefile")

    # create the data source
    data_source = driver.CreateDataSource(os.path.join(fileDir, shp))

    # create the spatial reference, WGS84
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    # create the layer
    layer = data_source.CreateLayer("Gamma Points", srs, ogr.wkbPoint)

    # Define Field Names and Attribute Types
    layer.CreateField(ogr.FieldDefn("FLINE",    ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("FDATE",    ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("FTIME",    ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("DIR",      ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("HALT",     ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("HTEMP",    ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("CODE",     ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("PALT",     ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("SCP",      ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("PLANE",    ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("RACK",     ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("CRYSTAL",  ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("REMS",     ogr.OFTString))
    layer.CreateField(ogr.FieldDefn("WSWE",     ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("KSWE",     ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("TSWE",     ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("GSWE",     ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("SWE35",    ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("WSM",      ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("MSM",      ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("KN",       ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("TN",       ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("GCN",      ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("GCAS",     ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("GCGS",     ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("GCDR",     ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("GCUR",     ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("LR",       ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("KR",       ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("UR",       ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("TR",       ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("CDR",      ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("CUR",      ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("KCENT",    ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("AM",       ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("ALT",      ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("PSI",      ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("TEMP",     ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("ALTC",     ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("PRESC",    ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("TEMPC",    ogr.OFTInteger))
    layer.CreateField(ogr.FieldDefn("ACQTIM",   ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("LTD",      ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("LTU",      ogr.OFTReal))
    layer.CreateField(ogr.FieldDefn("ErrorFlg", ogr.OFTString))

    # Assign values to attributes
    for row in valuesReader:
        # Create the feature
        feature = ogr.Feature(layer.GetLayerDefn())

        # Setting the attributes - this iterates through header and uses the header
        # value as a key in the values dictionary
        for attr in header:
            feature.SetField(attr, row[attr])
            
        # Convert the lat/long into Well Known Text (WKT) format
        
        wkt = "POINT(%f %f)" % \
             (float(pointDict[row['FLINE']][1]), float(pointDict[row['FLINE']][0]))
        
        # Conver the WKT into a point
        point = ogr.CreateGeometryFromWkt(wkt)

        # Set the feature geometry with the point
        feature.SetGeometry(point)

        # Create the feature into hte shapefile
        layer.CreateFeature(feature)

        # Destroy the feature in memory
        feature.Destroy()

    # Destroy the shapefile writer
    data_source.Destroy()        
    
def main():
    shapeFileMaker(svy)
    
main()
