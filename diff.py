#Reads two output files from shuffleparser and prints any differences between corresponding entries
#Usage: python diff.py input1 input2
#The input files are expected to use the format that is outputted by shuffleparser.py
#Namely:
#- Two line breaks (\n) between entries
#- First line of an entry is the index (which is ignored)
#- The rest of the lines of an entry will be of the format valuename: value
#It's also assumed that entries in the two files will be in the same order (meaning it doesn't check if the indexes are the same... for now)
#This has only been tested with Pokemon, Stage, and Ability data

import sys
from collections import OrderedDict

inputold = open(sys.argv[1])
contentsold = inputold.read()
entriesold = contentsold.split("\n\n")

inputnew = open(sys.argv[2])
contentsnew = inputnew.read()
entriesnew = contentsnew.split("\n\n")

#find indexes of entries that are different
updatedentryindexes = []
for i in range(len(entriesnew)):
    if i >= len(entriesold):
        updatedentryindexes.append(i)
    elif entriesnew[i] != entriesold[i]:
        updatedentryindexes.append(i)

for index in updatedentryindexes:
    #print new entries
    if index >= len(entriesold):
        print entriesnew[index]
        continue
    
    #get values of old entry
    oldentry = entriesold[index]
    oldvalues = oldentry.split("\n")
    oldvaluesdict = OrderedDict()
    for i in range(len(oldvalues)):
        #ignore index
        if i == 0:
            continue
        value = oldvalues[i]
        varname = value[0:value.find(":")]
        varvalue = value[value.find(":")+2:]
        oldvaluesdict[varname] = varvalue
    
    #get values of new entry
    newentry = entriesnew[index]
    newvalues = newentry.split("\n")
    newvaluesdict = OrderedDict()
    for i in range(len(newvalues)):
        #ignore index
        if i == 0:
            continue
        value = newvalues[i]
        varname = value[0:value.find(":")]
        varvalue = value[value.find(":")+2:]
        newvaluesdict[varname] = varvalue
    
    #find differences and print them out!
    try:
        print "Index {}: {}".format(index, newvaluesdict["Name"])
    except KeyError:
        try:
            print "Index {}: {}".format(index, newvaluesdict["Pokemon"])
        except KeyError:
            print "Index {}".format(index)
    
    for key in newvaluesdict.keys():
        try:
            oldvalue = oldvaluesdict[key]
            newvalue = newvaluesdict[key]
            if oldvalue != newvalue:
                print "{}: {} -> {}".format(key, oldvalue, newvalue)
        except KeyError:
            print "{}: (empty) -> {}".format(key, newvaluesdict[key])