#!/usr/bin/python
from __future__ import division

import sys
from struct import unpack
from bindata import *
import pokemoninfo as PI
import layoutimagegenerator

dropitems = {"1":"RML", "2":"LU", "3":"EBS", "4":"EBM", "5":"EBL", "6":"SBS", "7":"SBM", "8":"SBL", "9":"SS", "10":"MSU", "23":"10 Hearts", "24":"100 Coins", "25":"300 Coins", "27":"2000 Coins", "30":"5000 Coins", "32":"PSB"}
soundtracks = {"17":"bgm-stage-tutorial", "18":"bgm-stage-easy", "19":"bgm-stage-normal", "20":"bgm-stage-hard", "21":"bgm-stage-rare", "22":"bgm-stage-legend", "23":"bgm-stage-boss1", "24":"bgm-stage-boss2", "25":"bgm-stage-ex", "26":"bgm-stage-fun", "27":"bgm-stage-ranking", "29":"bgm-gettime"}

def binary(str):
    ans = str
    while len(ans) != 8:
        ans = "0" + ans
    return ans

def itemName(index):
    if index >= 2205:
        return "UNKNOWN ({})".format(index)
    elif index >= 2200:
        return "{}".format(("Rock","Block","Coin","Black Cloud","Barrier")[index-2200])
    elif index >= 2100 and index <= 2105:
        return "Support #{}".format(index-2099)
    elif index == 2000:
        return "Itself"
    elif index >= 1990 and index <= 1995:
        return "Support #{}".format(index-1989)
    elif index >= 1155 or index > 1995:
        return "UNKNOWN ({})".format(index)
    elif index >= 1151:
        return "{}".format(("Rock","Block","Coin")[index-1152])
    elif index == 0:
        return "Nothing"
    else:
        return "{}".format(PI.PokemonData.getPokemonInfo(index).fullname)

class StageLayoutRecord:
    def __init__(self,index,binary):
        
        firstLine = binary.getRecord(index)
        blocks = readbits(firstLine, 0, 0, 4)
        
        if blocks == 0:
            sys.stderr.write("The listed layout index ({}) has broken header data and may not be the start of a stage. Assuming it's a 1-block stage.\n".format(index))
            blocks = 1
            #raise IndexError
        
        self.numlines = blocks*6
        self.index = index
        
        self.lines = [None for x in range(self.numlines)]
        self.linesState = [None for x in range(self.numlines)]
        self.linesMisc = [None for x in range(self.numlines)]
        self.binLines = [None for x in range(self.numlines)]
        
        linePointer = self.numlines - 6
        
        for line in range(index,index+self.numlines):
            thisLine = binary.getRecord(line)
            self.binLines[linePointer] = thisLine
            #now decode the line
            self.lines[linePointer] = [readbits(thisLine, 0, 4, 11), readbits(thisLine, 2, 2, 11), readbits(thisLine, 4, 0, 11), readbits(thisLine, 5, 6, 11), readbits(thisLine, 8, 0, 11), readbits(thisLine, 9, 6, 11)]
            self.linesState[linePointer] = [readbits(thisLine, 1, 7, 3), readbits(thisLine, 3, 5, 3), readbits(thisLine, 5, 3, 3), readbits(thisLine, 7, 1, 3), readbits(thisLine, 9, 3, 3), readbits(thisLine, 11, 1, 3)]
            self.linesMisc[linePointer] = [readbits(thisLine, 7, 4, 4), readbits(thisLine, 11, 4, 4)]
            
            #ensure correct ordering
            linePointer += 1
            if linePointer % 6 == 0:
                linePointer -= 12
        
        if binary.num_records <= index+self.numlines:
            self.nextIndex = None
        else:
            self.nextIndex = index+self.numlines
    
class StageLayout:
    databin = None
    records = {}
    
    def __init__(self,layout_file):
        self.databin = BinStorage(layout_file)
        
    def getLayoutInfo(self, index):
        if index not in self.records.keys():
            self.records[index] = StageLayoutRecord(index, self.databin)
        #returns (info, nextLayout) - second can be None.
        return self.records[index], self.records[index].nextIndex
        
    def printdata(self, index, thisLayout=None, generatelayoutimage=False):
        itemlist = []
        itemstatelist = []

        if thisLayout is None:
            thisLayout, _ = self.getLayoutInfo(index)
        print "Layout Index {}:".format(index)
        for line in range(thisLayout.numlines):
            if line == thisLayout.numlines - 6 and line != 0:
                print "=========================================================" #divide skyfall from board
            lineString = ""
            for item in range(6):
                #get name
                itemvalue = thisLayout.lines[line][item]
                if itemvalue >= 1990:
                    itemName = "Support #{}".format(itemvalue-1989)
                elif itemvalue >= 1155 or itemvalue > 1995:
                    itemName = "UNKNOWN ({})".format(itemvalue)
                elif itemvalue >= 1151:
                    itemName = "{}".format(("Rock","Block","Coin")[itemvalue-1152])
                elif itemvalue == 0:
                    itemName = "Random"
                else:
                    itemName = "{}".format(PI.PokemonData.getPokemonInfo(itemvalue).fullname)
                
                itemlist.append(itemName)
            
                #get state
                statevalue = thisLayout.linesState[line][item]
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
            
                lineString += "{}{}{}".format(itemName, " [" + itemState + "]" if itemState != "" else "", ", " if item < 5 else "")
            
            #This apparently never triggers - maybe those two values are filler?
            if thisLayout.linesMisc[line][0] != 0 or thisLayout.linesMisc[line][1] != 0:
                lineString += " + ({},{})".format(thisLayout.linesMisc[line][0],thisLayout.linesMisc[line][1])
            print lineString
        print
        #Generate a layout image
        if generatelayoutimage == "l":
            layoutimagegenerator.generateLayoutImage(itemlist, itemstatelist, "Layout Index {}".format(index))
    
    #Python 32-bit seems to run out of memory after generating about 4 or so layout images
    def printalldata(self, generatelayoutimage=False):
        nextLayout = 1
        while nextLayout is not None:
            try:
                thisLayout, nextLayout = self.getLayoutInfo(nextLayout)
                self.printdata(thisLayout.index, thisLayout, generatelayoutimage=generatelayoutimage)
            except IndexError:
                nextLayout += 6 #skip to the next one
        
    def printLayoutBinary(self,index):
        thisLayout, _ = self.getLayoutInfo(index)
        for line in thisLayout.binLines:
            print line

class DisruptionPatternRecord:
    def __init__(self, index, binary):
        firstLine = binary.getRecord(index)
        
        self.index = index
        
        #disruption patterns are always 6 lines
        self.lines = [None for x in range(6)]
        self.linesState = [None for x in range(6)]
        
        for linenumber in range(6):
            thisLine = binary.getRecord(index + linenumber)
            
            self.lines[linenumber] = [readbits(thisLine, 0, 0, 12), readbits(thisLine, 2, 0, 12), readbits(thisLine, 4, 0, 12), readbits(thisLine, 6, 0, 12), readbits(thisLine, 8, 0, 12), readbits(thisLine, 10, 0, 12)]
            self.linesState[linenumber] = [readbits(thisLine, 1, 6, 2), readbits(thisLine, 3, 6, 2), readbits(thisLine, 5, 6, 2), readbits(thisLine, 7, 6, 2), readbits(thisLine, 9, 6, 2), readbits(thisLine, 11, 6, 2)]

class DisruptionPattern:
    databin = None
    records = {}
    
    def __init__(self, layout_file):
        self.databin = BinStorage(layout_file)
        
    def getLayoutInfo(self, index):
        if index not in self.records.keys():
            self.records[index] = DisruptionPatternRecord(index, self.databin)
        return self.records[index]
    
    def patternString(self, index):
        string = ""
        
        thisLayout = self.getLayoutInfo(index)
        for line in range(6):
            lineString = ""
            for item in range(6):
                #get name
                itemvalue = thisLayout.lines[line][item]
                itemname = itemName(itemvalue)
            
                #get state
                statevalue = thisLayout.linesState[line][item]
                if statevalue > 3:
                    itemState = "UNKNOWN ({})".format(statevalue)
                else:
                    itemState = ["", "Clear", "Black Cloud", "Barrier"][statevalue]
                
                lineString += "{}{}{}".format(itemname, " [" + itemState + "]" if itemState != "" else "", ", " if item < 5 else "")
            string += lineString + "\n"
        return string

def DisruptionPatternMini(width, height, list):
    string = ""
    for i in range(height):
        for j in range(width):
            index = (i * width) + j
            try:
                itemname = itemName(list[index])
                string += "{}{}".format(itemname, ", " if j < width-1 else "")
            except IndexError:
                string += "Nothing{}".format(", " if j < width-1 else "")
        string += "\n"
    string = string[:-1]
    return string

class StageDataRecord:
    def __init__(self,index,snippet,extra=False):
        self.binary = snippet
        self.index = index
        
        #parse!
        self.pokemonindex = readbits(snippet, 0, 0, 10)
        self.megapokemon = readbits(snippet, 1, 2, 1) #determines if the pokemon is a mega pokemon
        self.mystery = readbits(snippet, 1, 3, 3)
        self.numsupports = readbits(snippet, 1, 6, 4)
        self.timed = readbits(snippet, 2, 2, 1)
        self.seconds = readbits(snippet, 2, 3, 8)
        self.hp = readbits(snippet, 4, 0, 20)
        self.costtype = readbits(snippet, 7, 0, 8) #0 is hearts, 1 is coins
        self.attemptcost = readbits(snippet, 8, 0, 16)
        
        self.countdowns = [{} for i in range(3)]
        for i in range(3):
            self.countdowns[i]["cdswitchvalue"] = readbits(snippet, (12*i)+12, 0, 16) #threshold to switch countdowns (depending on switch condition)
            self.countdowns[i]["cdtimer"] = readbits(snippet, (12*i)+15, 0, 4) #moves to trigger disruption
            self.countdowns[i]["cdinitial"] = readbits(snippet, (12*i)+17, 2, 1) #if the countdown starts its timer at 0
            self.countdowns[i]["cdcombocondition"] = readbits(snippet, (12*i)+17, 3, 3) #1 means <=, 2 means =, 4 means >=
            self.countdowns[i]["cdcombothreshold"] = readbits(snippet, (12*i)+17, 6, 4) #combo value
            self.countdowns[i]["cddisrupttype"] = readbits(snippet, (12*i)+19, 0, 1) #0 means random, 1 means sequential
            self.countdowns[i]["cdindex"] = readbits(snippet, (12*i)+20, 0, 16) #disruption index
            self.countdowns[i]["cdswitchcondition"] = readbits(snippet, (12*i)+22, 0, 2) #0 means HP, 1 means disrupt times, 2 means moves
        
        self.srank = readbits(snippet, 48, 2, 10)
        self.arank = readbits(snippet, 49, 4, 10)
        self.brank = readbits(snippet, 50, 6, 10)
        self.basecatch = readbits(snippet, 52, 0, 7)
        self.bonuscatch = readbits(snippet, 52, 7, 7)
        self.coinrewardrepeat = readbits(snippet, 56, 7, 16)
        self.coinrewardfirst = readbits(snippet, 60, 0, 16)
        self.exp = readbits(snippet, 64, 0, 16)
        self.drop1item = readbits(snippet, 67, 0, 8)
        self.drop1rate = readbits(snippet, 68, 0, 4)
        self.drop2item = readbits(snippet, 68, 4, 8)
        self.drop2rate = readbits(snippet, 69, 4, 4)
        self.drop3item = readbits(snippet, 70, 0, 8)
        self.drop3rate = readbits(snippet, 71, 0, 4)
        self.trackid = readbits(snippet, 72, 3, 10)
        self.difficulty = readbits(snippet, 73, 5, 3)
        self.itemsetid = readbits(snippet, 78, 2, 6)
        self.extrahp = readbits(snippet, 80, 0, 16)
        self.layoutindex = readbits(snippet, 82, 0, 16) #layout = stage layout data. starting board.
        self.defaultsetindex = readbits(snippet, 84, 0, 16) #default supports - i.e. what's in the skyfall 
        self.moves = readbits(snippet, 86, 0, 8)
        self.backgroundid = readbits(snippet, 88, 2, 8)
        
        #Some values in Mobile are located at different places...
        if extra == "m" or extra == "md":
            self.costtype = readbits(snippet, 9, 0, 8) #0 is hearts, 1 is coins
            self.attemptcost = readbits(snippet, 10, 0, 16)
            self.basecatch = readfloat(snippet, 52)
            self.bonuscatch = readbits(snippet, 56, 0, 7)
            self.coinrewardrepeat = readbits(snippet, 60, 0, 14)
            self.coinrewardfirst = readbits(snippet, 61, 6, 14)
            self.trackid = readbits(snippet, 74, 0, 10)
            self.difficulty = readbits(snippet, 76, 0, 3)
            self.itemsetid = readbits(snippet, 80, 0, 6)
            self.extrahp = readbits(snippet, 84, 0, 16)
            self.layoutindex = readbits(snippet, 86, 0, 16)
            self.defaultsetindex = readbits(snippet, 88, 0, 16)
            self.moves = readbits(snippet, 90, 0, 8)
            self.backgroundid = readbits(snippet, 93, 0, 8) - 1
        
        #determine a few values
        if self.megapokemon == 1:
            self.pokemonindex += 1024
        self.pokemon = PI.PokemonData.getPokemonInfo(self.pokemonindex)
        
        try:
            self.soundtrack = soundtracks[str(self.trackid)]
        except KeyError:
            self.soundtrack = "Unknown (Track ID {})".format(self.trackid)
        
        if self.basecatch == int(self.basecatch):
            self.basecatch = int(self.basecatch)
        
        self.items = ItemSet.getItems(self.itemsetid)

class StageData:
    databin = None
    records = []
    
    def __init__(self,stage_file):
        self.databin = BinStorage(stage_file)
        self.records = [None for item in range(self.databin.num_records)]
    
    def getStageInfo(self, index, extra=False):
        if self.records[index] is None:
            self.records[index] = StageDataRecord(index, self.databin.getRecord(index), extra=extra)
        return self.records[index]
    
    def printdata(self, index, extra=False):
        record = self.getStageInfo(index, extra)
    
        print "Stage Index " + str(record.index)
        
        pokemonfullname = record.pokemon.name
        if (record.pokemon.modifier != ""):
            pokemonfullname += " (" + record.pokemon.modifier + ")"
        print "Pokemon: " + pokemonfullname + " (index {})".format(record.pokemonindex)
        
        hpstring = "HP: " + str(record.hp)
        if (record.extrahp != 0):
            hpstring += " + " + str(record.extrahp)
        print hpstring
        if (record.timed == 0):
            print "Moves: " + str(record.moves)
        else:
            print "Seconds: " + str(record.seconds)
        print "Experience: " + str(record.exp)
        
        if (record.timed == 0):
            print "Catchability: " + str(record.basecatch) + "% + " + str(record.bonuscatch) + "%/move"
        else:
            print "Catchability: " + str(record.basecatch) + "% + " + str(record.bonuscatch) + "%/3sec"
        
        print "# of Support Pokemon: " + str(record.numsupports)
        print "Default Supports: "+", ".join(StageDefaultSupports.getSupportNames(record.defaultsetindex, record.numsupports))
        print "Pika-Difficulty: "+str(record.difficulty)
        print "Rank Requirements: " + str(record.srank) + " / " + str(record.arank) + " / " + str(record.brank)
        
        print "Coin reward (first clear): " + str(record.coinrewardfirst)
        print "Coin reward (repeat clear): " + str(record.coinrewardrepeat)
        print "Background ID: " + str(record.backgroundid)
        print "Soundtrack: " + record.soundtrack
        print "Layout Index: " + str(record.layoutindex)
        
        print "Cost to play the stage: {} {}{}".format(record.attemptcost, ["Heart","Coin"][record.costtype], "s" if record.attemptcost != 1 else "")
        
        if (record.drop1item != 0 or record.drop2item != 0 or record.drop3item != 0):
            try:
                drop1item = dropitems[str(record.drop1item)]
            except KeyError:
                drop1item = str(record.drop1item)
            try:
                drop2item = dropitems[str(record.drop2item)]
            except KeyError:
                drop2item = str(record.drop2item)
            try:
                drop3item = dropitems[str(record.drop3item)]
            except KeyError:
                drop3item = str(record.drop3item)
            print "Drop Items: " + drop1item + " / " + drop2item + " / " + drop3item
            print "Drop Rates: " + str(1/pow(2,record.drop1rate-1)) + " / " + str(1/pow(2,record.drop2rate-1)) + " / " + str(1/pow(2,record.drop3rate-1))
        
        print "Items Available: " + ", ".join(record.items)
        
        #for now, only print disruption data if there is a flag "d"
        if extra != "d" and extra != "md":
            return
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
                    rulesstring += "Switch countdown when HP <= {}. ".format(countdown["cdswitchvalue"])
            elif countdown["cdswitchcondition"] == 1:
                rulesstring += "Switch countdown after disrupting {} time{}. ".format(countdown["cdswitchvalue"], "s" if countdown["cdswitchvalue"] >= 2 else "")
            elif countdown["cdswitchcondition"] == 2:
                rulesstring += "Switch countdown when Moves <= {}. ".format(countdown["cdswitchvalue"])
            elif countdown["cdswitchcondition"] == 3:
                rulesstring += "Switch countdown after {} move{}. ".format(countdown["cdswitchvalue"], "s" if countdown["cdswitchvalue"] >= 2 else "")
            else:
                rulesstring += "Unknown switch condition: {}. ".format(countdown["cdswitchcondition"])
            
            if cdindex != 0:
                #How to choose disruptions
                if countdown["cddisrupttype"] == 0:
                    rulesstring += "Choose one of these disruptions "
                elif countdown["cddisrupttype"] == 1:
                    rulesstring += "Do these disruptions in order "
                else:
                    rulesstring += "???"
                
                #Combo condition or a timer
                if countdown["cdcombocondition"] != 0:
                    rulesstring += "if Combo {} {}:".format(["wtf", "<=", "=", "<=", ">="][countdown["cdcombocondition"]], countdown["cdcombothreshold"])
                else:
                    rulesstring += "every {} move{}:".format(countdown["cdtimer"], "s" if countdown["cdtimer"] >= 2 else "")
            
            #this means there is nothing in this countdown, and we don't need to print anything
            if rulesstring == "":
                continue
            
            print
            print "=== Countdown {} Index {} ===".format(cdnum+1, cdindex)
            print rulesstring
            
            if cdindex != 0:
                #Now to figure out the disruptions
                #The countdown index points to a list of up to 8 indices, each pointing to a disruption
                cddisruptionindices = Countdowns.getDisruptions(cdindex)
                for i in cddisruptionindices:
                    #skip empty disruptions
                    if i == 0:
                        continue
                    #a strange edge case...
                    elif i == 3657:
                        print "** Disruption Index {}: Reset the board".format(i)
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
                    print "** Disruption Index {}".format(i)
                    
                    dict = {}
                    numitems = 0
                    for item in items:
                        try:
                            dict[item] += 1
                        except KeyError:
                            dict[item] = 1
                        numitems += 1
                    
                    if disruption["type"] == 3:
                        print "Disruption Pattern Index {}:\n".format(index) + dpdata.patternString(disruption["indices"][0])
                    elif disruption["type"] == 0:
                        if disruption["value"] == 1:
                            print "Fill the {} area at {} with this:".format(targetarea, targettile)
                            print DisruptionPatternMini(disruption["width"], disruption["height"], disruption["indices"]).replace("Itself", pokemonfullname)
                        elif len(items) == 1:
                            if targettile == "A1":
                                print "Fill a random {} area with {} {}".format(targetarea, disruption["value"], items[0]).replace("Itself", pokemonfullname)
                            else:
                                print "Fill the {} area at {} with {} {}".format(targetarea, targettile, disruption["value"], items[0]).replace("Itself", pokemonfullname)
                        else:
                            dict[items[0]] += disruption["value"] - numitems
                            disruptstring = ""
                            for key in dict.keys():
                                disruptstring += str(dict[key]) + " " + key + ", "
                            disruptstring = disruptstring[:-2].replace("Itself", pokemonfullname)
                            print "Fill the {} area at {} with {}".format(targetarea, targettile, disruptstring)
                    elif disruption["type"] == 1 or disruption["type"] == 2:
                        dict[items[0]] = disruption["value"]
                        disruptstring = ""
                        for key in dict.keys():
                            disruptstring += str(dict[key]) + " " + key + ", "
                        disruptstring = disruptstring[:-2].replace("Itself", pokemonfullname)
                        print "Fill the {} area at {} with {}".format(targetarea, targettile, disruptstring)
                    else:
                        print "???"
                    #print "Target Area: {}".format(targetarea)
                    #print "Target Tile: {}".format(targettile)
                    #print "Flag: {}".format(disruption["type"])
                    #print "Value: {}".format(disruption["value"])
                    #print items
                    #print "\n".join(binary(format(ord(x), 'b')) for x in disruption["someothervalues"])
        
        #self.printbinary(index)
        
        #BITS UNACCOUNTED FOR:
        #1.3 to 1.5 [3 bits]
        #3.3 to 3.7 [5 bits]
        #6.4 to 6.7 [4 bits]
        #10.0 to 48.1 (almost certainly disruptions) [38 bytes, 2 bits (306 bits)]
        #53.6 to 56.6 [3 bytes, 1 bit (25 bits)]
        #58.7 to 59.7 [1 byte, 1 bit (9 bits)]
        #bytes 62 and 63
        #byte 66
        #71.4 to 72.2 (7 bits)
        #74.4 to 79.7 [5 bytes, 5 bits (45 bits)]
        #87.0 to 88.1 [1 byte, 2 bits (10 bits)]
        #89.2 to 91.7 [2 bytes, 6 bits(22 bits)]
        
    def printalldata(self, extra=False):
        for record in range(self.databin.num_records):
            self.printdata(record, extra=extra)
            print #blank line between records!
    
    def printbinary(self,index):
        record = self.databin.getRecord(index)
        print "\n".join(format(ord(x), 'b') for x in record.binary)

class Countdowns:
    databin = None
    records = None
    
    @classmethod
    def getDisruptions(thisClass, index):
        if thisClass.databin is None:
            thisClass = thisClass()
        if thisClass.records[index] is None:
            binary = thisClass.databin.getRecord(index)
            indices = [readbits(binary, i*2, 0, 12) for i in range(8)]
            thisClass.records[index] = indices
        return thisClass.records[index]
    
    def __init__(self):
        self.databin = BinStorage("Configuration Tables/bossAction.bin")
        self.records = [None for i in range(self.databin.num_records)]

class Disruptions:
    databin = None
    records = None
    
    @classmethod
    def getDisruptions(thisClass, index):
        if thisClass.databin is None:
            thisClass = thisClass()
        if thisClass.records[index] is None:
            binary = thisClass.databin.getRecord(index)
            someothervalues = binary[0:4]
            #bytes 3 and 4 are apparently always 10100000 00000001
            indices = [readbits(binary, i*2 + 4, 0, 16) for i in range(12)]
            thisClass.records[index] = {"width":readbits(binary, 0, 0, 3), "height":readbits(binary, 0, 3, 3), "value":readbits(binary, 0, 6, 3), "type":readbits(binary, 1, 1, 2), "column":readbits(binary, 1, 3, 3), "row":readbits(binary, 1, 6, 3), "indices":indices, "someothervalues":someothervalues}
        return thisClass.records[index]
    
    def __init__(self):
        self.databin = BinStorage("Configuration Tables/bossActionPokemonData.bin")
        self.records = [None for i in range(self.databin.num_records)]

class StageDefaultSupports:
    databin = None
    records = None
    
    @classmethod
    def getSupportNames(thisClass, setID, numSupports=4):
        namesToGet = thisClass.getSupports(setID)[0:numSupports]
        names = []
        for name in namesToGet:
            if name < 1152:
                names.append(PI.PokemonData.getPokemonInfo(name).fullname)
            elif name == 1152: #disruptions hardcoded for now - ah well
                names.append("Rock")
            elif name == 1153: 
                names.append("Block")
            elif name == 1154: 
                names.append("Coin")
            else:
                names.append("??? (Disruption "+str(name)+")")
        return names         
            
    @classmethod
    def getSupports(thisClass, setID):
        if thisClass.databin is None:
            thisClass = thisClass()
        if thisClass.records[setID] is None:
            setChunk = thisClass.databin.getRecord(setID)
            thisClass.records[setID] = [unpack("<H",setChunk[char:char+2])[0] for char in range(0,thisClass.databin.record_len,2)]
        return thisClass.records[setID]
        
    #private init, pls don't use
    def __init__(self):
        self.databin = BinStorage("Configuration Tables/pokemonSet.bin")
        self.records = [None for i in range(self.databin.num_records)]

class ItemSet:
    databin = None
    records = None
    
    @classmethod
    def getItems(thisClass, setID):
        itemset = thisClass.getItemSet(setID)
        items = []
        for item in itemset:
            if item == 0:
                continue
            items.append(["M+5", "T+10", "EXP", "MS", "C-1", "DD", "APU", "Unknown", "MS (Free)", "C-1 (Free)", "DD (Free)", "APU (Free)"][item-1])
        if len(items) == 0:
            return ["None"]
        return items
    
    @classmethod
    def getItemSet(thisClass, setID):
        if thisClass.databin is None:
            thisClass = thisClass()
        if thisClass.records[setID] is None:
            chunk = thisClass.databin.getRecord(setID)
            thisClass.records[setID] = [readbyte(chunk, i) for i in [4,6,8,10,12,14]]
        return thisClass.records[setID]
    
    def __init__(self):
        self.databin = BinStorage("Configuration Tables/itemPattern.bin")
        self.records = [None for i in range(self.databin.num_records)]