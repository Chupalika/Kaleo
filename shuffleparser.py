#!/usr/bin/python

from __future__ import division

import sys, getopt
from struct import unpack

initialoffset = 80
initialoffsetability = 100
stagedatalength = 92
#pokemondatalength = 36
pokemonattacklength = 7
pokemonabilitylength = 36
maxlevel = 30

pokemonlist = []
pokemontypelist = []
pokemonabilitylist = []
dropitems = {"1":"RML", "3":"EBS", "4":"EBM", "5":"EBL", "6":"SBS", "7":"SBM", "8":"SBL", "10":"MSU", "23":"10 Hearts", "30":"5000 Coins", "32":"PSB"}


class BinStorage:
	def __init__(self, binFile):
		try:
			with open(binFile, "rb") as file:
				self.contents = file.read()
		except IOError:
			sys.stderr.write("Couldn't open the file {}. Please check the file is present.\n".format(binFile))
			sys.exit(1)
			
		self.num_records = unpack("<I",self.contents[0:4])[0]
		self.record_len = unpack("<I",self.contents[4:8])[0]
		self.text_start_point = unpack("<I",self.contents[8:12])[0]
		#I'm only 50% sure this is the text segment start point. Further investigation required.
		self.data_start_point = unpack("<I",self.contents[16:20])[0]
		self.third_seg_start_point = unpack("<I",self.contents[24:28])[0]
		#this is the start of the segment that comes after the data segment of .bin files. Is it some kind of index? I have no clue.
		
	def getAll(self):
		return self.contents
		
	def getRecord(self,index):
		record_start = self.data_start_point + index * self.record_len
		return self.contents[record_start:record_start+self.record_len]	

	def getHeader(self):
		return self.contents[:self.text_start_point]
		
	def getTextSegment(self):
		return self.contents[self.text_start_point:self.data_start_point]
		
	#todo: methods for parsing text - what about message .bin files?	
		
	def getAllRecords(self):
		return self.contents[self.data_start_point:self.third_start_point]
		
	def getThirdSegment(self):
		return self.contents[self.third_start_point:]

class PokemonDataRecord:
	def __init__(self,index,snippet):
			#this is for finding the names
			
		self.binary = snippet
		self.index = index	
			
		if len(pokemonlist) == 0:
			definepokemonlist()
	
		#this is for finding the types
		if len(pokemontypelist) == 0:
			definepokemontypelist()
	
		#this is for finding the types
		if len(pokemonabilitylist) == 0:
			definepokemonabilitylist()

		#parse!
		self.dex = readbits(snippet, 0, 0, 10)
		self.typeindex = readbits(snippet, 1, 3, 5)
		self.abilityindex = readbits(snippet, 2, 0, 8)
		self.bpindex = readbits(snippet, 3, 0, 4) #index of base power of the pokemon
		self.rmls = readbits(snippet, 4, 0, 6)
		self.nameindex = readbits(snippet, 6, 5, 11)
		self.modifierindex = readbits(snippet, 8, 0, 8)
		self.classtype = readbits(snippet, 9, 4, 3) #0 means it's a Pokemon, 2 means it's a Mega Pokemon
		self.icons = readbits(snippet, 10, 0, 7)
		self.msu = readbits(snippet, 10, 7, 7)
		self.megastoneindex = readbits(snippet, 12, 0, 11) #refers to the Index number of the mega stone
		self.megaindex = readbits(snippet, 13, 3, 11) #refers to the Index number of the base mega pokemon
		self.ss1index = readbyte(snippet, 32)
		self.ss2index = readbyte(snippet, 33)
		self.ss3index = readbyte(snippet, 34)
		self.ss4index = readbyte(snippet, 35)
	
		#determine a few values
		#name and modifier
		try:
			self.name = pokemonlist[self.nameindex]
		except IndexError:
			self.name = ""
		if self.modifierindex != 0:
			self.modifierindex += 768
			try:
				self.modifier = pokemonlist[self.modifierindex]
			except IndexError:
				self.modifier = ""
		else:
			self.modifier = ""
	
		#type
		try:
			self.type = pokemontypelist[self.typeindex]
		except IndexError:
			self.type = ""
	
		#ap list
		self.aplist = PokemonAttack(self.bpindex).APs #this function does a nice job
	
		#ability and skill swapper abilities
		try:
			self.ability = pokemonabilitylist[self.abilityindex]
		except IndexError:
			self.ability = "UNKNOWN ({})".format(self.ability)
		try:
			if (self.ss1index != 0):
				self.ss1 = pokemonabilitylist[self.ss1index]
		except IndexError:
			self.ss1 = "UNKNOWN ({})".format(self.ss1index)
		try:
			if (self.ss2index !=0):
				self.ss2 = pokemonabilitylist[self.ss2index]
		except IndexError:
			self.ss2 = "UNKNOWN ({})".format(self.ss2index)
		try:
			if (self.ss3index != 0):
				self.ss3 = pokemonabilitylist[self.ss3index]
		except IndexError:
			self.ss3 = "UNKNOWN ({})".format(self.ss3index)
		try:
			if (self.ss4index != 0):
				self.ss4 = pokemonabilitylist[self.ss4index]
		except IndexError:
			self.ss4 = "UNKNOWN ({})".format(self.ss4index)
	
		#mega stone
		try:
			if (self.megastoneindex != 0):
				self.megastone = PokemonData.getPokemonInfo(self.megastoneindex)
		except IndexError:
			self.megastone = ""

#PokemonDataRecord class ends.

class PokemonData:
	
	#now using singleton design pattern - that is, there is only ever one PokemonData instance. 
	
	databin = None
	records = []
	
	#this constructor is now PRIVATE. Please do not use it; please use getPokemonInfo.
	def __init__(self):
		#open file and store data - extraction is handled by getData and the PokemonDataRecord nested class
		if self.databin is not None:
			sys.stderr.write("Something is wrong. The init for PokemonData was called more than once.")
			sys.exit(1)
		self.databin = BinStorage("pokemonData.bin")
		self.records = [None for item in range(self.databin.num_records)]
	
	@classmethod
	def getPokemonInfo(thisClass, index):
		if thisClass.databin is None:
			thisClass = thisClass()
		if thisClass.records[index] is None:
			thisClass.records[index] = PokemonDataRecord(index, thisClass.databin.getRecord(index))
		return thisClass.records[index]
	
	@classmethod
	def printdata(thisClass,index):
		record = thisClass.getPokemonInfo(index)
	
		if (record.classtype == 0): 
			print "Pokemon Index " + str(record.index)
			
			pokemonfullname = record.name
			if (record.modifier != ""):
				pokemonfullname += " (" + record.modifier + ")"
			print "Name: " + pokemonfullname
			print "Dex: " + str(record.dex)
			print "Type: " + str(record.type)
			print "BP: " + str(record.aplist[0])
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
			
		elif (record.classtype == 2):
			print "Pokemon Index " + str(record.index)
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
			print "Index " + str(record.index)
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

class StageData:
	def __init__(self, index, event=False, expert=False):
		self.index = index
		
		#open file and extract the snippet we need
		if event:
			file = open("StageDataEvent.bin", "rb")
		elif expert:
			file = open("StageDataExtra.bin", "rb")
		else:
			file = open("stageData.bin", "rb")
		contents = file.read()
		begin = initialoffset + (stagedatalength * index)
		end = begin + stagedatalength
		snippet = contents[begin:end]
		self.binary = snippet
		file.close()
		
		#parse!
		self.pokemonindex = readbits(snippet, 0, 0, 10)
		self.megapokemon = readbits(snippet, 1, 2, 4) #determines if the pokemon is a mega pokemon
		self.numsupports = readbits(snippet, 1, 6, 4)
		self.timed = readbits(snippet, 2, 2, 1)
		self.seconds = readbits(snippet, 2, 3, 8)
		self.hp = readbits(snippet, 4, 0, 20)
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
		self.trackid = readbits(snippet, 72, 3, 6)
		self.extrahp = readbits(snippet, 80, 0, 16)
		self.moves = readbits(snippet, 86, 0, 8)
		self.backgroundid = readbits(snippet, 88, 2, 8)

		#unknown values for now
		self.defaultsetindex = readbits(snippet, 84, 0, 16)
		#default supports - i.e. what's in the skyfall 
		
		self.layoutindex = readbits(snippet, 82, 0, 16)
		#layout = stage layout data. starting board.
		
		#determine a few values
		if self.megapokemon == 1:
			self.pokemonindex += 1024
		self.pokemon = PokemonData.getPokemonInfo(self.pokemonindex)
	
	def printdata(self):
		print "Stage Index " + str(self.index)
		
		pokemonfullname = self.pokemon.name
		if (self.pokemon.modifier != ""):
			pokemonfullname += " (" + self.pokemon.modifier + ")"
		print "Pokemon: " + pokemonfullname
		
		hpstring = "HP: " + str(self.hp)
		if (self.extrahp != 0):
			hpstring += " + " + str(self.extrahp)
		print hpstring
		if (self.timed == 0):
			print "Moves: " + str(self.moves)
		else:
			print "Seconds: " + str(self.seconds)
		print "Experience: " + str(self.exp)
		
		if (self.timed == 0):
			print "Catchability: " + str(self.basecatch) + "% + " + str(self.bonuscatch) + "%/move"
		else:
			print "Catchability: " + str(self.basecatch) + "% + " + str(self.bonuscatch) + "%/3sec"
		
		print "# of Support Pokemon: " + str(self.numsupports)
		print "Rank Requirements: " + str(self.srank) + " / " + str(self.arank) + " / " + str(self.brank)
		
		print "Coin reward (first clear): " + str(self.coinrewardfirst)
		print "Coin reward (repeat clear): " + str(self.coinrewardrepeat)
		print "Background ID: " + str(self.backgroundid)
		print "Track ID: " + str(self.trackid)
		
		if (self.drop1item != 0 or self.drop2item != 0 or self.drop3item != 0):
			try:
				drop1item = dropitems[str(self.drop1item)]
			except KeyError:
				drop1item = self.drop1item
			try:
				drop2item = dropitems[str(self.drop2item)]
			except KeyError:
				drop2item = self.drop2item
			try:
				drop3item = dropitems[str(self.drop3item)]
			except KeyError:
				drop3item = self.drop3item
			print "Drop Items: " + str(drop1item) + " / " + str(drop2item) + " / " + str(drop3item)
			print "Drop Rates: " + str(1/pow(2,self.drop1rate-1)) + " / " + str(1/pow(2,self.drop2rate-1)) + " / " + str(1/pow(2,self.drop3rate-1))
	
	def printbinary(self):
		print "\n".join(format(ord(x), 'b') for x in self.binary)

class PokemonAttack:
	def __init__(self, index):
		self.index = index-1
		
		#open file and... grab the whole thing
		file = open("pokemonAttack.bin", "rb")
		contents = file.read()
		begin = initialoffset
		end = begin + (pokemonattacklength * maxlevel)
		snippet = contents[begin:end]
		self.binary = snippet
		file.close()
		
		#Parse the AP values of all levels, given the BP index
		self.APs = []
		for i in range(maxlevel):
			self.APs.append(readbyte(snippet, (pokemonattacklength*i) + self.index))

class PokemonAbility:
	def __init__(self, index):
		self.index = index
		
		#open file and extract the snippet we need
		file = open("pokemonAbility.bin", "rb")
		contents = file.read()
		begin = initialoffsetability + (pokemonabilitylength * index)
		end = begin + pokemonabilitylength
		snippet = contents[begin:end]
		self.binary = snippet
		file.close()
		
		#this is for finding the names and descriptions
		if len(pokemonabilitylist) == 0:
			definepokemonabilitylist()
		
		#parse!
		self.type = readbyte(snippet, 4)
		self.rate3 = readbyte(snippet, 5)
		self.rate4 = readbyte(snippet, 6)
		self.rate5 = readbyte(snippet, 7)
		self.nameindex = readbyte(snippet, 8) #index in the search dropdown menu
		self.descindex = readbyte(snippet, 9)
		self.sp1 = readbyte(snippet, 10)
		self.sp2 = readbyte(snippet, 11)
		self.sp3 = readbyte(snippet, 12)
		self.sp4 = readbyte(snippet, 13)
		
		#determine a few values
		self.name = pokemonabilitylist[self.index]
		#self.desc = pokemonabilitylist[self.descindex + 159]
	
	def printdata(self):
		print "Ability Index " + str(self.index)
		print "Name: " + str(self.name)
		#print "Description: " + str(self.desc)
		print "type: " + str(self.type)
		print "Activation Rates: " + str(self.rate3) + "% / " + str(self.rate4) + "% / " + str(self.rate5) + "%"
		print "SP Requirements: " + str(self.sp1) + " -> " + str(self.sp2) + " -> " + str(self.sp3) + " -> " + str(self.sp4)
		print "descindex: " + str(self.descindex)
		
		print "float1: " + str(unpack("f", self.binary[16:20])[0])
		print "float2: " + str(unpack("f", self.binary[20:24])[0])
		print "float3: " + str(unpack("f", self.binary[24:28])[0])
		print "float4: " + str(unpack("f", self.binary[28:32])[0])
		print "float5: " + str(unpack("f", self.binary[32:36])[0])
		
		print "unknownbyte0: " + str(readbyte(self.binary, 0))
		print "unknownbyte1: " + str(readbyte(self.binary, 1))
		print "unknownbyte2: " + str(readbyte(self.binary, 2))
		print "unknownbyte3: " + str(readbyte(self.binary, 3))
		print "unknownbyte14: " + str(readbyte(self.binary, 14))
		print "unknownbyte15: " + str(readbyte(self.binary, 15))
	
	def printbinary(self):
		print "\n".join(format(ord(x), 'b') for x in self.binary)

def main(args):
	#make sure correct number of arguments
	if len(args) != 2:
		print 'need 2 arguments: datatype, index'
		sys.exit()
	
	#parse arguments
	datatype = args[0]
	index = args[1]
	
	try:
		if datatype == "stage":
			if index == "all":
				numentries = getnumentries("stageData.bin")
				for i in range(numentries):
					sdata = StageData(i)
					sdata.printdata()
					print
			else:
				sdata = StageData(int(index))
				sdata.printdata()
		
		elif datatype == "expertstage":
			if index == "all":
				numentries = getnumentries("stageDataExtra.bin")
				for i in range(numentries):
					sdata = StageData(i, False, True)
					sdata.printdata()
					print
			else:
				sdata = StageData(int(index), False, True)
				sdata.printdata()
		
		
		elif datatype == "eventstage":
			if index == "all":
				numentries = getnumentries("stageDataEvent.bin")
				for i in range(numentries):
					sdata = StageData(i, True, False)
					sdata.printdata()
					print
			else:
				sdata = StageData(int(index), True, False)
				sdata.printdata()
		
		elif datatype == "pokemon":
			if index == "all":
				PokemonData.printalldata()
			else:
				PokemonData.printdata(int(index))
		
		elif datatype == "ability":
			if index == "all":
				numentries = getnumentries("pokemonAbility.bin")
				for i in range(numentries):
					adata = PokemonAbility(i)
					adata.printdata()
					print
			else:
				adata = PokemonAbility(int(index))
				adata.printdata()
		
		else:
			sys.stderr.write("datatype should be stage, expertstage, eventstage, pokemon, or ability\n")
	except IOError:
		sys.stderr.write("Couldn't find the bin file to extract data from.\n")
		raise

#Reads a certain number of bits starting from an offset byte and bit and returns the value
def readbits(text, offsetbyte, offsetbit, numbits):
	ans = ""
	bytes = [ord(b) for b in text[offsetbyte:offsetbyte+4]]
	val = 0
	for i in reversed(xrange(4)):
		val *= 256
		val += bytes[i]
	val >>= offsetbit
	val &= (1 << numbits) -1
	return val

def readbyte(text, offsetbyte):
	return ord(text[offsetbyte])

#Checks the first 2 bytes of a file and returns the value
def getnumentries(filename):
	file = open(filename, "rb")
	contents = file.read()
	numentries = readbits(contents, 0, 0, 32)
	file.close()
	return numentries

#Defines the global list for pokemon names
def definepokemonlist():
	try:
		listfile = open("pokemonlist.txt", "r")
		thewholething2 = listfile.read()
		global pokemonlist
		pokemonlist = thewholething2.split("\n")
		listfile.close()
	except IOError:
		sys.stderr.write("Couldn't find pokemonlist.txt to retrieve Pokemon names.\n")
		pokemonlist = [""] #to prevent calling this function again

#Defines the global list for pokemon types
def definepokemontypelist():
	try:
		listfile = open("pokemontypelist.txt", "r")
		thewholething2 = listfile.read()
		global pokemontypelist
		pokemontypelist = thewholething2.split("\n")
		listfile.close()
	except IOError:
		sys.stderr.write("Couldn't find pokemontypelist.txt to retrieve Pokemon types.\n")
		pokemontypelist = [""] #to prevent calling this function again

#Defines the global list for pokemon abilities and descriptions
def definepokemonabilitylist():
	try:
		listfile = open("pokemonabilitylist.txt", "r")
		thewholething2 = listfile.read()
		global pokemonabilitylist
		pokemonabilitylist = thewholething2.split("\n")
		listfile.close()
	except IOError:
		sys.stderr.write("Couldn't find pokemonabilitylist.txt to retrieve Pokemon abilities.\n")
		pokemontypelist = [""] #to prevent calling this function again


if __name__ == "__main__":
	main(sys.argv[1:])
