import sqlite3
from read_data import *
from pointcloud import *
from misc import *
from write_json import *

write_header()

transDict = getTranslateDict("input/translation/dictionary_NL_EN.csv")
print("CSV: Translation loaded")

#load Pointcloud
loadPC("input/clipped.las")
print("AHN: Pointcloud loaded")

#AuxiliaryTrafficArea
connATA = sqlite3.connect("input/BGT/bgt_auxiliarytrafficarea.sqlite")
columnsATA = ["tijdstipregistratie", "bgt_functie", "bgt_fysiekvoorkomen", "relatievehoogteligging", "geometry"] #can be that relatievehoogteligging is useless as we derive height from pointcloud
tableATA = "ondersteunendwegdeel"
dataATA = getColumns(connATA, tableATA, columnsATA)
dataATA = translateArray(transDict, dataATA)
dataATA[:,-1] = np.ma.apply_along_axis(getVertices, 1, dataATA)
print("BGT: AuxiliaryTrafficArea loaded")
pointsATA = []
ATABPs = []
for i in range(dataATA.shape[0]):
    pointsList, numberVertices = getPoints(dataATA[i][-1], 2, "median")
    pointsATA.append(pointsList)
    ATABPs.append(numberVertices)
    break

triangleATA = []
for i in range(dataATA.shape[0]):
    getTriangles(pointsATA[i], ATABPs[i])

print(pointsATA)
a/0
print("AuxiliaryTrafficArea height calculated")

#BridgeConstructionElement =
connBCE = sqlite3.connect("input/BGT/bgt_bridgeconstructionelement.sqlite")
columnsBCE = ["tijdstipregistratie", "relatievehoogteligging", "geometry"]
tableBCE = "overbruggingsdeel"
dataBCE = getColumns(connBCE, tableBCE, columnsBCE)
dataBCE = translateArray(transDict, dataBCE)
dataBCE[:,-1] = np.ma.apply_along_axis(getVertices, 1, dataBCE)
print("BGT: BridgeConstructionElement loaded")


#Building 1
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

#LandUse
connLU = sqlite3.connect("input/BGT/bgt_onbegroeidterreindeel.sqlite")
columnsLU = ["tijdstipregistratie"]
tableLU = "onbegroeidterreindeel"
dataLU = getColumns(connLU, tableLU, columnsLU)
dataLU = translateArray(transDict, dataLU)
print("BGT: Onbegroeidterreindeel loaded")

#PlantCover1
connPC1 = sqlite3.connect("input/BGT/bgt_plantcover.sqlite")
columnsPC1 = ["tijdstipregistratie", "bgt_fysiekvoorkomen"]
tablePC1 = "begroeidterreindeel"
dataPC1 = getColumns(connPC1, tablePC1, columnsPC1)
dataPC1 = translateArray(transDict, dataPC1)
print("BGT: Plantcover loaded")

#PlantCover2
connPC2 = sqlite3.connect("input/BGT/bgt_ondersteunendwaterdeel.sqlite")
columnsPC2 = ["tijdstipregistratie", "bgt_type"]
tablePC2 = "ondersteunendwaterdeel"
dataPC2 = getColumns(connPC2, tablePC2, columnsPC2)
dataPC2 = translateArray(transDict, dataPC2)
print("BGT: OndersteunendWaterdeel loaded")

#GenericCityObject1
connGCO1 = sqlite3.connect("input/BGT/bgt_overigbouwwerk.sqlite")
columnsGCO1 = ["tijdstipregistratie", "bgt_type"]
tableGCO1 = "overigbouwwerk"
dataGCO1 = getColumns(connGCO1, tableGCO1, columnsGCO1)
dataGCO1 = translateArray(transDict, dataGCO1)
print("BGT: OverigBouwwerk loaded")

#GenericCityObject2
connGCO2 = sqlite3.connect("input/BGT/bgt_scheiding.sqlite")
columnsGCO2 = ["tijdstipregistratie", "bgt_type"]
tableGCO2 = "scheiding"
dataGCO2 = getColumns(connGCO2, tableGCO2, columnsGCO2)
dataGCO2 = translateArray(transDict, dataGCO2)
print("BGT: Scheiding loaded")

#TrafficArea1
connTC = sqlite3.connect("input/BGT/bgt_trafficarea.sqlite")
columnsTC = ["tijdstipregistratie", "bgt_functie", "bgt_fysiekvoorkomen"]
tableTC = "wegdeel"
dataTC = getColumns(connTC, tableTC, columnsTC)
dataTC = translateArray(transDict, dataTC)
print("BGT: TrafficArea loaded")

#WaterBody
connWB = sqlite3.connect("input/BGT/bgt_waterdeel.sqlite")
columnsWB = ["tijdstipregistratie","plus_type", "geometry"]
tableWB = "waterdeel"
dataWB = getColumns(connWB, tableWB, columnsWB)
dataWB = translateArray(transDict, dataWB)
dataWB[:,-1] = np.ma.apply_along_axis(getVertices, 1, dataWB)
print("BGT: Waterdeel loaded")

create_json()
