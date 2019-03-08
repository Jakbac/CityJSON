import numpy as np
import shapely.wkt
import shapely.geometry as sg
from shapely.wkb import dumps, loads
#from shapely.ops import triangulate

import matplotlib.pyplot as plt
import triangle as tr
import copy

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

def getTriangles(pointlist, numberVertBound):

    vertices = copy.deepcopy(pointlist)
    for row in vertices:
        del row[2]

    segments = []
    for i in range(numberVertBound - 1):
        segments.append([i, i + 1])
    segments.append([numberVertBound-1, 0])

    input = dict(vertices=vertices, segments=segments)
    tri = tr.triangulate(input, 'p') #-- 'p' is important to respect the segments

    """
    ax = plt.axes()

    print("number of triangles:", len(tri['triangles']))
    print(tri['triangles'])
    tr.plot(ax, **tri)
    plt.show()
    """

    indexes = tri["triangles"].flatten()

    return(pointlist, indexes)

    """#myWKT = "(("
    myWKT = "("
    for i, elem in enumerate(indexes):
        if i%3 == 0:
            if i > 0:
                myWKT = myWKT + "(" + str(pointlist[saver]).replace(",", "") + ")),("
            saver = elem
        #print(elem)
        myWKT = myWKT + "(" + str(pointlist[elem]).replace(",", "") + "),"
    myWKT = myWKT + "(" + str(pointlist[elem]).replace(",", "") + "))"
    myWKT = myWKT.replace("]", "")
    myWKT = myWKT.replace("[", "")

    myWKT = "MULTIPOLYGON (" + myWKT + ")"
    return(myWKT)"""

def get3DModel(polygon, height):

    footprint = shapely.wkt.loads(polygon)

    cm={}
    cm["vertices"] = []

    allsurfaces = [] #-- list of surfaces forming the oshell of the solid
    #-- exterior ring of each footprint
    oring = list(footprint.exterior.coords)
    oring.pop() #-- remove last point since first==last
    if footprint.exterior.is_ccw == False:
        #-- to get proper orientation of the normals
        oring.reverse()
    extrude_walls(oring, height, allsurfaces, cm)
    #-- interior rings of each footprint
    irings = []
    interiors = list(footprint.interiors)
    for each in interiors:
        iring = list(each.coords)
        iring.pop() #-- remove last point since first==last
        if each.is_ccw == True:
            #-- to get proper orientation of the normals
            iring.reverse()
        irings.append(iring)
        extrude_walls(iring, height, allsurfaces, cm)
    #-- top-bottom surfaces
    extrude_roof_ground(oring, irings, height, False, allsurfaces, cm)
    extrude_roof_ground(oring, irings, 0, True, allsurfaces, cm)
    #-- add the extruded geometry to the geometry
    boundaries = []
    boundaries.append(allsurfaces)

    boundariesFormatted = []
    for elem in boundaries:
        for _elem in elem:
            boundariesFormatted.append(_elem[0])

    #-- add the geom to the building

    return cm["vertices"], boundariesFormatted

def extrude_roof_ground(orng, irngs, height, reverse, allsurfaces, cm):
    oring = copy.deepcopy(orng)
    irings = copy.deepcopy(irngs)
    if reverse == True:
        oring.reverse()
        for each in irings:
            each.reverse()
    for (i, pt) in enumerate(oring):
        cm['vertices'].append([pt[0], pt[1], height])
        oring[i] = (len(cm['vertices']) - 1)
    for (i, iring) in enumerate(irings):
        for (j, pt) in enumerate(iring):
            cm['vertices'].append([pt[0], pt[1], height])
            irings[i][j] = (len(cm['vertices']) - 1)
    # print(oring)
    output = []
    output.append(oring)
    for each in irings:
        output.append(each)
    allsurfaces.append(output)

def extrude_walls(ring, height, allsurfaces, cm):
    #-- each edge become a wall, ie a rectangle
    for (j, v) in enumerate(ring[:-1]):
        l = []
        cm['vertices'].append([ring[j][0],   ring[j][1],   0])
        cm['vertices'].append([ring[j+1][0], ring[j+1][1], 0])
        cm['vertices'].append([ring[j+1][0], ring[j+1][1], height])
        cm['vertices'].append([ring[j][0],   ring[j][1],   height])
        t = len(cm['vertices'])
        allsurfaces.append([[t-4, t-3, t-2, t-1]])
    #-- last-first edge
    l = []
    cm['vertices'].append([ring[-1][0], ring[-1][1], 0])
    cm['vertices'].append([ring[0][0],  ring[0][1],  0])
    cm['vertices'].append([ring[0][0],  ring[0][1],  height])
    cm['vertices'].append([ring[-1][0], ring[-1][1], height])
    t = len(cm['vertices'])
    allsurfaces.append([[t-4, t-3, t-2, t-1]])
