##States=string XX
import urllib2, os
import zipfile 
from qgis.core import *
from qgis.utils import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

states = States.split(' ')
if states == 'XX':
    states = ['AL',  'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL',
        'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE',
        'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 
        'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
# Download and unzip the latest Database of Obstructions
if not os.path.exists('C:/Users/shawn.carter/.qgis2/processing/scripts/dof'):
    os.mkdir('C:/Users/shawn.carter/.qgis2/processing/scripts/dof')

os.chdir('C:/Users/shawn.carter/.qgis2/processing/scripts/dof')

dof_server = 'http://www.aeronav.faa.gov/Obst_Data/DAILY_DOF.ZIP'

response = urllib2.urlopen(dof_server)
zipcontent = response.read()
with open(os.path.join(os.getcwd(), 'DAILY_DOF.zip'), 'wb') as f:
    f.write(zipcontent)
zip_ref = zipfile.ZipFile(os.path.join(os.getcwd(), 'DAILY_DOF.zip'))
zip_ref.extractall(os.getcwd())
zip_ref.close()

raw_data = os.path.join(os.getcwd(), 'DOF.DAT')

oas, v, co, st, city, lat_deg, lat_min, lat_sec, lon_deg, lon_min, lon_sec, type, number, agl, amsl, color, h_acc, v_acc, ind, study, action, date = ([] for i in range(22))

x = 0 # Used to count lines in the data file

vertical_accuracy = {'A':"+-3'", 'B':"+-10'", 'C':"+-20'", 'D':"+-50'",
    'E':"+-125'", 'F':"+-250'", 'G':"+-500'", 'H':"+-1000'", 'I':"Unknown"}

horizontal_accuracy = {'1':"+-20'", '2':"+-50'", '3':"+-100'", '4':"+-250'",
    '5':"+-500'", '6':"+-1000'", '7':"+-1/2 NM", '8':"+-1 NM", '9':"Unknown"}

lighting = {'R':'Red', 'D':'Medium intensity White Strobe & Red', 'H':'High intensity White Strobe & Red',
    'M':'Medium Intensity White Strobe', 'S':'High Intensity White Strobe', 'F':'Flood', 
    'C':'Dual Medium Catenary', 'W':'Synchronized Red Lighting', 'L':'Lighted (Type Unknown)',
    'N':'None', 'U':'Unknown'}

marker = {'P':'Orange or Orange and White Paint', 'W':'White Paint Only', 'M':'Marked',
    'F':'Flag Marker', 'S':'Spherical Marker', 'N':'None', 'U':'Unknown'}

with open(raw_data, 'rb') as inFile:
    for i in xrange(4):
        inFile.next()
    for line in inFile:
        oas.append(line[0:9])
        v.append(line[10:11])
        co.append(line[12:14])
        st.append(line[15:17])
        city.append(line[18:35].rstrip())
        lat_deg.append(line[35:37])
        lat_min.append(line[38:40])
        lat_sec.append(line[41:47])
        lon_deg.append(line[48:51])
        lon_min.append(line[52:54])
        lon_sec.append(line[55:61])
        type.append(line[62:81].rstrip())
        number.append(line[81:82])
        agl.append(line[83:88])
        amsl.append(line[89:94])
        color.append(line[95:96])
        h_acc.append(line[97:98])
        v_acc.append(line[99:100])
        ind.append(line[101:102])
        study.append(line[103:117])
        action.append(line[118:119])
        date.append(line[120:127])
        
        x += 1
        
with open(os.path.join(os.getcwd(), 'dof.csv'), 'wb') as outFile:
        outFile.write('OAS|Verification Status|Country|State|City|Latitude|Longitude|Type|Number|AGL|AMSL|Light Color|Horizontal Accuracy|Vertical Accuracy|Marking|FAA Study|Action|JDATE\n')
        for line in range(0, x):
            if len(states) != 0:
                if st[line] in states:
                    latitude = float(lat_deg[line]) + (float(lat_min[line])/60) + (float(lat_sec[line][:-1])/3600)
                    longitude = '-' + str(float(lon_deg[line]) + (float(lon_min[line])/60) + (float(lon_sec[line][:-1])/3600))
                    if v_acc[line] != ' ':
                        v_accuracy = vertical_accuracy[v_acc[line]]
                    else: 
                        v_accuaracy = vertical_accuracy['I']
                    if h_acc[line] != ' ':
                        h_accuracy = horizontal_accuracy[h_acc[line]]
                    else:
                        h_accuracy = horizontal_accuracy['9']
                    
                    if color[line] != ' ':
                        lights = lighting[color[line]]
                    else:
                        lights = lighting['U']
                    
                    if ind[line] != ' ':
                        marking = marker[ind[line]]
                    else:
                        marking = marker['U']
                    outFile.write('%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % (oas[line], v[line], co[line], st[line], city[line], latitude, longitude, type[line], number[line], agl[line], amsl[line], lights, h_accuracy, v_accuracy, marking, study[line], date[line]))
            else:
                latitude = float(lat_deg[line]) + (float(lat_min[line])/60) + (float(lat_sec[line][:-1])/3600)
                longitude = '-' + str(float(lon_deg[line]) + (float(lon_min[line])/60) + (float(lon_sec[line][:-1])/3600))
                if v_acc[line] != ' ':
                    v_accuracy = vertical_accuracy[v_acc[line]]
                else: 
                    v_accuaracy = vertical_accuracy['I']
                if h_acc[line] != ' ':
                    h_accuracy = horizontal_accuracy[h_acc[line]]
                else:
                    h_accuracy = horizontal_accuracy['9']
                
                if color[line] != ' ':
                    lights = lighting[color[line]]
                else:
                    lights = lighting['U']
                
                if ind[line] != ' ':
                    marking = marker[ind[line]]
                else:
                    marking = marker['U']
                outFile.write('%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % (oas[line], v[line], co[line], st[line], city[line], latitude, longitude, type[line], number[line], agl[line], amsl[line], lights, h_accuracy, v_accuracy, marking, study[line], date[line]))

vlayer_uri = 'file:///' + os.path.join(os.getcwd(), 'dof.csv') + '?type=csv&delimiter=,%7C&xField=Longitude&yField=Latitude&spatialIndex=no&subsetIndex=no&watchFile=no'
vlayer = QgsVectorLayer(vlayer_uri, 'Database of Obstructions', 'delimitedtext')
QgsMapLayerRegistry.instance().addMapLayer(vlayer)
