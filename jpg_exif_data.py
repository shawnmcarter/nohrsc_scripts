# -*- coding: utf-8 -*-
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import PIL
from datetime import datetime
import os

def get_exif_data(image):
    """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]

                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value

    return exif_data

def _get_if_exist(data, key):
    if key in data:
        return data[key]

    return None

def _convert_to_degress(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)

def get_lat_lon(exif_data):
    """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
    lat = None
    lon = None

    if "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]

        gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
        gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
        gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
        gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":
                lat = 0 - lat

            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon

    return lat, lon

def image_location(jpg_folder):
    """Returns a dictionary with the image name, time captured,  and it's man/machine readable GPS coordinate"""
    jpg_dict = {}
    for file in os.listdir(jpg_folder):
        if file.lower().endswith('.jpg'):
            jpg = PIL.Image.open(os.path.join(jpg_folder, file))
            jpg_exif = get_exif_data(jpg)
            if 'DateTimeOriginal' in jpg_exif:
                datetime = jpg_exif['DateTimeOriginal']
            else:
                datetime = 'Not Recorded'
            if 'ImageDescription' in jpg_exif:
                img_desc = jpg_exif['ImageDescription']
            else:
                img_desc = 'No Description'
            if 'GPSTrack' in jpg_exif['GPSInfo']:
                gps_track = jpg_exif['GPSInfo']['GPSTrack'][0] / jpg_exif['GPSInfo']['GPSTrack'][1]
            else:
                gps_track = 'Not Recorded'
            jpg_dict[file[:-4]] = (get_lat_lon(jpg_exif),
                                   datetime, img_desc, gps_track)

    return jpg_dict

def get_photo_name(jpg_dict, datetime):
    for name in jpg_dict:
        if jpg_dict[name][1] == datetime.strftime('%Y:%m:%d %H:%M:%S'):
            return name

def thumb_maker(jpg, jpg_folder):
    if jpg.lower().endswith('.jpg'):
        image = PIL.Image.open(os.path.join(jpg_folder, jpg))
        thm_size = (200,200)
        tag_size = (400,400)
        image.thumbnail(thm_size, Image.NEAREST)
        image.save(os.path.join(jpg_folder, jpg[:-4] + '_thm.jpg'), "JPEG", quality=50, optimize=True)
        image.thumbnail(tag_size, Image.NEAREST)
        image.save(os.path.join(jpg_folder, jpg[:-4] + '_tag.jpg'), "JPEG", quality=50, optimize=True)
        image.close()


def write_geojson(jpg_dict, datetimes):
    """Returns a geojson representing the location of all photos"""
    json  = '{\n'
    json += '    "type":"FeatureCollection",\n'
    json += '    "features": [{\n'
    x = 1
    for i in range(0, len(datetimes)):
        j = get_photo_name(jpg_dict, datetimes[i])
        # this if/else statements blanks out any comments that have a single slash that will invalidate the json text.
        if '\\' in jpg_dict[j][2]:
            description = ''
        else:
            description = jpg_dict[j][2]
        json += '        "type": "Feature",\n'
        json += '        "geometry": {\n'
        json += '            "type":"Point",\n'
        json += '            "coordinates":[%s, %s]\n' % (jpg_dict[j][0][1], jpg_dict[j][0][0])
        json += '        },\n'
        json += '        "properties": {\n'
        json += '            "id": "%s",\n' % x
        json += '            "zoom":15,\n'
        json += '            "image":"%s",\n' % ('/snowsurvey/' + j + '.jpg')
        json += '            "thumb":"%s",\n' % ('/snowsurvey/' + j + '_tag.jpg')
        json += '            "source-credit": "Source:NOAA Office of Water Prediction Snow Survey Program",\n'
        json += '            "source-link": "http://www.nohrsc.noaa.gov/snowsurvey",\n'
        json += '            "description": "%s",\n' % description
        date = jpg_dict[j][1].split(' ')[0].split(':')
        time = jpg_dict[j][1].split(' ')[1]
        json += '            "date": "%s",\n' % (date[0] + '-' + date[1] + '-' + date[2])
        json += '            "time": "%s",\n' % (time)
        if jpg_dict[j][3] != 'Not Recorded':
            if jpg_dict[j][3] > 270.0:
              heading = 90 - (360 - jpg_dict[j][3])
            else:
              heading = 90 + jpg_dict[j][3]
        else:
            heading = 'Not Recorded'
        json += '            "photo_heading": "%s"\n' % (heading)
        json += '        }\n'
        if x < len(jpg_dict):
            json += '        }, {\n'
        elif x == len(jpg_dict):
            json += '    }\n]\n}'
        x += 1


    return json

def write_kml(jpg_dict, datetimes):
      """Returns a kml with photo overlays"""
      kml = '<?xml version="1.0" encoding="utf-8"?>\n'
      kml += '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
      kml += '  <Document>\n'
      kml += '    <name>Snow Survey</name>\n'
      kml += '    <open>1</open>\n'
      kml += '    <Style id="Photo">\n'
      kml += '      <IconStyle>\n'
      kml += '        <scale>1.0</scale>\n'
      kml += '        <Icon>\n'
      kml += '          <href>root://icons/palette-4.png</href>\n'
      kml += '          <x>192</x>\n'
      kml += '          <y>64</y>\n'
      kml += '          <w>32</w>\n'
      kml += '          <h>32</h>\n'
      kml += '        </Icon>\n'
      kml += '      </IconStyle>\n'
      kml += '    </Style>\n'
      kml += '    <Folder>\n'
      kml += '      <name></name>\n'
      kml += '      <open>1</open>\n'
      for i in range(0, len(datetimes)):
        j = get_photo_name(jpg_dict, datetimes[i])
        if '//' in jpg_dict[j][2]:
          description = ''
        else:
          description = jpg_dict[j][2]
        kml += '    <Placemark>\n'
        kml += '      <name>%s</name>\n' % description
        kml += '      <Snippet maxLines="2"></Snippet>\n'
        kml += '      <description><![CDATA[\n'
        kml += '        <a href="%s"><br>\n        <img src="%s"><br>' % ('/snowsurvey/' + j + '_tag.jpg', '/snowsurvey/' + j + '_thm.jpg')
        kml += '        <b>%s</b><br><br></a>\n' % (description)
        kml += '        <a href="%s">Full Size</a><br>\n' % ('/snowsurvey/' + j + '.jpg')
        kml += '        <a href="%s">Reduced Size</a><br>\n' % ('/snowsurvey/' + j + '_tag.jpg')
        kml += '      ]]></description>\n'
        kml += '      <TimeStamp>\n'
        kml += '        <when>%s</when>\n' % (jpg_dict[j][1].split(' ')[0])
        kml += '      </TimeStamp>\n'
        kml += '      <styleUrl>#Photo</styleUrl>\n'
        kml += '      <Point>\n'
        kml += '        <altitudeMode>clampedToGround</altitudeMode>\n'
        kml += '        <coordinates>%s, %s</coordinates>\n' % (jpg_dict[j][0][1], jpg_dict[j][0][0])
        kml += '      </Point>\n'
        kml += '      <Style>\n'
        kml += '        <IconStyle>\n'
        kml += '          <Icon>\n'
        kml += '            <href>%s</href>\n' % ('/snowsurvey/' + j + '_thm.jpg')
        kml += '          </Icon>\n'
        kml += '        </IconStyle>\n'
        kml += '      </Style>\n'
        kml += '    </Placemark>\n'

      kml += '    </Folder>\n</Document>\n</kml>'
      return kml

def main():
    jpg_folder = 'C:/Users/shawn.carter/Desktop/Fox_River_Flood_Survey/img'
    jpg_dict = image_location(jpg_folder)
    datetimes = [datetime.strptime(jpg_dict[i][1], '%Y:%m:%d %H:%M:%S') for i in jpg_dict]
    datetimes = sorted(datetimes)
    json = write_geojson(jpg_dict, datetimes)
    with open('C:/Users/shawn.carter/Desktop/Fox_River_Flood_Survey/map.geojson', 'wb') as outFile:
        outFile.write(json)
    for i in os.listdir(jpg_folder):
        thumb_maker(i, jpg_folder)
    kml = write_kml(jpg_dict, datetimes)
    with open('C:/Users/shawn.carter/Desktop/Fox_River_Flood_Survey/map.kml', 'wb') as outFile:
        outFile.write(kml)

if __name__== "__main__":
    main()
