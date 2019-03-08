import sqlite3
from read_data import *
from pointcloud import *
from misc import *
from write_json import *

myCounter=None

write_header()

transDict = getTranslateDict("input/translation/dictionary_NL_EN.csv")
print("CSV: Translation loaded")

#load Pointcloud
loadPC("input/clipped.las")
print("AHN: Pointcloud loaded")

################################################################################
#AuxiliaryTrafficArea
################################################################################
connATA = sqlite3.connect("input/BGT/bgt_auxiliarytrafficarea.sqlite")
columnsATA = ["tijdstipregistratie", "bgt_functie", "bgt_fysiekvoorkomen", "relatievehoogteligging", "geometry"] #can be that relatievehoogteligging is useless as we derive height from pointcloud
tableATA = "ondersteunendwegdeel"
dataATA = getColumns(connATA, tableATA, columnsATA)
dataATA = translateArray(transDict, dataATA)
dataATA[:,-1] = np.ma.apply_along_axis(getVertices, 1, dataATA)
print("BGT: AuxiliaryTrafficArea loaded")

points = []
BPs = []

counter = 1
for i in range(dataATA.shape[0]):
    pointsList, numberVertices = getPoints(dataATA[i][-1], 2, "median")
    points.append(pointsList)
    BPs.append(numberVertices)
    print("polygon " + str(counter) + " of " + str(dataATA.shape[0]) + ": points read")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

#ATAwkt = []
vertices = []
indexes = []

counter = 1
for i in range(dataATA.shape[0]):
    Tvertices, Tindexes = getTriangles(points[i], BPs[i])
    vertices.append(Tvertices)
    indexes.append(Tindexes)
    print("polygon " + str(counter) + " of " + str(dataATA.shape[0]) + ": triangulated")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

type="AuxiliaryTrafficArea"
attributes= ["creationDate", "class", "surfaceMaterial"]
geomType = "MultiSurface"
lod = 1

counter = 1
for i in range(dataATA.shape[0]):
    attrdict = {}
    for j, elem in enumerate(attributes):
        attrdict[elem] = dataATA[i,j]
    write_cityObject(type, attrdict, geomType, lod, indexes[i], vertices[i])
    print("polygon " + str(counter) + " of " + str(dataATA.shape[0]) + ": written to JSON")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

create_json("ATA.json")
refresh_json()
write_header()


################################################################################
#BridgeConstructionElement
################################################################################
connBCE = sqlite3.connect("input/BGT/bgt_bridgeconstructionelement.sqlite")
columnsBCE = ["tijdstipregistratie", "relatievehoogteligging", "geometry"]
tableBCE = "overbruggingsdeel"
dataBCE = getColumns(connBCE, tableBCE, columnsBCE)
dataBCE = translateArray(transDict, dataBCE)
dataBCE[:,-1] = np.ma.apply_along_axis(getVertices, 1, dataBCE)
print("BGT: BridgeConstructionElement loaded")

points = []
BPs = []

counter = 1
for i in range(dataBCE.shape[0]):
    pointsList, numberVertices = getPoints(dataBCE[i][-1], 2, "median")
    points.append(pointsList)
    BPs.append(numberVertices)
    print("polygon " + str(counter) + " of " + str(dataBCE.shape[0]) + ": points read")
    counter = counter + 1

#ATAwkt = []
vertices = []
indexes = []

counter = 1
for i in range(dataBCE.shape[0]):
    Tvertices, Tindexes = getTriangles(points[i], BPs[i])
    vertices.append(Tvertices)
    indexes.append(Tindexes)
    print("polygon " + str(counter) + " of " + str(dataBCE.shape[0]) + ": triangulated")
    counter = counter + 1

type="BridgeConstructionElement"
attributes= ["creationDate"]
geomType = "MultiSurface"
lod = 1

counter = 1
for i in range(dataBCE.shape[0]):
    attrdict = {}
    for j, elem in enumerate(attributes):
        attrdict[elem] = dataBCE[i,j]
    write_cityObject(type, attrdict, geomType, lod, indexes[i], vertices[i])
    print("polygon " + str(counter) + " of " + str(dataBCE.shape[0]) + ": written to JSON")
    counter = counter + 1

create_json("BCE.json")
refresh_json()
write_header()

################################################################################
#Building 1
################################################################################
connB1 = sqlite3.connect("input/BGT/bgt_buildingpart.sqlite")
columnsB1 = ["tijdstipregistratie", "geometry"]
tableB1 = "pand"
dataB1 = getColumns(connB1, tableB1, columnsB1)
dataB1 = translateArray(transDict, dataB1)
dataB1[:,-1] = np.ma.apply_along_axis(getVertices, 1, dataB1)
print("BGT: Buildingpart loaded")

#Building 2
connB2 = sqlite3.connect("input/BAG/bag_pand.sqlite")
columnsB2 = ["bouwjaar", "gebruiksdoel", "geometry"]
tableB2 = "pand"
dataB2 = getColumns(connB2, tableB2, columnsB2, time="no")
dataB2 = translateArray(transDict, dataB2)
dataB2[:,-1] = np.ma.apply_along_axis(getVertices, 1, dataB2)
print("BAG: Pand loaded")

BMatrix = getOverlapMatrix(dataB1[:,-1], dataB2[:,-1])
print("Building Overlapmatrix created")

dataB = np.empty((dataB1.shape[0], 4), dtype=object)
dataB[:,0] = dataB1[:,0]
dataB[:,-1] = dataB1[:,-1]

for i in range(BMatrix.shape[0]):
    if np.max(BMatrix[i]) > 0.1:
        index = np.argmax(BMatrix[i])
        dataB[i,1] = dataB2[index,0]
        dataB[i,2] = dataB2[index,1]
    else:
        dataB[i,1] = "unknown"
        dataB[i,2] = "unknown"
print("Building BAG and BGT joined")

vertices = []
indexes = []
storeys = []

counter = 1
for i in range(dataB.shape[0]):
    height = getHeight(dataB[i][-1], 6, "median")
    Tvertices, Tindexes = get3DModel(dataB[i][-1], height)
    vertices.append(Tvertices)
    indexes.append(Tindexes)

    storey = height // 4.0
    if storey == 0:
        storey = 1
    storeys.append(storey)

    print("polygon " + str(counter) + " of " + str(dataB.shape[0]) + ": 3D model created")
    counter = counter + 1

type="Building"
attributes= ["creationDate", "yearOfConstruction", "class", "storeysAboveGround"]
geomType = "Solid"
lod = 1

counter = 1
for i in range(dataB.shape[0]):
    attrdict = {}
    for j, elem in enumerate(attributes):
        if j == 3:
            attrdict[elem] = storeys[i]
        else:
            attrdict[elem] = dataB[i,j]
    write_cityObject(type, attrdict, geomType, lod, indexes[i], vertices[i], D3 = "3D")
    print("polygon " + str(counter) + " of " + str(dataB.shape[0]) + ": written to JSON")
    counter = counter + 1
    if counter == 30:
        break

create_json("building.json")
refresh_json()
write_header()

################################################################################
#LandUse
################################################################################
connLU = sqlite3.connect("input/BGT/bgt_onbegroeidterreindeel.sqlite")
columnsLU = ["tijdstipregistratie", "geometry"]
tableLU = "onbegroeidterreindeel"
dataLU = getColumns(connLU, tableLU, columnsLU)
dataLU = translateArray(transDict, dataLU)
dataLU[:,-1] = np.ma.apply_along_axis(getVertices, 1, dataLU)

print("BGT: Onbegroeidterreindeel loaded")

points = []
BPs = []

counter = 1
for i in range(dataLU.shape[0]):
    pointsList, numberVertices = getPoints(dataLU[i][-1], 2, "median")
    points.append(pointsList)
    BPs.append(numberVertices)
    print("polygon " + str(counter) + " of " + str(dataLU.shape[0]) + ": points read")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

#ATAwkt = []
vertices = []
indexes = []

counter = 1
for i in range(dataLU.shape[0]):
    Tvertices, Tindexes = getTriangles(points[i], BPs[i])
    vertices.append(Tvertices)
    indexes.append(Tindexes)
    print("polygon " + str(counter) + " of " + str(dataLU.shape[0]) + ": triangulated")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

type="LandUse"
attributes= ["creationDate"]
geomType = "MultiSurface"
lod = 1

counter = 1
for i in range(dataLU.shape[0]):
    attrdict = {}
    for j, elem in enumerate(attributes):
        attrdict[elem] = dataLU[i,j]
    write_cityObject(type, attrdict, geomType, lod, indexes[i], vertices[i])
    print("polygon " + str(counter) + " of " + str(dataLU.shape[0]) + ": written to JSON")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

create_json("LU.json")
refresh_json()
write_header()


################################################################################
#PlantCover1
################################################################################
connPC1 = sqlite3.connect("input/BGT/bgt_plantcover.sqlite")
columnsPC1 = ["tijdstipregistratie", "bgt_fysiekvoorkomen", "geometry"]
tablePC1 = "begroeidterreindeel"
dataPC1 = getColumns(connPC1, tablePC1, columnsPC1)
dataPC1 = translateArray(transDict, dataPC1)
dataPC1[:,-1] = np.ma.apply_along_axis(getVertices, 1, dataPC1)

print("BGT: Plantcover loaded")

points = []
BPs = []

counter = 1
for i in range(dataPC1.shape[0]):
    pointsList, numberVertices = getPoints(dataPC1[i][-1], 2, "median")
    points.append(pointsList)
    BPs.append(numberVertices)
    print("polygon " + str(counter) + " of " + str(dataPC1.shape[0]) + ": points read")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

#ATAwkt = []
vertices = []
indexes = []

counter = 1
for i in range(dataPC1.shape[0]):
    Tvertices, Tindexes = getTriangles(points[i], BPs[i])
    vertices.append(Tvertices)
    indexes.append(Tindexes)
    print("polygon " + str(counter) + " of " + str(dataPC1.shape[0]) + ": triangulated")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

type="PlantCover"
attributes= ["creationDate", "class", "class"]
geomType = "MultiSurface"
lod = 1

counter = 1
for i in range(dataPC1.shape[0]):
    attrdict = {}
    for j, elem in enumerate(attributes):
        attrdict[elem] = dataPC1[i,j]
    write_cityObject(type, attrdict, geomType, lod, indexes[i], vertices[i])
    print("polygon " + str(counter) + " of " + str(dataPC1.shape[0]) + ": written to JSON")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

################################################################################
#PlantCover2
################################################################################
connPC2 = sqlite3.connect("input/BGT/bgt_ondersteunendwaterdeel.sqlite")
columnsPC2 = ["tijdstipregistratie", "bgt_type", "geometry"]
tablePC2 = "ondersteunendwaterdeel"
dataPC2 = getColumns(connPC2, tablePC2, columnsPC2)
dataPC2 = translateArray(transDict, dataPC2)
dataPC2[:,-1] = np.ma.apply_along_axis(getVertices, 1, dataPC2)
print("BGT: OndersteunendWaterdeel loaded")

points = []
BPs = []

counter = 1
for i in range(dataPC2.shape[0]):
    pointsList, numberVertices = getPoints(dataPC2[i][-1], 2, "median")
    points.append(pointsList)
    BPs.append(numberVertices)
    print("polygon " + str(counter) + " of " + str(dataPC2.shape[0]) + ": points read")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

#ATAwkt = []
vertices = []
indexes = []

counter = 1
for i in range(dataPC2.shape[0]):
    Tvertices, Tindexes = getTriangles(points[i], BPs[i])
    vertices.append(Tvertices)
    indexes.append(Tindexes)
    print("polygon " + str(counter) + " of " + str(dataPC2.shape[0]) + ": triangulated")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

type="PlantCover"
attributes= ["creationDate", "class", "class"]
geomType = "MultiSurface"
lod = 1

counter = 1
for i in range(dataPC2.shape[0]):
    attrdict = {}
    for j, elem in enumerate(attributes):
        attrdict[elem] = dataPC2[i,j]
    write_cityObject(type, attrdict, geomType, lod, indexes[i], vertices[i])
    print("polygon " + str(counter) + " of " + str(dataPC2.shape[0]) + ": written to JSON")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

create_json("PC.json")
refresh_json()
write_header()

################################################################################
#GenericCityObject1
################################################################################
connGCO1 = sqlite3.connect("input/BGT/bgt_overigbouwwerk.sqlite")
columnsGCO1 = ["tijdstipregistratie", "bgt_type", "geometry"]
tableGCO1 = "overigbouwwerk"
dataGCO1 = getColumns(connGCO1, tableGCO1, columnsGCO1)
dataGCO1 = translateArray(transDict, dataGCO1)
dataGCO1[:,-1] = np.ma.apply_along_axis(getVertices, 1, dataGCO1)
print("BGT: OverigBouwwerk loaded")

points = []
BPs = []

counter = 1
for i in range(dataGCO1.shape[0]):
    pointsList, numberVertices = getPoints(dataGCO1[i][-1], 2, "median")
    points.append(pointsList)
    BPs.append(numberVertices)
    print("polygon " + str(counter) + " of " + str(dataGCO1.shape[0]) + ": points read")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

#ATAwkt = []
vertices = []
indexes = []

counter = 1
for i in range(dataGCO1.shape[0]):
    Tvertices, Tindexes = getTriangles(points[i], BPs[i])
    vertices.append(Tvertices)
    indexes.append(Tindexes)
    print("polygon " + str(counter) + " of " + str(dataGCO1.shape[0]) + ": triangulated")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

type="GenericCityObject"
attributes= ["creationDate", "class"]
geomType = "MultiSurface"
lod = 1

counter = 1
for i in range(dataGCO1.shape[0]):
    attrdict = {}
    for j, elem in enumerate(attributes):
        attrdict[elem] = dataGCO1[i,j]
    write_cityObject(type, attrdict, geomType, lod, indexes[i], vertices[i])
    print("polygon " + str(counter) + " of " + str(dataGCO1.shape[0]) + ": written to JSON")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

################################################################################
#GenericCityObject2
################################################################################
connGCO2 = sqlite3.connect("input/BGT/bgt_scheiding.sqlite")
columnsGCO2 = ["tijdstipregistratie", "bgt_type", "geometry"]
tableGCO2 = "scheiding"
dataGCO2 = getColumns(connGCO2, tableGCO2, columnsGCO2)
dataGCO2 = translateArray(transDict, dataGCO2)
dataGCO2[:,-1] = np.ma.apply_along_axis(getVertices, 1, dataGCO2)
print("BGT: Scheiding loaded")

points = []
BPs = []

counter = 1
for i in range(dataGCO2.shape[0]):
    pointsList, numberVertices = getPoints(dataGCO2[i][-1], 2, "median")
    points.append(pointsList)
    BPs.append(numberVertices)
    print("polygon " + str(counter) + " of " + str(dataGCO2.shape[0]) + ": points read")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

#ATAwkt = []
vertices = []
indexes = []

counter = 1
for i in range(dataGCO2.shape[0]):
    Tvertices, Tindexes = getTriangles(points[i], BPs[i])
    vertices.append(Tvertices)
    indexes.append(Tindexes)
    print("polygon " + str(counter) + " of " + str(dataGCO2.shape[0]) + ": triangulated")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

type="GenericCityObject"
attributes= ["creationDate", "class"]
geomType = "MultiSurface"
lod = 1

counter = 1
for i in range(dataGCO2.shape[0]):
    attrdict = {}
    for j, elem in enumerate(attributes):
        attrdict[elem] = dataGCO2[i,j]
    write_cityObject(type, attrdict, geomType, lod, indexes[i], vertices[i])
    print("polygon " + str(counter) + " of " + str(dataGCO2.shape[0]) + ": written to JSON")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

create_json("GCO.json")
refresh_json()
write_header()


################################################################################
#TrafficArea1
################################################################################
connTC = sqlite3.connect("input/BGT/bgt_trafficarea.sqlite")
columnsTC = ["tijdstipregistratie", "bgt_functie", "bgt_fysiekvoorkomen", "geometry"]
tableTC = "wegdeel"
dataTC = getColumns(connTC, tableTC, columnsTC)
dataTC = translateArray(transDict, dataTC)
dataTC[:,-1] = np.ma.apply_along_axis(getVertices, 1, dataTC)
print("BGT: TrafficArea loaded")

points = []
BPs = []

counter = 1
for i in range(dataTC.shape[0]):
    pointsList, numberVertices = getPoints(dataTC[i][-1], 2, "median")
    points.append(pointsList)
    BPs.append(numberVertices)
    print("polygon " + str(counter) + " of " + str(dataTC.shape[0]) + ": points read")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

#ATAwkt = []
vertices = []
indexes = []

counter = 1
for i in range(dataTC.shape[0]):
    Tvertices, Tindexes = getTriangles(points[i], BPs[i])
    vertices.append(Tvertices)
    indexes.append(Tindexes)
    print("polygon " + str(counter) + " of " + str(dataTC.shape[0]) + ": triangulated")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

type="TrafficArea"
attributes= ["creationDate", "class", "surfaceMaterial"]
geomType = "MultiSurface"
lod = 1

counter = 1
for i in range(dataTC.shape[0]):
    attrdict = {}
    for j, elem in enumerate(attributes):
        attrdict[elem] = dataTC[i,j]
    write_cityObject(type, attrdict, geomType, lod, indexes[i], vertices[i])
    print("polygon " + str(counter) + " of " + str(dataTC.shape[0]) + ": written to JSON")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

create_json("TA.json")
refresh_json()
write_header()

################################################################################
#WaterBody
################################################################################
connWB = sqlite3.connect("input/BGT/bgt_waterdeel.sqlite")
columnsWB = ["tijdstipregistratie","plus_type", "geometry"]
tableWB = "waterdeel"
dataWB = getColumns(connWB, tableWB, columnsWB)
dataWB = translateArray(transDict, dataWB)
dataWB[:,-1] = np.ma.apply_along_axis(getVertices, 1, dataWB)
print("BGT: Waterdeel loaded")

print("TODO: fixed height!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

points = []
BPs = []

counter = 1
for i in range(dataWB.shape[0]):
    pointsList, numberVertices = getPoints(dataWB[i][-1], 9, "median")
    points.append(pointsList)
    BPs.append(numberVertices)
    print("polygon " + str(counter) + " of " + str(dataWB.shape[0]) + ": points read")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

#ATAwkt = []
vertices = []
indexes = []

counter = 1
for i in range(dataWB.shape[0]):
    Tvertices, Tindexes = getTriangles(points[i], BPs[i])
    vertices.append(Tvertices)
    indexes.append(Tindexes)
    print("polygon " + str(counter) + " of " + str(dataWB.shape[0]) + ": triangulated")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

type="WaterBody"
attributes= ["creationDate", "class"]
geomType = "MultiSurface"
lod = 1

counter = 1
for i in range(dataWB.shape[0]):
    attrdict = {}
    for j, elem in enumerate(attributes):
        attrdict[elem] = dataWB[i,j]
    write_cityObject(type, attrdict, geomType, lod, indexes[i], vertices[i])
    print("polygon " + str(counter) + " of " + str(dataWB.shape[0]) + ": written to JSON")
    counter = counter + 1
    if counter != None:
        if counter == myCounter:
            break

create_json("WB.json")
refresh_json()
