#!/usr/bin/python

import sys
from bindata import *

locale = "US" #change this for different language

type_overrides = [0,1,3,4,2,6,5,7,8,9,10,12,11,14,13,15,16,17]
#this list patches the fact that the type names in messagePokemonType_whatever are out of order compared to what the records expect. If the typeindex is, say, 6 [for Rock], this list will redirect it to type list entry 5 (where 'Rock' is actually stored, instead of the wrong value, 'Bug').
#If GS ever switches this up, or it turns out to be different in different locales, this list can be reset to compensate.
#remember, if the pokemon record says the type is index#X, then the actual location of that should be in type_overrides[X].

class PokemonDataRecord:
	def __init__(self,index,snippet,namingBin,typeBin):
			#this is for finding the names
			
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
		#TODO: consolidate this
		self.ss1index = readbyte(snippet, 32)
		self.ss2index = readbyte(snippet, 33)
		self.ss3index = readbyte(snippet, 34)
		self.ss4index = readbyte(snippet, 35)
	
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
		
		#Nidoran fix
		if self.name == "Nidoran@":
			self.name = "Nidoran-F"
		if self.name == "NidoranB":
			self.name = "Nidoran-M"
		
		#Unowns have nonexistant modifiers, and some Pikachus have identical modifiers, so let's deal with those...
		if self.name == "Unown":
			renamedmodifiers = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","Exclamation","Question"]
			self.modifier = renamedmodifiers[self.index - 201]
		if self.name == "Pikachu":
			if self.modifier == "Costume":
				print self.modifier
				renamedmodifiers = ["Charizard Costume", "Magikarp Costume", "Gyarados Costume", "Shiny Gyarados Costume", "Ho-Oh Costume", "Lugia Costume", "", "", "Rayquaza Costume", "Shiny Rayquaza Costume"]
				self.modifier = renamedmodifiers[self.index - 869]
			if self.modifier == "Celebration":
				#Well... most of these aren't released yet so they probably won't be needed for now
				renamedmodifiers = ["Celebration", "Celebration", "Celebration", "Celebration", "Beach Walk", "Celebration", "Celebration", "Celebration", "Celebration", "Celebration", "Celebration", "Celebration"]
				self.modifier = renamedmodifiers[self.index - 879]
		
		self.fullname = self.name
		if (self.modifier != ""):
			self.fullname += " (" + self.modifier + ")"
	
		#type
		try:
			self.type = typeBin.getMessage(type_overrides[self.typeindex])
		except IndexError:
			self.type = "UNKNOWN ({})".format(self.typeindex)
	

		#ability and skill swapper abilities
		try:
			self.ability = PokemonAbility.getAbilityInfo(self.abilityindex).name
		except IndexError:
			self.ability = "UNKNOWN ({})".format(self.abilityindex)
		try:
			if self.ss1index != 0:
				self.ss1 = PokemonAbility.getAbilityInfo(self.ss1index).name
		except IndexError:
			self.ss1 = "UNKNOWN ({})".format(self.ss1index)
		try:
			if self.ss2index !=0:
				self.ss2 = PokemonAbility.getAbilityInfo(self.ss2index).name
		except IndexError:
			self.ss2 = "UNKNOWN ({})".format(self.ss2index)
		try:
			if self.ss3index != 0:
				self.ss3 = PokemonAbility.getAbilityInfo(self.ss3index).name
		except IndexError:
			self.ss3 = "UNKNOWN ({})".format(self.ss3index)
		try:
			if self.ss4index != 0:
				self.ss4 = PokemonAbility.getAbilityInfo(self.ss4index).name
		except IndexError:
			self.ss4 = "UNKNOWN ({})".format(self.ss4index)
	
		#mega stone
		try:
			if self.megastoneindex != 0:
				self.megastone = PokemonData.getPokemonInfo(self.megastoneindex)
		except IndexError:
			self.megastone = ""

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
		self.databin = BinStorage("pokemonData.bin")
		self.namebin = BinStorage("messagePokemonList_"+locale+".bin")
		self.typebin = BinStorage("messagePokemonType_"+locale+".bin")
		self.records = [None for item in range(self.databin.num_records)]
	
	@classmethod
	def getPokemonInfo(thisClass, index):
		if thisClass.databin is None:
			thisClass = thisClass()
		if thisClass.records[index] is None:
			thisClass.records[index] = PokemonDataRecord(index, thisClass.databin.getRecord(index),thisClass.namebin,thisClass.typebin)
		return thisClass.records[index]
	
	@classmethod
	def printdata(thisClass,index):
		record = thisClass.getPokemonInfo(index)
	
		print "Pokemon Index " + str(record.index)
	
		if (record.classtype == 0):
			pokemonfullname = record.name
			if (record.modifier != ""):
				pokemonfullname += " (" + record.modifier + ")"
			
			print "Name: " + pokemonfullname
			print "Dex: " + str(record.dex)
			print "Type: " + str(record.type)
			print "BP: " + str(PokemonAttack.getPokemonAttack(record.bpindex,1))
			print "RMLs: " + str(record.rmls)
			print "Ability: " + str(record.ability) + " (index " + str(record.abilityindex) + ")"
			if (record.ss1index !=0):	 #only display the skill swapper ability if it has one
				print "SS Ability 1: " + str(record.ss1) + " (index " + str(record.ss1index) + ")"
			if (record.ss2index != 0):
				print "SS Ability 2: " + str(record.ss2) + " (index " + str(record.ss2index) + ")"
			if (record.ss3index != 0):
				print "SS Ability 3: " + str(record.ss3) + " (index " + str(record.ss3index) + ")"
			if (record.ss4index != 0):
				print "SS Ability 4: " + str(record.ss4) + " (index " + str(record.ss4index) + ")"
		
		elif (record.classtype == 1):
			print "This is a disruption entry. We don't know much more rn. 1152/1153/1154 are Rock/Block/Coin, respectively." 
			
		elif (record.classtype == 2):
			pokemonfullname = record.name
			if (record.modifier != ""):
				pokemonfullname += " (" + record.modifier + ")"
			print "Name: " + pokemonfullname
			print "Mega Stone: " + str(record.megastone.name) + " (Index " + str(record.megastoneindex) + ")"
			print "Dex: " + str(record.dex)
			print "Type: " + str(record.type)
			print "Icons to Mega Evolve: " + str(record.icons)
			print "MSUs Available: " + str(record.msu)
			
		else:
			pokemonfullname = record.name
			if (record.modifier != ""):
				pokemonfullname += " (" + record.modifier + ")"
			print "Name: " + pokemonfullname
	
	
	@classmethod
	def printalldata(thisClass):
		if thisClass.databin is None:
			thisClass = thisClass()
		for record in range(thisClass.databin.num_records):
			thisClass.printdata(record)
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
		databin = BinStorage("pokemonAttack.bin")
		self.APs = [[] for i in range(databin.record_len)] #one sublist for each growth class
		
		for i in range(databin.num_records):
			thisRecord = databin.getRecord(i)
			for growth, byte in enumerate(thisRecord):
				self.APs[growth].append(ord(byte))
								
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
		self.databin = BinStorage("pokemonAbility.bin")		
		self.namebin = BinStorage("messagePokedex_"+locale+".bin")
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
		
		print "SP Requirements: {} => {} => {} => {}".format(*record.skillboost)
		
		print "Name Index: " + str(record.nameindex)
	
	@classmethod
	def printalldata(thisClass):
		if thisClass.databin is None:
			thisClass = thisClass()
		for record in range(thisClass.databin.num_records):
			thisClass.printdata(record)
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

