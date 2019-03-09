from shapely.geometry import Point, Polygon
import shapely.wkt
import numpy as np
from laspy.file import File
import matplotlib.pyplot as plt
import math
dataset = None

def loadPC(path):
    global dataset

    inFile = File(path, mode='r')

    scale = inFile.header.scale[0]
    xOffset = inFile.header.offset[0]
    yOffset = inFile.header.offset[1]
    zOffset = inFile.header.offset[2]


    dataset = np.vstack([inFile.x, inFile.y, inFile.z, inFile.Classification]).transpose()
    """
    dataset[:,0] = dataset[:,0] * scale + xOffset
    dataset[:,1] = dataset[:,1] * scale + yOffset
    dataset[:,2] = dataset[:,2] * scale + zOffset
    """

    dataset = np.around(dataset, decimals=5)
    #dataset = inFile.points

def getPoints(polygon, pointClass, type, invHeight):

    poly = shapely.wkt.loads(polygon)

    """
    x, y = poly.exterior.xy

    fig = plt.figure(1, figsize=(5,5), dpi=90)
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    ax.set_title('Polygon Edges')

    plt.show()
    """

    x, y = poly.exterior.coords.xy
    vertices = np.column_stack((x, y))
    vertices = vertices[:-1, :]

    vertices = np.around(vertices, decimals=5).tolist()

    smallDataset = np.copy(dataset)

    smallDataset = smallDataset[smallDataset[:,0] > poly.bounds[0]]
    smallDataset = smallDataset[smallDataset[:,0] < poly.bounds[2]]
    smallDataset = smallDataset[smallDataset[:,1] > poly.bounds[1]]
    smallDataset = smallDataset[smallDataset[:,1] < poly.bounds[3]]
    if len(pointClass) == 1:
        smallDataset = smallDataset[smallDataset[:,3] == pointClass[0]]
    elif len(pointClass) == 2:
        smallDataset = smallDataset[(smallDataset[:,3] == pointClass[0]) |
        (smallDataset[:,3] == pointClass[1])]
    elif len(pointClass) == 3:
        smallDataset = smallDataset[smallDataset[:,3] == pointClass[0] |
        (smallDataset[:,3] == pointClass[1]) |
        (smallDataset[:,3] == pointClass[2])]

    pointsInPoly = []

    numberVertices=0
    for i, elem in enumerate(vertices):
        pointsInPoly.append(elem)
        numberVertices = numberVertices + 1

    heights = []
    for i in range(0, smallDataset.shape[0]):
        p = Point(smallDataset[i][0], smallDataset[i][1])
        if p.within(poly):
            pointsInPoly.append([smallDataset[i][0], smallDataset[i][1], smallDataset[i][2]])
            heights.append(smallDataset[i][2])

    if len(heights) == 0:
        type="invalid"

    if type == "min":
        bHeight = np.amin(heights, axis=0)
    elif type == "max":
        bHeight = np.amax(heights, axis=0)
    elif type == "median":
        bHeight = np.median(heights, axis=0)
    elif type == "invalid":
        print("no points inside polygon")
        bHeight = invHeight

    for i in range(numberVertices):
        pointsInPoly[i].append(bHeight)

    return(pointsInPoly, numberVertices)

def getHeight(polygon, pointClass, type):

    poly = shapely.wkt.loads(polygon)

    smallDataset = np.copy(dataset)

    smallDataset = smallDataset[smallDataset[:,0] > poly.bounds[0]]
    smallDataset = smallDataset[smallDataset[:,0] < poly.bounds[2]]
    smallDataset = smallDataset[smallDataset[:,1] > poly.bounds[1]]
    smallDataset = smallDataset[smallDataset[:,1] < poly.bounds[3]]
    smallDataset = smallDataset[smallDataset[:,3] == pointClass]
    pointsInPoly = []


    for i in range(0, smallDataset.shape[0]):
        p = Point(smallDataset[i][0], smallDataset[i][1])
        if p.within(poly):
            pointsInPoly.append(i)


    heights = smallDataset[pointsInPoly][:,2]

    if (len(pointsInPoly) == 0):
        return "invalid"

    if type == "min":
        returner = np.amin(heights, axis=0)
    elif type == "max":
        returner = np.amax(heights, axis=0)
    elif type == "median":
        returner = np.median(heights, axis=0)

    return returner

"""def addHeight(pString, pointClass, type):
    pString = np.array(pString)
    poly = Polygon(pString[:,:2])
    smallDataset = np.copy(dataset)


    smallDataset = smallDataset[smallDataset[:,0] > poly.bounds[0]]
    smallDataset = smallDataset[smallDataset[:,0] < poly.bounds[2]]
    smallDataset = smallDataset[smallDataset[:,1] > poly.bounds[1]]
    smallDataset = smallDataset[smallDataset[:,1] < poly.bounds[3]]
    smallDataset = smallDataset[smallDataset[:,3] == pointClass]
    pointsInPoly = []


    for i in range(0, smallDataset.shape[0]):
        p = Point(smallDataset[i][0], smallDataset[i][1])
        if p.within(poly):
            pointsInPoly.append(i)

    #heights = smallDataset[pointsInPoly][:,2]
    heights =[1,1,1,1]


    if type == "min":
        returner = np.amin(heights, axis=0)
    elif type == "max":
        returner = np.amax(heights, axis=0)
    elif type == "median":
        returner = np.median(heights, axis=0)

    returner = np.array([returner, returner, returner])
    pString = np.array2string((np.column_stack((pString, returner))))
    print(pString)
    pString = pString.replace("[[", "(")
    pString = pString.replace("]]", ")")
    pString = pString.replace("]", ",")
    pString = pString.replace("[", "")


    print(pString)
    a/0

    return pString
"""
