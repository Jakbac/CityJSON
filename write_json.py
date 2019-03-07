import json
import numpy as np

data = {}
cityObjects = {}
objectCounter = 1


def write_header():
    EPSG = 7415
    global data
    global cityObjects
    global objectCounter


    data['type'] = 'CityJSON'
    data['version'] = '0.9'
    extensions = {}
    data['extensions'] = extensions
    metadata = {}
    metadata['referenceSystem'] = "urn:ogc:def:crs:EPSG::" + str(EPSG) + ""
    data['metadata'] = metadata

    transform = {}
    transform["scale"] = []
    transform["translate"] = []
    data['transform'] = transform

    data["CityObjects"] = cityObjects

    """
    appearance = {}
    data['appearance'] = appearance
    geometryTemplates = {}
    data['geometry-templates'] = geometryTemplates
    """
def write_cityObject(type, attributes, lod, geoType, dArr, geom):
    global data
    global cityObjects
    global objectCounter

    dictObj = {}
    dictObj["type"] = type

    dictAttr = {}
    for i, elem in enumerate(attributes):
        dictAttr[elem] = dArr[i]
    attributes = dictAttr
    dictObj["attributes"] = attributes

    geometry = []
    geomdict = {}
    geomdict['type'] = "Solid"
    geomdict['lod'] = lod

    boundaries = list(range(len(vertices)-1))
    geomdict['boundaries'] = [[boundaries]]

    geometry.append(geomdict)

    dictObj["geometry"] = geometry

    cityObjects["id-" + str(objectCounter)] = dictObj

    data['vertices'] = vertices

    objectCounter = objectCounter + 1


def create_json():
    global data
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile, indent = 4)
