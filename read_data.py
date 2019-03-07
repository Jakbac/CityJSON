import csv
import sqlite3
import prettytable
import numpy as np

"""con = sqlite3.connect('input/BGT/bgt_wegdeel.sqlite')
cursor = con.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())"""


#print all information from all columns from table
def printAllColumns(conn, table, old="no"):
    c = conn.cursor()
    c.execute("SELECT * FROM " + table + ";")
    output = prettytable.from_db_cursor(c)
    output.set_style(prettytable.PLAIN_COLUMNS)
    output.align = "l"
    #TODO remove values that are not exisiting
    print(output)

#print all information in specific columns(in list) from table
def printColumns(conn, table, columnNames, old="no"):
    mySearchString = ""
    for elem in columnNames:
        mySearchString = mySearchString + elem + ", "
    mySearchString = mySearchString[:-2]
    mySearchString = mySearchString + ", eindregistratie"
    print(mySearchString)
    c = conn.cursor()
    c.execute("SELECT " + mySearchString + " FROM " + table + ";")
    output = prettytable.from_db_cursor(c)
    output.set_style(prettytable.PLAIN_COLUMNS)
    output.align = "l"
    #TODO remove values that are not exisiting
    print(output)

#print all information from one column from table
def printColumn(conn, table, columnName, current, old="no"):
    c = conn.cursor()
    c.execute("SELECT " + columnName + ", eindregistratie FROM " + table + ";")
    output = prettytable.from_db_cursor(c)
    output.set_style(prettytable.PLAIN_COLUMNS)
    output.align = "l"
    #TODO remove values that are not exisiting
    return(output)

def getAllColumns(conn, table, old="no"):
    #TODO
    return

def getColumns(conn, table, columnNames, old="no", time="yes"):
    mySearchString = ""
    for elem in columnNames:
        mySearchString = mySearchString + elem + ", "
    mySearchString = mySearchString[:-2]
    if time == "yes":
        mySearchString = mySearchString + ", eindregistratie"
    c = conn.cursor()
    c.execute("SELECT " + mySearchString + " FROM " + table + ";")
    clist = c.fetchall()
    data = np.array(clist)
    if time == "yes":
        if (old=="no"):
            data = data[data[:, -1] == None]
            data = data[:, :-1]
    return(data)

def getColumn(conn, table, columnNames, old="no"):
    #TODO
    return

#get columnnames from table
def getColumnNames(conn, table):
    c = conn.cursor()
    c.execute("SELECT * FROM " + table + ";")
    names = [description[0] for description in c.description]
    return(names)

#get dictionary with translation
def getTranslateDict(path):
    with open(path, 'r') as csvfile:
        creader = csv.reader(csvfile, delimiter=';')
        transDict = {}
        for row in creader:
            transDict[row[0]] = row[1]
    return(transDict)

#getTranslateDict('input/translation/dictionary_NL_EN.csv')

"""
conn = sqlite3.connect("input/BGT/bgt_auxiliarytrafficarea.sqlite.sqlite")
columns = ["tijdstipregistratie", "bgt_functie", "bgt_fysiekvoorkomen"]
output = getColumns(conn, "ondersteunendwegdeel", columns)
print(output)
"""
