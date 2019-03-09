import json
import numpy as np

data = {}
cityObjects = {}
objectCounter = 1
allVertices = []

def write_header():
    EPSG = 7415
    global data
    global cityObjects
    global objectCounter
    global vertices

    data['type'] = 'CityJSON'
    data['version'] = '0.9'

    metadata = {}
    metadata['referenceSystem'] = "urn:ogc:def:crs:EPSG::" + str(EPSG) + ""
    data['metadata'] = metadata

    data["CityObjects"] = cityObjects

    data["vertices"] = allVertices

    """
    appearance = {}
    data['appearance'] = appearance

    geometryTemplates = {}
    data['geometry-templates'] = geometryTemplates
    """
    print("JSON Header written")

def write_cityObject(type, attributes, geomType, lod, boundaries, vertices, D3="Flat"):
    global cityObjects
    global objectCounter
    global allVertices

    dictObj = {}
    cityObjects["id_" + str(type) + "_" + str(objectCounter)] = dictObj

    dictObj["type"] = type

    geometry = []
    geomdict = {}

    geomdict['type'] = geomType
    geomdict['lod'] = lod


    if D3=="Flat":
        boundaries = np.array(boundaries)
        boundaries = boundaries + len(allVertices)
        boundaries = boundaries.reshape(-1, 3).tolist()
        for i, elem in enumerate(boundaries):
            boundaries[i] = [elem]
    elif D3== "3D":
        for i, elem in enumerate(boundaries):
            for j, _elem in enumerate(elem):
                boundaries[i][j] = _elem + len(allVertices)
            boundaries[i] = [elem]
        boundaries = [boundaries]
    elif D3== "water":
        for i, elem in enumerate(boundaries):
            boundaries[i] = elem + len(allVertices)
        boundaries = [[boundaries]]

    geomdict['boundaries'] = boundaries

    geometry.append(geomdict)
    dictObj["geometry"] = geometry

    semantics = {}
    surfaces = []
    surfdict = attributes
    surfaces.append(surfdict)
    semantics["surfaces"] = surfaces
    semantics["values"] = []
    dictObj["semantics"] = semantics


    counter = 0
    for elem in vertices:
        allVertices.append(elem)
        counter = counter + 1

    objectCounter = objectCounter + 1


def write_cityObject_old(dArr, attributes, lod, type, geoType, verticeCs, boundaries):
    global data
    global cityObjects
    global objectCounter
    global vertices

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

    boundaries = np.array(boundaries).reshape(-1, 3).tolist()

    geomdict['boundaries'] = [boundaries]

    geometry.append(geomdict)

    dictObj["geometry"] = geometry

    print(type(COvertices))


    cityObjects["id-" + str(objectCounter)] = dictObj

    vertices.extend(COvertices)

    objectCounter = objectCounter + 1

def refresh_json():
    global data
    global cityObjects
    global objectCounter
    global vertices
    data.clear()
    cityObjects.clear()
    objectCounter = 1
    del allVertices[:]

    print("JSON refreshed")

def create_json(filename):
    global data
    data["vertices"] = allVertices
    with open("output/" + filename, 'w') as outfile:
        json.dump(data, outfile, indent=2)
