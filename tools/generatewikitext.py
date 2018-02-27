#!/usr/bin/python
# -*- coding: utf_8 -*-

from __future__ import division

import numpy as np
import sys, os.path
import datetime
import pytz
sys.path.append("../")
import pokemoninfo
from pokemoninfo import *
from stageinfo import *
from bindata import *
from miscdetails import *
import layoutimagegenerator

dropitems = {"0": "Nothing", "1":"Raise Max Level", "2":"Level Up", "3":"Exp. Booster S", "4":"Exp. Booster M", "5":"Exp. Booster L", "6":"Skill Booster S", "7":"Skill Booster M", "8":"Skill Booster L", "9":"Skill Swapper", "10":"Mega Speedup", "11":"Moves +5", "12":"Time +10", "13":"Exp. Points x1.5", "14":"Mega Start", "15":"Complexity -1", "16":"Disruption Delay", "17":"Attack Power ↑", "18":"1 Heart", "19":"2 Hearts", "20":"5 Hearts", "21":"3 Hearts", "22":"20 Hearts", "23":"10 Hearts", "24":"100 Coins", "25":"300 Coins", "26":"1000 Coins", "27":"2000 Coins", "28":"200 Coins", "29":"400 Coins", "30":"5000 Coins", "31":"Jewel", "32":"Skill Booster"}

def items(record):
    string = ""
    if "EXP" in record.items:
        string += "|itemexp15 = true\n"
    if "M+5" in record.items:
        string += "|itemmoves5 = true\n"
    if "T+10" in record.items:
        string += "|itemtime10 = true\n"
    if "DD" in record.items:
        string += "|itemdd = true\n"
    if "MS" in record.items:
        string += "|itemms = true\n"
    if "APU" in record.items:
        string += "|itemapu = true\n"
    if "C-1" in record.items:
        string += "|itemcomp = true\n"
    return string

def disruptions(record):
    disruptionpatterns = []
    string = ""
    dpdata = DisruptionPattern("Configuration Tables/bossActionStageLayout.bin")
    #For each countdown...
    for cdnum in range(3):
        countdown = record.countdowns[cdnum]
        cdindex = countdown["cdindex"]
        #Figure out the countdown rules
        rulesstring = ""
        
        #If countdown initializes counter at 0
        if countdown["cdinitial"] == 1:
            rulesstring += "Start counter at 0. "
        
        #Countdown switch condition
        if countdown["cdswitchcondition"] == 0:
            if countdown["cdswitchvalue"] == 0:
                rulesstring += ""
            else:
                rulesstring += "Switch countdown when [[HP]] <= {} ([[Score]] >= {}). ".format(countdown["cdswitchvalue"], record.hp - countdown["cdswitchvalue"])
        elif countdown["cdswitchcondition"] == 1:
            rulesstring += "Switch countdown after disrupting {} time{}. ".format(countdown["cdswitchvalue"], "s" if countdown["cdswitchvalue"] >= 2 else "")
        elif countdown["cdswitchcondition"] == 2:
            rulesstring += "Switch countdown when Moves <= {}. ".format(countdown["cdswitchvalue"])
        elif countdown["cdswitchcondition"] == 3:
            rulesstring += "Switch countdown after {} move{}. ".format(countdown["cdswitchvalue"], "s" if countdown["cdswitchvalue"] >= 2 else "")
        else:
            rulesstring += "Unknown switch condition: {}. ".format(countdown["cdswitchcondition"])
        
        if cdindex != 0:
            cddisruptionindices = Countdowns.getDisruptions(cdindex)
            #remove empty disruptions
            while cddisruptionindices[-1] == 0:
                cddisruptionindices.pop()
            if len(cddisruptionindices) == 1:
                rulesstring += "INSERTDISRUPTIONHERE "
            #How to choose disruptions
            elif countdown["cddisrupttype"] == 0:
                rulesstring += "Choose one of these disruptions "
            elif countdown["cddisrupttype"] == 1:
                rulesstring += "Do these disruptions in order "
            else:
                rulesstring += "???"
            
            #Combo condition or a timer
            if countdown["cdcombocondition"] != 0:
                rulesstring += "if [[Combo]] {} {}:".format(["wtf", "<=", "=", "<=", "=>"][countdown["cdcombocondition"]], countdown["cdcombothreshold"])
            else:
                if record.timed:
                    rulesstring += "every {} move{}:".format(countdown["cdtimer2"], "s" if countdown["cdtimer2"] >= 2 else "")
                else:
                    rulesstring += "every {} move{}:".format(countdown["cdtimer"], "s" if countdown["cdtimer"] >= 2 else "")
        
        #this means there is nothing in this countdown, and we don't need to print anything
        if rulesstring == "":
            continue
        string += "|cd{} = ".format(cdnum+1) + rulesstring
        
        disruptionstrings = []
        
        if cdindex != 0:
            #Now to figure out the disruptions
            #The countdown index points to a list of up to 8 indices, each pointing to a disruption
            for i in cddisruptionindices:
                disruptionstring = ""
                #a strange edge case...
                if i == 3657:
                    disruptionstring = "Reset the board"
                    disruptionstrings.append(disruptionstring)
                    continue
                
                #get disruption info
                disruption = Disruptions.getDisruptions(i)
                #grab item names
                items = [itemName(j) for j in disruption["indices"]]
                #remove unneeded items
                while (items[-1] == "Nothing" or len(items) > disruption["width"] * disruption["height"]) and len(items) > 1:
                    items.pop()
                
                targetarea = "{}x{}".format(disruption["width"], disruption["height"])
                targettile = "{}{}".format(["A","B","C","D","E","F","G"][disruption["column"]], disruption["row"]+1)
                
                #used for fill tiles randomly disruptions
                dict = {}
                numitems = 0
                for item in items:
                    try:
                        dict[item] += 1
                    except KeyError:
                        dict[item] = 1
                    numitems += 1
                if disruption["value"] == 12:
                    temp = 12
                else:
                    temp = disruption["value"] % 12
                while numitems < temp:
                    dict[items[0]] += 1
                    numitems += 1
                disruptstring = ""
                for key in dict.keys():
                    disruptstring += str(dict[key]) + " {Thumbicon|pokemon=" + key + "}, "
                disruptstring = disruptstring[:-2]
                
                #determine the target area and construct a string
                targetareastring = ""
                if disruption["width"] == 6 and disruption["height"] == 6:
                    targetareastring = "board"
                elif disruption["width"] == 6:
                    targetareastring = "row"
                elif disruption["height"] == 6:
                    targetareastring = "column"
                else:
                    targetareastring = "{} area".format(targetarea)
                
                if targettile == "G7" or targettile == "A1":
                    if targetareastring not in ["board", "row", "column"]:
                        targetareastring = "a random {}".format(targetareastring)
                elif disruption["column"] == 6:
                    if targetareastring not in ["board", "row", "column"]:
                        targetareastring = "a random {} in row {}".format(targetareastring, disruption["row"]+1)
                    else:
                        targetareastring = "a {}".format(targetareastring)
                elif disruption["row"] == 6:
                    if targetareastring not in ["board", "row", "column"]:
                        targetareastring = "a random {} in column {}".format(targetareastring, disruption["column"]+1)
                    else:
                        targetareastring = "a {}".format(targetareastring)
                else:
                    if targetareastring not in ["board", "row", "column"]:
                        targetareastring = "the {} at {}".format(targetareastring, targettile)
                    elif targetareastring == "row":
                        targetareastring = "row {}".format(disruption["row"]+1)
                    elif targetareastring == "column":
                        targetareastring = "column {}".format(disruption["column"]+1)
                
                if disruption["value"] == 25:
                    dpstring = dpdata.patternString(disruption["indices"][0])
                    try:
                        dpindex = disruptionpatterns.index(dpstring)
                        disruptionstring = "Fill board with Disruption Pattern {}".format(dpindex+1)
                    except ValueError:
                        disruptionstring = "Fill board with Disruption Pattern {}".format(len(disruptionpatterns)+1)
                        disruptionpatterns.append(dpstring)
                elif disruption["value"] == 1:
                    #if all the items are the same, no need to create a Disruption Pattern
                    dpstring = DisruptionPatternMini(disruption["width"], disruption["height"], disruption["indices"])
                    items = dpstring.replace("\n", ",").split(",")
                    if items.count(items[0]) == disruption["width"] * disruption["height"]:
                        disruptionstring = "Fill {} with {{Thumbicon|pokemon={}}}".format(targetareastring, items[0])
                    else:
                        disruptionstring = "Fill {} with Disruption Pattern {}".format(targetareastring, len(disruptionpatterns)+1)
                        disruptionpatterns.append(dpstring)
                
                elif disruption["value"] == 0:
                    disruptionstring = "Fill {} with 1 {}".format(targetareastring, "{{Thumbicon|pokemon=" + items[0] + "}}")
                elif disruption["value"] <= 12:
                    disruptionstring = "Fill {} with {}".format(targetareastring, disruptstring)
                elif disruption["value"] <= 24:
                    disruptionstring = "Fill the {} area at {} with {}".format(targetarea, targettile, disruptstring)
                else:
                    disruptionstring = "???"
                
                disruptionstrings.append(disruptionstring)
            
            if len(disruptionstrings) == 1:
                string = string.replace("INSERTDISRUPTIONHERE", disruptionstrings[0])
                string = string[:-1]
            else:
                for j in range(len(disruptionstrings)):
                    if countdown["cddisrupttype"] == 0:
                        string += "\n<div>- {}</div>".format(disruptionstrings[j])
                    elif countdown["cddisrupttype"] == 1:
                        string += "\n<div>{}) {}</div>".format(j+1, disruptionstrings[j])
        string += "\n"
    
    for k in range(len(disruptionpatterns)):
        #need to convert the string to a data structure first...
        disruptionpattern = disruptionpatterns[k]
        if disruptionpattern == "":
            continue
        dpitems = []
        dpstates = []
        lines = disruptionpattern.split("\n")
        for line in lines:
            if line == "":
                continue
            items = line.split(", ")
            rowitems = []
            rowstates = []
            for item in items:
                temp = item.find("[")
                temp2 = item.find("]")
                if temp == -1:
                    rowstates.append("")
                else:
                    state = item[temp+1:temp2]
                    item = item[:temp-1]
                    rowstates.append(state)
                rowitems.append(item)
            dpitems.append(rowitems)
            dpstates.append(rowstates)
        
        #strip off empty rows and columns (easier with numpy)
        dpitems = np.asarray(dpitems)
        dpstates = np.asarray(dpstates)
        testrowitems = dpitems[0]
        testrowstates = dpstates[0]
        while (testrowitems == "Nothing").sum() == len(testrowitems) and (testrowstates == "").sum() == len(testrowstates):
            dpitems = dpitems[1:]
            dpstates = dpstates[1:]
            testrowitems = dpitems[0]
            testrowstates = dpstates[0]
        testrowitems = dpitems[-1]
        testrowstates = dpstates[-1]
        while (testrowitems == "Nothing").sum() == len(testrowitems) and (testrowstates == "").sum() == len(testrowstates):
            dpitems = dpitems[:-1]
            dpstates = dpstates[:-1]
            testrowitems = dpitems[-1]
            testrowstates = dpstates[-1]
        testcolumnitems = dpitems[:,0]
        testcolumnstates = dpstates[:,0]
        while (testcolumnitems == "Nothing").sum() == len(testcolumnitems) and (testcolumnstates == "").sum() == len(testcolumnstates):
            dpitems = dpitems[:,1:]
            dpstates = dpstates[:,1:]
            testcolumnitems = dpitems[:,0]
            testcolumnstates = dpstates[:,0]
        testcolumnitems = dpitems[:,-1]
        testcolumnstates = dpstates[:,-1]
        while (testcolumnitems == "Nothing").sum() == len(testcolumnitems) and (testcolumnstates == "").sum() == len(testcolumnstates):
            dpitems = dpitems[:,:-1]
            dpstates = dpstates[:,:-1]
            testcolumnitems = dpitems[:,-1]
            testcolumnstates = dpstates[:,-1]
        
        #now convert the data structure to wikitext
        itemsstring = ""
        barriersstring = "|barriers="
        blackcloudsstring = "|blackclouds="
        for i in range(len(dpitems)):
            rowitems = dpitems[i]
            rowstates = dpstates[i]
            for j in range(len(rowitems)):
                tile = "{}{}".format(["A","B","C","D","E","F"][j], i+1)
                item = rowitems[j]
                state = rowstates[j]
                
                if item != "Nothing":
                    itemsstring += "|{}={}".format(tile, item)
                if state == "Barrier":
                    barriersstring += "{},".format(tile)
                elif state == "Black Cloud":
                    blackcloudsstring += "{},".format(tile)
        dp = "{{Disruption|width={}|height={}{}{}{}}}".format(len(dpitems[0]), len(dpitems), itemsstring, barriersstring[:-1] if barriersstring != "|barriers=" else "", blackcloudsstring[:-1] if blackcloudsstring != "|blackclouds=" else "")
        string += "|dp{} = {}\n".format(k+1, dp)
    
    string = string.replace("Itself", record.pokemon.fullname)
    string = string.replace("Support #", "Support Pokémon ")
    return string

#parse arguments
appfolder = sys.argv[1]
extfolder = sys.argv[2]
BinStorage.workingdirs["ext"] = os.path.abspath(extfolder)
BinStorage.workingdirs["app"] = os.path.abspath(appfolder)
datatype = sys.argv[3]
index = None
if len(sys.argv) > 4:
    index = int(sys.argv[4])
flag = ""
if len(sys.argv) > 5:
    flag = sys.argv[5]

try:
    if datatype == "stage":
        sdata = StageData("Configuration Tables/stageData.bin")
        ldata = StageLayout("Configuration Tables/stageLayout.bin")
        record = sdata.getStageInfo(index, extra=flag)
    elif datatype == "expertstage":
        sdata = StageData("Configuration Tables/stageDataExtra.bin")
        ldata = StageLayout("Configuration Tables/stageLayoutExtra.bin")
        record = sdata.getStageInfo(index, extra=flag)
    elif datatype == "eventstage":
        sdata = StageData("Configuration Tables/stageDataEvent.bin")
        ldata = StageLayout("Configuration Tables/stageLayoutEvent.bin")
        record = sdata.getStageInfo(index, extra=flag)
    elif datatype == "news":
        messages = BinStorage("Message_US/messageEventStage_US.bin")
    elif datatype == "events":
        sdata = StageData("Configuration Tables/stageDataEvent.bin")
        eventBin = BinStorage("Configuration Tables/eventStage.bin")
    else:
        print "datatype should be one of these: stage, expertstage, eventstage, news, events"
        sys.exit()
except IOError:
    sys.stderr.write("Couldn't find the bin file to extract data from.\n")
    raise

#generate wikitext for board layout
if datatype == "stage" or datatype == "eventstage" or datatype == "expertstage":
    itemlist = []
    itemstatelist = []
    layoutstring = ""
    if record.layoutindex != 0:
        barriers = ""
        blackclouds = ""
        layout, _ = ldata.getLayoutInfo(record.layoutindex)
        for line in range(layout.numlines):
            for item in range(6):
                #get name
                itemvalue = layout.lines[line][item]
                if itemvalue >= 1990:
                    itemname = "Support Pokémon {}".format(itemvalue-1989)
                elif itemvalue >= 1155 or itemvalue > 1995:
                    itemname = "UNKNOWN ({})".format(itemvalue)
                elif itemvalue >= 1151:
                    itemname = ("Rock","Block","Coin")[itemvalue-1152]
                elif itemvalue == 0:
                    itemname = "Random"
                else:
                    itemname = "{}".format(pokemoninfo.PokemonData.getPokemonInfo(itemvalue).fullname)
                
                itemlist.append(itemname)
                
                #get state
                statevalue = layout.linesState[line][item]
                if statevalue == 5:
                    itemState = "Barrier"
                elif statevalue == 4:
                    itemState = "Black Cloud"
                elif statevalue == 3:
                    itemState = ""
                #0 doesn't seem to be anything... probably
                #maybe it's a tutorial marker?
                elif statevalue == 0:
                    itemState = ""
                else:
                    itemState = "UNKNOWN ({})".format(statevalue)
                
                itemstatelist.append(itemState)
                
                if line >= layout.numlines - 6:
                    if itemname != "Random":
                        layoutstring += "|{}{}={}".format(("A","B","C","D","E","F")[item], line%6+1, itemname)
                    if itemState == "Barrier":
                        barriers += "{}{},".format(("A","B","C","D","E","F")[item], line%6+1)
                    if itemState == "Black Cloud":
                        blackclouds += "{}{},".format(("A","B","C","D","E","F")[item], line%6+1)
        if barriers != "":
            layoutstring += "|barriers=" + barriers
            layoutstring = layoutstring[0:len(layoutstring)-1]
        if blackclouds != "":
            layoutstring += "|blackclouds=" + blackclouds
            layoutstring = layoutstring[0:len(layoutstring)-1]
        
        #Generate a layout image
        if flag == "l":
            layoutimagegenerator.generateLayoutImage(itemlist, itemstatelist, "Stage {} - {}".format(record.index, record.pokemon.fullname))

if datatype == "stage":
    if record.index <= 30:
        area = ["Puerto Blanco", "Sandy Bazaar", "Night Festival"][(record.index - 1) // 10]
    elif record.index <= 150:
        area = ["Isla Asul", "Rainbow Park", "Galerie Rouge", "Sweet Strasse", "Silbern Museum", "Mount Vinter", "Castle Noapte", "Jungle Verde"][(record.index - 31) // 15]
    elif record.index <= 240:
        area = ["Wacky Workshop", "Pedra Valley", "Albens Town"][(record.index - 151) // 30]
    elif record.index <= 300:
        area = "Roseus Center"
    else:
        area = ["Desert Umbra", "Violeta Palace", "Blau Salon", "Graucus Hall", "Nacht Carnival", "Prasino Woods", "Zaffiro Coast", "Marron Trail"][(record.index - 301) // 50]
    string = "{{Stage v2\n|name = Stage {}: {}\n|area = {}\n|stage = {}\n|hp = {}\n|moves = {}\n|exp = {}\n".format(record.index, record.pokemon.fullname, area, record.index, record.hp, record.moves, record.exp)
    string += "|basecatch = {}\n|bonuscatch = {}\n|ranks = {}\n|ranka = {}\n|rankb = {}\n|backgroundid = {}\n|soundtrack = {}\n".format(record.basecatch, record.bonuscatch, record.srank, record.arank, record.brank, record.backgroundid, record.soundtrack)
    string += items(record)
    #string += "|coinrewardfirst = {}\n|coinrewardrepeat = {}\n".format(record.coinrewardfirst, record.coinrewardrepeat)
    supports = StageDefaultSupports.getSupportNames(record.defaultsetindex, record.numsupports)
    if record.numsupports == 5:
        addedsupport = supports.pop(0)
        supports.append(addedsupport)
    for i in range(record.numsupports):
        support = supports[i]
        string += "|default{} = {}\n".format(i+1, support)
    if layoutstring != "":
        string += "|boardlayout = {{BoardLayout|imagename=Stage {} - {}}}\n".format(record.index, record.pokemon.fullname)
        string += "|boardlayoutv2 = {{Board".format() + layoutstring + "}}\n".format()
    string += disruptions(record)
    if (record.drop1item != 0 or record.drop2item != 0 or record.drop3item != 0):
        string += "|drop1 = {{Thumbicon|pokemon={}}}\n|drop1chance = {}\n".format(dropitems[str(record.drop1item)], str(1/pow(2,record.drop1rate-1)*100))
        string += "|drop2 = {{Thumbicon|pokemon={}}}\n|drop2chance = {}\n".format(dropitems[str(record.drop2item)], str(1/pow(2,record.drop2rate-1)*100))
        string += "|drop3 = {{Thumbicon|pokemon={}}}\n|drop3chance = {}\n".format(dropitems[str(record.drop3item)], str(1/pow(2,record.drop3rate-1)*100))
    string += "}"
    string = string.replace("{", "{{")
    string = string.replace("}", "}}")
    
    print string

elif datatype == "eventstage":
    hpstring = str(record.hp)
    if record.extrahp != 0:
        hpstring = hpstring + " + {}/level".format(record.extrahp)
    string = "{{Event Stage v4\n|name = AAAAAA: {}\n|area = Special Stages\n|stage = AAAAAA\n|hp = {}\n|{} = {}\n|exp = {}\n".format(record.pokemon.fullname, hpstring, "seconds" if record.timed else "moves", record.seconds if record.timed else record.moves, record.exp)
    string += "|basecatch = {}\n|bonuscatch = {}\n|ranks = {}\n|ranka = {}\n|rankb = {}\n|backgroundid = {}\n|soundtrack = {}\n".format(record.basecatch, record.bonuscatch, record.srank, record.arank, record.brank, record.backgroundid, record.soundtrack)
    string += items(record)
    #string += "|coinrewardfirst = {}\n|coinrewardrepeat = {}\n".format(record.coinrewardfirst, record.coinrewardrepeat)
    supports = StageDefaultSupports.getSupportNames(record.defaultsetindex, record.numsupports)
    if record.numsupports == 5:
        addedsupport = supports.pop(0)
        supports.append(addedsupport)
    for i in range(record.numsupports):
        support = supports[i]
        string += "|default{} = {}\n".format(i+1, support)
    if layoutstring != "":
        string += "|boardlayout = {{BoardLayout|imagename=AAAAAA - {}}}\n".format(record.pokemon.fullname)
        string += "|boardlayoutv2 = {{Board".format() + layoutstring + "}}\n".format()
    string += disruptions(record)
    
    '''
    string += "|duration = <tabber>\n|-|AAAAAA={{EventDetails".format()
    if (record.drop1item != 0 or record.drop2item != 0 or record.drop3item != 0):
        string += "|drop1={{Thumbicon|pokemon={}}}|drop1chance={}".format(dropitems[str(record.drop1item)], str(1/pow(2,record.drop1rate-1)*100))
        string += "|drop2={{Thumbicon|pokemon={}}}|drop2chance={}".format(dropitems[str(record.drop2item)], str(1/pow(2,record.drop2rate-1)*100))
        string += "|drop3={{Thumbicon|pokemon={}}}|drop3chance={}".format(dropitems[str(record.drop3item)], str(1/pow(2,record.drop3rate-1)*100))
    if (record.costtype != 0 or record.attemptcost != 1):
        string += "|cost={} {{Thumbicon|pokemon={}}}".format(record.attemptcost, ["Heart","Coin"][record.costtype])
    string += "}}\n</tabber>\n".format()
    string += "}"
    '''
    
    string += "|ERweeknum = 1\n"
    string += "|ERduration = 7\n"
    
    if (record.drop1item != 0 or record.drop2item != 0 or record.drop3item != 0):
        string += "|drop1 = {{Thumbicon|pokemon={}}}\n".format(dropitems[str(record.drop1item)])
        string += "|drop1chance = {}\n".format(str(1/pow(2,record.drop1rate-1)*100))
        string += "|drop2 = {{Thumbicon|pokemon={}}}\n".format(dropitems[str(record.drop2item)])
        string += "|drop2chance = {}\n".format(str(1/pow(2,record.drop2rate-1)*100))
        string += "|drop3 = {{Thumbicon|pokemon={}}}\n".format(dropitems[str(record.drop3item)])
        string += "|drop3chance = {}\n".format(str(1/pow(2,record.drop3rate-1)*100))
    
    if (record.costtype != 0 or record.attemptcost != 1):
        string += "|cost = {} {{Thumbicon|pokemon={}}}\n".format(record.attemptcost, ["Heart","Coin"][record.costtype])
    
    string += "}"
    
    string = string.replace("{", "{{")
    string = string.replace("}", "}}")
    
    print string

elif datatype == "news":
    for index in range(messages.num_records):
        message = messages.getMessage(index)
        message = message.replace(chr(145), "↑")
        message = message.replace(chr(233), "é")
        
        pokemon = ["Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard", "Squirtle", "Wartortle", "Blastoise", "Pidgey", "Pidgeotto", "Pidgeot", "Espurr", "Meowstic", "Pichu", "Pikachu", "Raichu", "Togepi", "Togetic", "Togekiss", "Bonsly", "Sudowoodo", "Eevee", "Vaporeon", "Jolteon", "Flareon", "Espeon", "Umbreon", "Leafeon", "Glaceon", "Sylveon", "Audino", "Absol", "Purrloin", "Liepard", "Mareep", "Flaaffy", "Ampharos", "Rotom", "Happiny", "Chansey", "Blissey", "Swablu", "Altaria", "Phanpy", "Donphan", "Heracross", "Nidoran(F)", "Nidorina", "Nidoqueen", "Nidoran(M)", "Nidorino", "Nidoking", "Buneary", "Lopunny", "Klefki", "Kangaskhan", "Azurill", "Marill", "Azumarill", "Vulpix", "Ninetales", "Zorua", "Zoroark", "Litwick", "Lampent", "Chandelure", "Chingling", "Chimecho", "Swirlix", "Slurpuff", "Volbeat", "Illumise", "Sableye", "Surskit", "Masquerain", "Riolu", "Lucario", "Taillow", "Swellow", "Slowpoke", "Slowbro", "Slowking", "Meowth", "Persian", "Corsola", "Croagunk", "Toxicroak", "Treecko", "Grovyle", "Sceptile", "Torchic", "Combusken", "Blaziken", "Mudkip", "Marshtomp", "Swampert", "Lapras", "Minccino", "Cinccino", "Vanillite", "Vanillish", "Vanilluxe", "Chatot", "Axew", "Fraxure", "Haxorus", "Hawlucha", "Buizel", "Floatzel", "Mawile", "Gastly", "Haunter", "Gengar", "Cubone", "Marowak", "Dratini", "Dragonair", "Dragonite", "Amaura", "Aurorus", "Mienfoo", "Mienshao", "Snorunt", "Glalie", "Froslass", "Gulpin", "Swalot", "Miltank", "Dedenne", "Cottonee", "Whimsicott", "Petilil", "Lilligant", "Bronzor", "Bronzong", "Emolga", "Scyther", "Scizor", "Carbink", "Throh", "Sawk", "Skarmory", "Delibird", "Stunfisk", "Misdreavus", "Mismagius", "Aerodactyl", "Articuno", "Zapdos", "Moltres", "Raikou", "Entei", "Suicune", "Heatran", "Xerneas", "Yveltal", "Mewtwo", "Mew", "Kyogre", "Groudon", "Rayquaza", "Pachirisu", "Tropius", "Sigilyph", "Farfetch'd", "Druddigon", "Keldeo", "Chespin", "Quilladin", "Chesnaught", "Fennekin", "Braixen", "Delphox", "Froakie", "Frogadier", "Greninja", "Munchlax", "Snorlax", "Onix", "Steelix", "Smeargle", "Larvesta", "Volcarona", "Feebas", "Milotic", "Poochyena", "Mightyena", "Trubbish", "Garbodor", "Hippopotas", "Hippowdon", "Bagon", "Shelgon", "Salamence", "Pancham", "Pangoro", "Yamask", "Cofagrigus", "Solosis", "Duosion", "Reuniclus", "Honedge", "Doublade", "Aegislash", "Drilbur", "Excadrill", "Larvitar", "Pupitar", "Tyranitar", "Shuppet", "Banette", "Rufflet", "Braviary", "Bergmite", "Avalugg", "Snubbull", "Granbull", "Lickitung", "Lickilicky", "Timburr", "Gurdurr", "Conkeldurr", "Tangela", "Tangrowth", "Genesect", "Carvanha", "Sharpedo", "Spinda", "Cherrim", "Cherubi", "Celebi", "Pinsir", "Sneasel", "Weavile", "Regirock", "Regice", "Registeel", "Girafarig", "Kecleon", "Relicanth", "Shuckle", "Spiritomb", "Shaymin", "Victini", "Blitzle", "Zebstrika", "Giratina", "Dialga", "Palkia", "Electrike", "Manectric", "Stantler", "Darumaka", "Darmanitan", "Phione", "Manaphy", "Snivy", "Servine", "Serperior", "Tepig", "Pignite", "Emboar", "Oshawott", "Dewott", "Samurott", "Wynaut", "Wobbuffet", "Torkoal", "Zangoose", "Seviper", "Luvdisc", "Jirachi", "Arceus", "Cresselia", "Furfrou", "Staryu", "Starmie", "Gible", "Gabite", "Garchomp", "Scatterbug", "Spewpa", "Vivillon", "Starly", "Staravia", "Staraptor", "Goomy", "Sliggoo", "Goodra", "Gothita", "Gothorita", "Gothitelle", "Mime Jr.", "Mr. Mime", "Ralts", "Kirlia", "Gardevoir", "Gallade", "Cobalion", "Terrakion", "Virizion", "Darkrai", "Carnivine", "Lugia", "Ho-Oh", "Diancie", "Skitty", "Delcatty", "Klink", "Klang", "Klinklang", "Meditite", "Medicham", "Latias", "Latios", "Zubat", "Golbat", "Crobat", "Pumpkaboo", "Gourgeist", "Duskull", "Dusclops", "Dusknoir", "Grimer", "Muk", "Wingull", "Pelipper", "Bouffalant", "Pawniard", "Bisharp", "Heatmor", "Durant", "Maractus", "Dunsparce", "Qwilfish", "Tornadus", "Thundurus", "Landorus", "Budew", "Roselia", "Roserade", "Machop", "Machoke", "Machamp", "Shinx", "Luxio", "Luxray", "Whismur", "Loudred", "Exploud", "Spritzee", "Aromatisse", "Regigigas", "Deoxys", "Turtwig", "Grotle", "Torterra", "Chimchar", "Monferno", "Infernape", "Piplup", "Prinplup", "Empoleon", "Inkay", "Malamar", "Skiddo", "Gogoat", "Joltik", "Galvantula", "Fletchling", "Fletchinder", "Talonflame", "Numel", "Camerupt", "Roggenrola", "Boldore", "Gigalith", "Rattata", "Raticate", "Snover", "Abomasnow", "Flabébé", "Floette", "Florges", "Munna", "Musharna", "Doduo", "Dodrio", "Alomomola", "Aron", "Lairon", "Aggron", "Chinchou", "Lanturn", "Vullaby", "Mandibuzz", "Porygon", "Porygon2", "Porygon-Z", "Spinarak", "Ariados", "Tympole", "Palpitoad", "Seismitoad", "Nosepass", "Probopass", "Makuhita", "Hariyama", "Igglybuff", "Jigglypuff", "Wigglytuff", "Swinub", "Piloswine", "Mamoswine", "Stunky", "Skuntank", "Gligar", "Gliscor", "Reshiram", "Zekrom", "Kyurem", "Weedle", "Kakuna", "Beedrill", "Sentret", "Furret", "Exeggcute", "Exeggutor", "Finneon", "Lumineon", "Pansage", "Simisage", "Pansear", "Simisear", "Panpour", "Simipour", "Growlithe", "Arcanine", "Magnemite", "Magneton", "Magnezone", "Murkrow", "Honchkrow", "Spheal", "Sealeo", "Walrein", "Skorupi", "Drapion", "Golett", "Golurk", "Tyrunt", "Tyrantrum", "Paras", "Parasect", "Teddiursa", "Ursaring", "Spoink", "Grumpig", "Koffing", "Weezing", "Sandile", "Krokorok", "Krookodile", "Phantump", "Trevenant", "Mankey", "Primeape", "Spearow", "Fearow", "Smoochum", "Jynx", "Omanyte", "Omastar", "Kabuto", "Kabutops", "Magikarp", "Gyarados", "Oddish", "Gloom", "Vileplume", "Bellossom", "Tauros", "Abra", "Kadabra", "Alakazam", "Noibat", "Noivern", "Houndour", "Houndoom", "Pineco", "Forretress", "Hoothoot", "Noctowl", "Uxie", "Mesprit", "Azelf", "Cleffa", "Clefairy", "Clefable", "Deerling", "Sawsbuck", "Zygarde", "Psyduck", "Golduck", "Yanma", "Yanmega", "Lotad", "Lombre", "Ludicolo", "Glameow", "Purugly", "Scraggy", "Scrafty", "Binacle", "Barbaracle", "Elekid", "Electabuzz", "Electivire", "Magby", "Magmar", "Magmortar", "Natu", "Xatu", "Trapinch", "Vibrava", "Flygon", "Shellos", "Gastrodon", "Patrat", "Watchog", "Skrelp", "Dragalge", "Rhyhorn", "Rhydon", "Rhyperior", "Unown", "Clamperl", "Huntail", "Gorebyss", "Cranidos", "Rampardos", "Shieldon", "Bastiodon", "Bunnelby", "Diggersby", "Horsea", "Seadra", "Kingdra", "Slugma", "Magcargo", "Cacnea", "Cacturne", "Combee", "Vespiquen", "Deino", "Zweilous", "Hydreigon", "Lunatone", "Solrock", "Castform", "Mantyke", "Mantine", "Tyrogue", "Hitmonlee", "Hitmonchan", "Hitmontop", "Frillish", "Jellicent", "Drowzee", "Hypno", "Elgyem", "Beheeyem", "Shellder", "Cloyster", "Pidove", "Tranquil", "Unfezant", "Chikorita", "Bayleef", "Meganium", "Cyndaquil", "Quilava", "Typhlosion", "Totodile", "Croconaw", "Feraligatr", "Geodude", "Graveler", "Golem", "Poliwag", "Poliwhirl", "Poliwrath", "Politoed", "Slakoth", "Vigoroth", "Slaking", "Venipede", "Whirlipede", "Scolipede", "Voltorb", "Electrode", "Seel", "Dewgong", "Tynamo", "Eelektrik", "Eelektross", "Hoopa", "Aipom", "Ambipom", "Sewaddle", "Swadloom", "Leavanny", "Shroomish", "Breloom", "Tirtouga", "Carracosta", "Archen", "Archeops", "Wailmer", "Wailord", "Burmy", "Wormadam", "Mothim", "Bidoof", "Bibarel", "Ferroseed", "Ferrothorn", "Baltoy", "Claydol", "Helioptile", "Heliolisk", "Nincada", "Ninjask", "Shedinja", "Seedot", "Nuzleaf", "Shiftry", "Beldum", "Metang", "Metagross", "Drifloon", "Drifblim", "Sunkern", "Sunflora", "Meloetta", "Lillipup", "Herdier", "Stoutland", "Cubchoo", "Beartic", "Bellsprout", "Weepinbell", "Victreebel", "Hoppip", "Skiploom", "Jumpluff", "Lileep", "Cradily", "Anorith", "Armaldo", "Litleo", "Pyroar", "Corphish", "Crawdaunt", "Karrablast", "Escavalier", "Shelmet", "Accelgor", "Woobat", "Swoobat", "Foongus", "Amoongus", "Ledyba", "Ledian", "Tentacool", "Tentacruel", "Zigzagoon", "Linoone", "Sandshrew", "Sandslash", "Barboach", "Whiscash", "Volcanion", "Plusle", "Minun", "Goldeen", "Seaking", "Krabby", "Kingler", "Ponyta", "Rapidash", "Ekans", "Arbok", "Ducklett", "Swanna", "Clauncher", "Clawitzer", "Wurmple", "Silcoon", "Beautifly", "Cascoon", "Dustox", "Diglett", "Dugtrio", "Ditto", "Rowlet", "Dartrix", "Decidueye", "Litten", "Torracat", "Incineroar", "Popplio", "Brionne", "Primarina", "Oricorio", "Fomantis", "Lurantis", "Wishiwashi", "Komala", "Oranguru", "Passimian", "Salandit", "Salazzle", "Togedemaru", "Mimikyu", "Dewpider", "Araquanid", "Rockruff", "Lycanroc", "Cosmog", "Cosmoem", "Solgaleo", "Lunala", "Magearna", "Mudbray", "Mudsdale", "Pyukumuku", "Grubbin", "Charjabug", "Vikavolt", "Crabrawler", "Crabominable", "Bounsweet", "Steenee", "Tsareena", "Caterpie", "Metapod", "Butterfree", "Venonat", "Venomoth", "Remoraid", "Octillery", "Dwebble", "Crustle", "Basculin", "Tapu Koko", "Tapu Lele", "Tapu Bulu", "Tapu Fini", "Kricketot", "Kricketune", "Cryogonal", "Pikipek", "Trumbeak", "Toucannon", "Drampa", "Nihilego", "Buzzwole", "Pheromosa", "Xurkitree", "Celesteela", "Kartana", "Guzzlord", "Type: Null", "Silvally"]
        keywords = ["Jewel", "Enhancement", "Enhancements", "Coin", "Heart", "Mega Speedup", "Raise Max Level", "Level Up", "Mega Start", "Attack Power ↑", "Disruption Delay", "Exp. Points x1.5", "Moves +5", "Time +10", "Complexity -1", "Exp. Booster S", "Exp. Booster M", "Exp. Booster L", "Skill Booster S", "Skill Booster M", "Skill Booster L", "Skill Swapper", "Escalation Battles", "Daily Pokénmon", "Pokénmon Safari", "Competitive Stage", "Main Stages", "Expert Stages", "Special Stages", "type", "Optimize", "Start-of-Month Challenge", "Mid-month_Challenge"]
        keywords = keywords + pokemon
        dict = {}
        for keyword in keywords:
            index = message.find(keyword)
            if index != -1 and dict.keys().count(keyword) != 1:
                message = message.replace(keyword, "[[" + keyword + "]]", 1)
                dict[keyword] = 1
        
        splitindex = message.find("\n\n")
        if splitindex == -1:
            continue
        desc1 = message[0:splitindex]
        desc2 = message[splitindex+2:]
        
        string = "{{3DSNews\n|title = AAAAAA\n|icon = AAAAAA\n|color = {{NoticeColor|type=AAAAAA}}\n|desc1 = {}\n|desc2 = {}\n}}".format(desc1, desc2)
        string = string.replace("{", "{{")
        string = string.replace("}", "}}")
        
        print string
        print
        print


if datatype == "expertstage":
    string = "{{Expert Stage\n|name = Stage EX{}: {}\n|area = Expert Stages\n|EXstage = {}\n|sranksrequired = \n|hp = {}\n|seconds = {}\n|exp = {}\n".format(record.index+1, record.pokemon.fullname, record.index+1, record.hp, record.seconds, record.exp)
    string += "|basecatch = {}\n|bonuscatch = {}\n|ranks = {}\n|ranka = {}\n|rankb = {}\n|backgroundid = {}\n|soundtrack = {}\n".format(record.basecatch, record.bonuscatch, record.srank, record.arank, record.brank, record.backgroundid, record.soundtrack)
    string += items(record)
    #string += "|coinrewardfirst = {}\n|coinrewardrepeat = {}\n".format(record.coinrewardfirst, record.coinrewardrepeat)
    supports = StageDefaultSupports.getSupportNames(record.defaultsetindex, record.numsupports)
    if record.numsupports == 5:
        addedsupport = supports.pop(0)
        supports.append(addedsupport)
    for i in range(record.numsupports):
        support = supports[i]
        string += "|default{} = {}\n".format(i+1, support)
    if layoutstring != "":
        string += "|boardlayout = {{BoardLayout|imagename=Stage EX{} - {}}}\n".format(record.index+1, record.pokemon.fullname)
        string += "|boardlayoutv2 = {{Board".format() + layoutstring + "}}\n".format()
    string += disruptions(record)
    if (record.drop1item != 0 or record.drop2item != 0 or record.drop3item != 0):
        string += "|drop1 = {{Thumbicon|pokemon={}}}\n|drop1chance = {}\n".format(dropitems[str(record.drop1item)], str(1/pow(2,record.drop1rate-1)*100))
        string += "|drop2 = {{Thumbicon|pokemon={}}}\n|drop2chance = {}\n".format(dropitems[str(record.drop2item)], str(1/pow(2,record.drop2rate-1)*100))
        string += "|drop3 = {{Thumbicon|pokemon={}}}\n|drop3chance = {}\n".format(dropitems[str(record.drop3item)], str(1/pow(2,record.drop3rate-1)*100))
    string += "}"
    string = string.replace("{", "{{")
    string = string.replace("}", "}}")
    
    print string

elif datatype == "events":
    for i in range(eventBin.num_records):
        snippet = eventBin.getRecord(i)
        record = EventDetails(i, snippet, sdata, flag)
        
        string = "|-\n|"
        
        string += ["", "{} Appears".format(record.stagepokemon), "Daily Pokémon Are Here!", "", "A Chance for Coins!", "Competitive Stage Now Live!", "Take on Escalation Battles", "Head Back into the Safari!", "{} Appears".format(record.stagepokemon)][record.stagetype]
        if record.stagetype != 2 and record.stagetype != 7:
            string += " {{Thumbicon|pokemon={}}}".format(record.stagepokemon)
        string += "\n|"
        
        #datetime stuff
        starttime = datetime.datetime(record.startyear + 2000, record.startmonth, record.startday, record.starthour, record.startminute)
        starttimestring = starttime.strftime("%m/%d/%y")
        endtime = datetime.datetime(record.endyear + 2000, record.endmonth, record.endday, record.endhour, record.endminute) - datetime.timedelta(1)
        endtimestring = endtime.strftime("%m/%d/%y")
        
        string += "{} to {}\n|".format(starttimestring, endtimestring)
        string += "[["
        string += ["", "Great Challenge", "Daily Pokémon", "", "Meowth's Coin Mania", "Competitive Stage", "Escalation Battles", "Pokémon Safari", "Try 'Em Items Stage"][record.stagetype]
        string += "]]\n|"
        
        #daily pokemon
        if record.stagetype == 2:
            record.stage = record.stages[0]
            string += "<div>Daily #? Pokémon:</div>\n"
            for i in range(len(record.stagepokemon)):
                day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][i]
                pokemon = record.stagepokemon[i]
                string += "<div>{}: {{Thumbicon|pokemon={}}} [[{}]]</div>\n".format(day, pokemon, pokemon)
        
        #comp rewards
        if record.stagetype == 5:
            string += "{Competition Rewards\n|rewards=\n{Thumbicon|pokemon=MEGASTONE} + 5 {Thumbicon|pokemon=Mega Speedup} + 15 {Thumbicon|pokemon=Raise Max Level},\n{Thumbicon|pokemon=MEGASTONE} + 4 {Thumbicon|pokemon=Mega Speedup} + 10 {Thumbicon|pokemon=Raise Max Level},\n{Thumbicon|pokemon=MEGASTONE} + 4 {Thumbicon|pokemon=Mega Speedup} + 6 {Thumbicon|pokemon=Raise Max Level},\n{Thumbicon|pokemon=MEGASTONE} + 3 {Thumbicon|pokemon=Mega Speedup} + 4 {Thumbicon|pokemon=Raise Max Level},\n{Thumbicon|pokemon=MEGASTONE} + 3 {Thumbicon|pokemon=Mega Speedup} + 2 {Thumbicon|pokemon=Raise Max Level},\n{Thumbicon|pokemon=MEGASTONE} + 2 {Thumbicon|pokemon=Mega Speedup} + {Thumbicon|pokemon=Raise Max Level},\n{Thumbicon|pokemon=MEGASTONE} + {Thumbicon|pokemon=Mega Speedup} + {Thumbicon|pokemon=Raise Max Level},\n{Thumbicon|pokemon=MEGASTONE} + {Thumbicon|pokemon=Mega Speedup} + {Thumbicon|pokemon=Mega Start},\n{Thumbicon|pokemon=MEGASTONE} + {Thumbicon|pokemon=Mega Start} + {Thumbicon|pokemon=Moves +5},\n{Thumbicon|pokemon=Attack Power ↑} + {Thumbicon|pokemon=Moves +5} + 3000 {Thumbicon|pokemon=Coin},\n{Thumbicon|pokemon=Attack Power ↑} + 3000 {Thumbicon|pokemon=Coin},\n3000 {Thumbicon|pokemon=Coin}\n|3dsna=1-100, 101-300, 301-600, 601-1000, 1001-2100, 2101-3600, 3601-5200, 5201-7800, 7801-10400, 10401-13000, 13001-16800, 16801+\n|3dseu=1-100, 101-200, 201-500, 501-700, 701-1500, 1501-2600, 2601-3700, 3701-5600, 5601-7400, 7400-9300, 9301-12100, 12101+\n|3dsjp=1-300, 301-1000, 1001-2500, 2501-4000, 4001-8000, 8001-14000, 14001-20000, 20001-30000, 30001-40000, 40001-50000, 50001-65000, 65001+\n|mobile=1-600, 601-2000, 2001-5000, 5001-8000, 8001-16000, 16001-28000, 28000-40000, 40001-60000, 60001-80000, 80001-100000, 100001-130000, 130001+\n}\n<div>{Thumbicon|pokemon=MEGASTONE} already owned: {Thumbicon|pokemon=Level Up}</div>"
        
        #eb rewards
        if record.stagetype == 6:
            EBrewardsBin = BinStorage("Configuration Tables/stagePrizeEventLevel.bin")
            ebrewards = EscalationRewards(EBrewardsBin)
            for e in ebrewards.entries:
                string += "<div>Level {}: {}{{Thumbicon|pokemon={}}}</div>\n".format(e["level"], str(e["itemamount"]) + " " if e["itemamount"] > 1 else "", e["item"])
        
        #safari
        if record.stagetype == 7:
            string += "Safari #? Pokémon and encounter rates</div>\n"
            totalvalue = sum(record.extravalues)
            for i in range(len(record.stages)):
                stage = record.stages[i]
                string += "<div>{{Thumbicon|pokemon={}}} [[{}]] - {:0.2f}%</div>\n".format(stage.pokemon.fullname, stage.pokemon.fullname, float(record.extravalues[i] * 100) / totalvalue)
        
        #attempt cost
        if record.stage.costtype != 0 or record.stage.attemptcost != 1:
            string += "<div>Costs {} {{Thumbicon|pokemon={}}} per attempt</div>\n".format(record.stage.attemptcost, ["Heart", "Coin"][record.stage.costtype])
        
        #drop rates
        if record.stage.drop1item != 0 and record.stagetype != 6:
            try:
                drop1item = dropitems[str(record.stage.drop1item)]
            except KeyError:
                drop1item = str(record.stage.drop1item)
            try:
                drop2item = dropitems[str(record.stage.drop2item)]
            except KeyError:
                drop2item = str(record.stage.drop2item)
            try:
                drop3item = dropitems[str(record.stage.drop3item)]
            except KeyError:
                drop3item = str(record.stage.drop3item)
            string += "<div>[[Drops]]: {{Thumbicon|pokemon={}}} {}% / {{Thumbicon|pokemon={}}} {}% / {{Thumbicon|pokemon={}}} {}%</div>\n".format(drop1item, str(1/pow(2,record.stage.drop1rate-1)*100), drop2item, str(1/pow(2,record.stage.drop2rate-1)*100), drop3item, str(1/pow(2,record.stage.drop3rate-1)*100))
        
        #unlock costs
        if record.unlockcost != 0 and record.stagetype != 7:
            string += "<div>Stage costs {} {}{} to unlock {} time{}.".format(record.unlockcost, ["{Thumbicon|pokemon=Coin}","{Thumbicon|pokemon=Jewel}"][record.unlockcosttype], "s" if record.unlockcost > 1 else "", record.unlocktimes, "s" if record.unlocktimes > 1 else "")
        if record.triesavailable != 0 and record.stagetype != 7:
            string += " Stage is available to attempt {} time{} before it disappears</div>".format(record.triesavailable, "s" if record.triesavailable > 1 else "")
        
        if string[-1] == "\n":
            string = string[:-1]
        
        string = string.replace("{", "{{")
        string = string.replace("}", "}}")
        
        print string