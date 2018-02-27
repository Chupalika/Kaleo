#!/usr/bin/python

import sys
from bindata import *

locale = "US" #change this for different language

type_overrides = [0,1,3,4,2,6,5,7,8,9,10,12,11,14,13,15,16,17]
#this list patches the fact that the type names in messagePokemonType_whatever are out of order compared to what the records expect. If the typeindex is, say, 6 [for Rock], this list will redirect it to type list entry 5 (where 'Rock' is actually stored, instead of the wrong value, 'Bug').
#If GS ever switches this up, or it turns out to be different in different locales, this list can be reset to compensate.
#remember, if the pokemon record says the type is index#X, then the actual location of that should be in type_overrides[X].

megaeffects_overrides = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,36,37,38,33,34,35]

class PokemonDataRecord:
    def __init__(self, index, snippet, namingBin, typeBin, pokedexBin, extra=""):
        self.binary = snippet
        self.index = index    
    
        #parse!
        self.dex = readbits(snippet, 0, 0, 10)
        self.typeindex = readbits(snippet, 1, 3, 5)
        self.abilityindex = readbits(snippet, 2, 0, 8)
        self.bpindex = readbits(snippet, 3, 0, 4) #index of base power of the pokemon - APs can now be read with PokemonAttack.getPokemonAttack(this value,level)
        self.rmls = readbits(snippet, 4, 0, 6)
        self.nameindex = readbits(snippet, 6, 5, 11)
        self.modifierindex = readbits(snippet, 8, 0, 8)
        self.classtype = readbits(snippet, 9, 4, 3) #0 means it's a Pokemon, 1 = disruption, 2 means it's a Mega Pokemon
        self.icons = readbits(snippet, 10, 0, 7)
        self.msu = readbits(snippet, 10, 7, 7)
        self.megastoneindex = readbits(snippet, 12, 0, 11) #refers to the Index number of the mega stone
        self.megaindex = readbits(snippet, 13, 3, 11) #refers to the Index number of the base mega pokemon
        self.ssindices = []
        if extra == "m":
            for i in range(48, 52):
                self.ssindices.append(readbyte(snippet, i))
        else:
            for i in range(32, 36):
                self.ssindices.append(readbyte(snippet, i))
    
        #determine a few values
        #name and modifier
        try:
            self.name = namingBin.getMessage(self.nameindex)
            #print self.name
        except IndexError:
            self.name = "UNKNOWN ({})".format(self.nameindex)
        if self.modifierindex != 0:
            self.modifierindex += 768
            try:
                self.modifier = namingBin.getMessage(self.modifierindex)
            except IndexError:
                self.modifier = "UNKNOWN ({})".format(self.modifierindex)
        else:
            self.modifier = ""
        
        #Unowns have nonexistant modifiers, and some Pikachus have identical modifiers, so let's deal with those...
        if self.name == "Unown":
            renamedmodifiers = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","Exclamation","Question"]
            self.modifier = renamedmodifiers[self.index - 201]
        if self.name == "Pikachu":
            if self.modifier == "Costume":
                renamedmodifiers = ["Charizard Costume", "Magikarp Costume", "Gyarados Costume", "Shiny Gyarados Costume", "Ho-Oh Costume", "Lugia Costume", "", "", "Rayquaza Costume", "Shiny Rayquaza Costume"]
                self.modifier = renamedmodifiers[self.index - 869]
            if self.modifier == "Celebration":
                renamedmodifiers = ["Intern", "Children's Day", "Rainy Season", "Summer Festival", "Beach Walk", "Pastry Chef", "Artist", "Mushroom Harvest", "Year's End", "Lion Dancer", "Kotatsu", "Graduate"]
                self.modifier = renamedmodifiers[self.index - 879]
        
        #Nidoran
        if self.index == 29:
            self.name = "Nidoran-F"
        if self.index == 32:
            self.name = "Nidoran-M"
        
        #Shiny Genesect
        if self.index == 707:
            self.modifier = "Shiny"
        
        self.fullname = self.name
        if (self.modifier != ""):
            self.fullname += " (" + self.modifier + ")"
    
        #type
        try:
            self.type = typeBin.getMessage(type_overrides[self.typeindex])
        except IndexError:
            self.type = "UNKNOWN ({})".format(self.typeindex)
        
        #BP
        self.bp = PokemonAttack.getPokemonAttack(self.bpindex, 1)
        self.maxap = PokemonAttack.getPokemonAttack(self.bpindex, 10 + self.rmls)

        #ability and skill swapper abilities
        self.ss = []
        try:
            self.ability = PokemonAbility.getAbilityInfo(self.abilityindex).name
        except IndexError:
            self.ability = "UNKNOWN ({})".format(self.abilityindex)
        for ssindex in self.ssindices:
            try:
                if ssindex != 0:
                    self.ss.append(PokemonAbility.getAbilityInfo(ssindex).name)
            except IndexError:
                self.ss.append("UNKNOWN ({})".format(ssindex))
    
        #mega stone
        try:
            if self.megastoneindex != 0:
                self.megastone = PokemonData.getPokemonInfo(self.megastoneindex)
        except IndexError:
            self.megastone = ""
        
        #mega power
        if self.classtype == 2:
            self.megapower = " ".join(pokedexBin.getMessage(megaeffects_overrides[self.abilityindex] + 231).split())
        else:
            self.megapower = ""

#PokemonDataRecord class ends.

class PokemonData:    
    #now using singleton design pattern - that is, there is only ever one PokemonData instance. 
    
    databin = None
    namebin = None
    typebin = None
    records = []
    
    #this constructor is now PRIVATE. Please do not use it; please use getPokemonInfo.
    def __init__(self):
        #open file and store data - extraction is handled by getData and the PokemonDataRecord nested class
        if self.databin is not None:
            sys.stderr.write("Something is wrong. The init for PokemonData was called more than once.")
            sys.exit(1)
        self.databin = BinStorage("Configuration Tables/pokemonData.bin")
        self.namebin = BinStorage("Message_{}/messagePokemonList_{}.bin".format(locale, locale), "app") #in app data 
        self.typebin = BinStorage("Message_{}/messagePokemonType_{}.bin".format(locale, locale), "app") #also in app data
        self.pokedexbin = BinStorage("Message_{}/messagePokedex_{}.bin".format(locale, locale))
        
        self.records = [None for item in range(self.databin.num_records)]
    
    @classmethod
    def getPokemonInfo(thisClass, index, extra=""):
        if thisClass.databin is None:
            thisClass = thisClass()
        if thisClass.records[index] is None:
            thisClass.records[index] = PokemonDataRecord(index, thisClass.databin.getRecord(index), thisClass.namebin, thisClass.typebin, thisClass.pokedexbin, extra)
        return thisClass.records[index]
    
    @classmethod
    def printdata(thisClass, index, extra=""):
        record = thisClass.getPokemonInfo(index, extra)
    
        print "Pokemon Index " + str(record.index)
    
        if (record.classtype == 0):
            print "Name: " + record.fullname
            print "Dex: " + str(record.dex)
            print "Type: " + str(record.type)
            print "BP: " + str(record.bp)
            print "RMLs: " + str(record.rmls)
            print "Ability: " + str(record.ability) + " (index " + str(record.abilityindex) + ")"
            for i in range(len(record.ss)):
                print "SS Ability {}: {} (index {})".format(i+1, str(record.ss[i]), str(record.ssindices[i]))
        
        elif (record.classtype == 1):
            print "This is a disruption entry. We don't know much more rn. 1152/1153/1154 are Rock/Block/Coin, respectively." 
            
        elif (record.classtype == 2):
            print "Name: " + record.fullname
            print "Mega Stone: " + str(record.megastone.name) + " (Index " + str(record.megastoneindex) + ")"
            print "Dex: " + str(record.dex)
            print "Type: " + str(record.type)
            print "Icons to Mega Evolve: " + str(record.icons)
            print "MSUs Available: " + str(record.msu)
            
            print "Mega Effects: {}".format(record.megapower)
            
        else:
            print "Name: " + record.fullname
    
    @classmethod
    def printalldata(thisClass, extra=""):
        if thisClass.databin is None:
            thisClass = thisClass()
        for index in range(thisClass.databin.num_records):
            thisClass.printdata(index, extra)
            print #blank line between records!
    
    @classmethod
    def printdata2(thisClass, query, extra=""):
        if thisClass.databin is None:
            thisClass = thisClass()
        for index in range(thisClass.databin.num_records):
            record = thisClass.getPokemonInfo(index, extra)
            if record.fullname == query:
                thisClass.printdata(index, extra)
                print #blank line between records!
    
    @classmethod            
    def printbinary(thisClass,index):
        if thisClass.databin is None:
            thisClass = thisClass()
        record = thisClass.databin.getRecord(index)
        print "\n".join(format(ord(x), 'b') for x in record.binary)


class PokemonAttack:
    
    APs = None
    
    @classmethod
    def getPokemonAttack(thisClass, growthIndex, level=None):
        if thisClass.APs is None:
            thisClass = thisClass()
        if level is None:    
            return thisClass.APs[growthIndex-1]
        return thisClass.APs[growthIndex-1][level-1]
        #the -1: growthIndex/level start at 1, this array starts at 0

    def __init__(self):
        databin = BinStorage("Configuration Tables/pokemonAttack.bin","app") #it's in app data now
        self.APs = [[] for i in range(databin.record_len)] #one sublist for each growth class
        
        for i in range(databin.num_records):
            thisRecord = databin.getRecord(i)
            for growth, byte in enumerate(thisRecord):
                self.APs[growth].append(ord(byte))

class PokemonExperience:
    EXPs = None
    
    @classmethod
    def getPokemonExperience(thisClass, growthIndex, level=None):
        if thisClass.EXPs is None:
            thisClass = thisClass()
        if level is None:
            return thisClass.EXPs[growthIndex]
        return thisClass.EXPs[growthIndex-1][level-1]
    
    def __init__(self):
        databin = BinStorage("Configuration Tables/pokemonLevel.bin")
        self.EXPs = [[] for i in range(databin.record_len/4)]
        
        for i in range(databin.num_records):
            thisRecord = databin.getRecord(i)
            for j in range(databin.record_len/4):
                exp = readbits(thisRecord, j*4, 0, 32)
                self.EXPs[j].append(exp)

def printExpTable():
    rowstring = "BP\t"
    for i in range(1,8):
        rowstring += str(PokemonAttack.getPokemonAttack(i, level=1)) + "\t"
    print rowstring[:-1]
    print "Level"
    
    for i in range(1,31):
        rowstring = str(i) + "\t"
        for j in range(1,8):
            rowstring += str(PokemonExperience.getPokemonExperience(j, level=i)) + "\t"
        print rowstring[:-1]
                                
class PokemonAbilityRecord:
    def __init__(self,index,snippet,namingBin):
    
        self.index = index
        self.binary = snippet
        #parse!
        #man, floats take up a lot of space
        self.damagemultiplier = readfloat(snippet,0)
                
        self.bonuseffect = readbyte(snippet, 29) #1 if bonus affects activation rate, 2 if bonus affects damage
        self.bonus = [self.bonuseffect-1] #dummy entry for rate increases - 0 for % (+), 1 for damage (*)
        #read bonuseffect early because...
        
        if self.bonuseffect == 1:
            for sectbyte in range(4,20,4):
                self.bonus.append(int(readfloat(snippet,sectbyte))) #we cast to int ONLY if the increases are chance based.
        else: #self.bonuseffect == 2:
            for sectbyte in range(4,20,4):
                self.bonus.append(readfloat(snippet,sectbyte))
        
        self.name = namingBin.getMessage(readbits(snippet,20,0,16))
        self.desc = " ".join(namingBin.getMessage(readbits(snippet,22,0,16)).split()) #strip newlines
        "?"
        
        self.type = readbyte(snippet, 24) #I think this determines the ability's associated icon.
        self.rate = []
        for sectbyte in range(25,28):
            self.rate.append(readbyte(snippet, sectbyte))
        
        self.nameindex = readbyte(snippet, 28) #index in the search dropdown menu. sort by this when printing?
        
        self.skillboost = [] 
        for sectbyte in range(30,34):
            self.skillboost.append(readbyte(snippet, sectbyte))
        #bytes 34 and 35 are end filler or a cap of some sort, so they're no issue.
        #congratulations! We have ALL data for abilities figured out! :D
        
    
class PokemonAbility:

    databin = None
    namebin = None
    records = []
    
    def __init__(self):
        if self.databin is not None:
            sys.stderr.write("Something is wrong. The init for PokemonAbility was called more than once.")
            sys.exit(1)
        self.databin = BinStorage("Configuration Tables/pokemonAbility.bin")        
        self.namebin = BinStorage("Message_{}/messagePokedex_{}.bin".format(locale, locale))
        self.records = [None for item in range(self.databin.num_records)]
    
    @classmethod
    def getAbilityInfo(thisClass, index):
        if thisClass.databin is None:
            thisClass = thisClass()
        if thisClass.records[index] is None:
            thisClass.records[index] = PokemonAbilityRecord(index,thisClass.databin.getRecord(index),thisClass.namebin)
        return thisClass.records[index]
    
    @classmethod
    def printdata(thisClass, index):
        record = thisClass.getAbilityInfo(index)
        
        print "Ability Index " + str(record.index)
        print "Name: " + str(record.name)
        print "Description: " + str(record.desc)
        print "Type: " + ["Offensive", "Defensive", "Mega Boost"][record.type]
        print "Activation Rates: " + str(record.rate[0]) + "% / " + str(record.rate[1]) + "% / " + str(record.rate[2]) + "%"
        print "Damage Multiplier: x" + str(record.damagemultiplier)
        
        #Bonus effect - activation rates
        if (record.bonuseffect == 1):
            for i in range(len(record.bonus)):
                boost = record.bonus[i]
                print "SL{} Bonus: +{}% ({} / {} / {})".format(i+1, boost, format_percent(record.rate[0],boost), format_percent(record.rate[1],boost), format_percent(record.rate[2],boost))
        
        #Bonus effect - damage multiplier
        elif (record.bonuseffect == 2):
            for i in range(len(record.bonus)):
                boost = record.bonus[i]
                print "SL{} Bonus: x{} (x{})".format(i+1, boost, record.damagemultiplier*boost)
        
        elif (record.bonuseffect == 3):
            for i in range(len(record.bonus)):
                boost = record.bonus[i]
                print "SL{} Bonus: {} (x{})".format(i+1, boost, record.damagemultiplier+boost)
        
        else:
            print "Unknown SL Bonus Effect {}".format(record.bonuseffect)
        
        print "SP Requirements: {} => {} => {} => {}".format(*record.skillboost)
        
        print "Name Index: " + str(record.nameindex)
    
    @classmethod
    def printalldata(thisClass):
        if thisClass.databin is None:
            thisClass = thisClass()
        for index in range(thisClass.databin.num_records):
            thisClass.printdata(index)
            print #blank line between records!
    
    @classmethod
    def printdata2(thisClass, query):
        if thisClass.databin is None:
            thisClass = thisClass()
        for index in range(thisClass.databin.num_records):
            record = thisClass.getAbilityInfo(index)
            if query == record.name:
                thisClass.printdata(index)
                print #blank line between records!
        
    @classmethod
    def printbinary(thisClass,index):
        record = thisClass.getAbilityInfo(index)
        print "\n".join(format(ord(x), 'b') for x in record.binary)


def format_percent(num, boost=0):
    #formats rates of ability activations
    if num == 0:
        return "0%"
    num = num+boost    
    if num >= 100:
        return "100%"
    else:
        return "{}%".format(num)

