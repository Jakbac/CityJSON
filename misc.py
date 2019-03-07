import numpy as np
import shapely.wkt
from shapely.wkb import dumps, loads
from shapely.ops import triangulate
from shapely.geometry import LineString

import matplotlib.pyplot as plt
import triangle as tr


def translateArray(transDict, myArr):
    for key, value in transDict.items():
        myArr[myArr == key] = value
    return(myArr)

def getVertices(myArr):
    geomString=myArr[-1]
    return(loads(geomString).wkt)

def getOverlapMatrix(geomArray1, geomArray2):

    """
    print(geomArray1.shape)
    print(geomArray2.shape)

    myIntersectArray = np.zeros((geomArray1.shape[0], geomArray2.shape[0]))

    print(myIntersectArray.shape)

    for i in range(0, myIntersectArray.shape[0]):
        for j in range(0, myIntersectArray.shape[1]):
            p1 = shapely.wkt.loads(geomArray1[i])
            p2 = shapely.wkt.loads(geomArray2[j])
            if p1.intersects(p2):
                p3 = p1.intersection(p2)
                myIntersectArray[i][j] = p3.area
        if (i%50 == 0):
            print(i, myIntersectArray.shape[0])

    np.save("IntersectArray", myIntersectArray)

    print(myIntersectArray)
    a/0
    """
    myIntersectArray = np.load("IntersectArray.npy")

    return(myIntersectArray)

def getTriangles(polystring):

    poly = shapely.wkt.loads(polystring)
    x, y = poly.exterior.coords.xy
    vertices = np.column_stack((x, y)).tolist()
    vertices = vertices[:-1]

    segments = []
    for i in range(len(vertices) - 1):
        sgt = [i, i+1]
        segments.append(sgt)
    segments.append([len(vertices) -1 , 0])

    input = dict(vertices=vertices, segments=segments)
    tri = tr.triangulate(input, 'p') #-- 'p' is important to respect the segments

    multipoly = tri["triangles"].tolist()
    triangles = []
    for elem in multipoly:
        triline = []
        for idx in elem:
            triline.append(vertices[idx])
        triangles.append(triline)

    return(triangles)

def create3DPoly(polygon, height, type):
    poly = shapely.wkt.loads(polygon)
    vertices = []
    if (type == "flat"):
        x, y = poly.exterior.coords.xy
        for i, elem in enumerate(x):
            vertices.append([x[i], y[i], height])
    elif(type =="volume"):
        x, y = poly.exterior.coords.xy
        #Ground
        vert = []
        for i, elem in enumerate(x):
            vert.append([x[i], y[i], 0])
        vertices.append(vert)
        for i, elem in enumerate(x):
            vert = []
            vert.append([x[i], y[i], 0])
            if i != len(x)-1:
                vert.append([x[i+1], y[i+1], 0])
                vert.append([x[i+1], y[i+1], height])
            else:
                vert.append([x[0], y[0], 0])
                vert.append([x[0], y[0], height])
            vert.append([x[i], y[i], 0])
            vertices.append(vert)
        for i, elem in enumerate(x):
            vert.append([x[i], y[i], height])
        vertices.append(vert)
        print("HI")

    return(vertices)
