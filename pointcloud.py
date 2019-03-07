from shapely.geometry import Point, Polygon
import shapely.wkt
import numpy as np
from laspy.file import File

dataset = None

def loadPC(path):
    inFile = File(path, mode='r')

    scale = inFile.header.scale[0]
    xOffset = inFile.header.offset[0]
    yOffset = inFile.header.offset[1]
    zOffset = inFile.header.offset[2]

    global dataset

    dataset = np.vstack([inFile.x, inFile.y, inFile.z, inFile.Classification]).transpose()
    dataset[:,0] = dataset[:,0] * scale + xOffset
    dataset[:,1] = dataset[:,1] * scale + yOffset
    dataset[:,2] = dataset[:,2] * scale + zOffset


    #dataset = inFile.points

def getPoints(polygon, pointClass, type):

    poly = shapely.wkt.loads(polygon)
    x, y = poly.exterior.coords.xy
    vertices = np.column_stack((x, y)).tolist()

    smallDataset = np.copy(dataset)

    smallDataset = smallDataset[smallDataset[:,0] > poly.bounds[0]]
    smallDataset = smallDataset[smallDataset[:,0] < poly.bounds[2]]
    smallDataset = smallDataset[smallDataset[:,1] > poly.bounds[1]]
    smallDataset = smallDataset[smallDataset[:,1] < poly.bounds[3]]
    smallDataset = smallDataset[smallDataset[:,3] == pointClass]
    pointsInPoly = []

    numberVertices=0
    for elem in vertices:
        pointsInPoly.append(elem)
        numberVertices = numberVertices + 1

    heights = []
    for i in range(0, smallDataset.shape[0]):
        p = Point(smallDataset[i][0], smallDataset[i][1])
        if p.within(poly):
            pointsInPoly.append([smallDataset[i][0], smallDataset[i][1], smallDataset[i][2]])
            heights.append(smallDataset[i][2])

    if type == "min":
        bHeight = np.amin(heights, axis=0)
    elif type == "max":
        bHeight = np.amax(heights, axis=0)
    elif type == "median":
        bHeight = np.median(heights, axis=0)

    for i in range(numberVertices):
        pointsInPoly[i].append(bHeight)

    return(pointsInPoly, numberVertices)


def getHeight(array, pointClass, type):

    polygon = array[-1]
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

    if type == "min":
        returner = np.amin(heights, axis=0)
    elif type == "max":
        returner = np.amax(heights, axis=0)
    elif type == "median":
        returner = np.median(heights, axis=0)

    return returner

def addHeight(pString, pointClass, type):
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
