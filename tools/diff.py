#!/usr/bin/python

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

#here is a list of value names to ignore
ignorelist = ["Background ID", "Layout Index", "Coin reward (first clear)", "Coin reward (repeat clear)"]

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

wikitext = '{| border="1" class="sortable"\n!style="background-color: #ffffcc; width:5%;"|Dex\n!style="background-color: #ffffcc; width:5%;" class="unsortable"|Icon\n!style="background-color: #ffffcc; width:30%;"|Name\n!style="background-color: #ffffcc; width:10%;" class="unsortable"|[[Raise Max Level|RML]]\n!style="background-color: #ffffcc; width:20%;" class="unsortable"|[[Skill Swapper|SS (before)]]\n!style="background-color: #ffffcc; width:20%;" class="unsortable"|[[Skill Swapper|SS (after)]]\n'

for index in updatedentryindexes:
    #print new entries
    if index >= len(entriesold):
        print entriesnew[index]
        #line breaks between entries
        print
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
        
        #ignore values in ignorelist
        if varname in ignorelist:
            continue
        
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
        
        #ignore values in ignorelist
        if varname in ignorelist:
            continue
        
        newvaluesdict[varname] = varvalue
    
    #find differences and print them out!
    try:
        #for Pokemon
        print "Index {}: {}".format(index, newvaluesdict["Name"])
    except KeyError:
        #for Stages
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

    if len(sys.argv) <= 3:
        print
        continue
    
    #wikitext stuff
    try:
        if oldvaluesdict["RMLs"] == newvaluesdict["RMLs"]:
            rmlchange = ""
        else:
            rmlchange = "{} -> {}".format(oldvaluesdict["RMLs"], newvaluesdict["RMLs"])
    except KeyError:
        rmlchange = ""
    ssbefore = ""
    ssafter = ""
    for i in range(4):
        try:
            oldvalue = oldvaluesdict["SS Ability " + str(i+1)]
            oldvalue = oldvalue[:oldvalue.find("(")-1]
            ssbefore += "{{Skill With Tooltip|skill=" + oldvalue + "}}"
        except KeyError:
            ""
        try:
            newvalue = newvaluesdict["SS Ability " + str(i+1)]
            newvalue = newvalue[:newvalue.find("(")-1]
            ssafter += "{{Skill With Tooltip|skill=" + newvalue + "}}"
        except KeyError:
            ""
    if rmlchange != "" or ssbefore != ssafter:
        wikitext += "|-\n|{}\n|{}\n|[[{}]]\n|{}\n|{}\n|{}\n".format(newvaluesdict["Dex"], "{{Thumbicon|pokemon=" + newvaluesdict["Name"] + "}}", newvaluesdict["Name"], rmlchange, ssbefore if ssbefore != ssafter else "", ssafter if ssbefore != ssafter else "")
    
    #line breaks between entries
    print

wikitext += "|}"
#add a fourth argument, a file name, to print wikitext that shows a table of changes in pokemon data
if len(sys.argv) > 3:
    outputfile = open(sys.argv[3], 'w')
    outputfile.write(wikitext)