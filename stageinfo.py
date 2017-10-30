#!/usr/bin/python
from __future__ import division

import sys
from struct import unpack
from bindata import *
import pokemoninfo as PI
import layoutimagegenerator

dropitems = {"1":"RML", "2":"LU", "3":"EBS", "4":"EBM", "5":"EBL", "6":"SBS", "7":"SBM", "8":"SBL", "9":"SS", "10":"MSU", "23":"10 Hearts", "24":"100 Coins", "25":"300 Coins", "27":"2000 Coins", "30":"5000 Coins", "32":"PSB"}
soundtracks = {"17":"bgm-stage-tutorial", "18":"bgm-stage-easy", "19":"bgm-stage-normal", "20":"bgm-stage-hard", "21":"bgm-stage-rare", "22":"bgm-stage-legend", "23":"bgm-stage-boss1", "24":"bgm-stage-boss2", "25":"bgm-stage-ex", "26":"bgm-stage-fun", "27":"bgm-stage-ranking", "29":"bgm-gettime"}

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


class StageDataRecord:
	def __init__(self,index,snippet,mobile=False):
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
		self.extrahp = readbits(snippet, 80, 0, 16)
		self.layoutindex = readbits(snippet, 82, 0, 16) #layout = stage layout data. starting board.
		self.defaultsetindex = readbits(snippet, 84, 0, 16) #default supports - i.e. what's in the skyfall 
		self.moves = readbits(snippet, 86, 0, 8)
		self.backgroundid = readbits(snippet, 88, 2, 8)
		
		#Some values in Mobile are located at different places...
		if mobile == "m":
		    self.costtype = readbits(snippet, 9, 0, 8) #0 is hearts, 1 is coins
		    self.attemptcost = readbits(snippet, 10, 0, 16)
		    self.basecatch = readfloat(snippet, 52)
		    self.bonuscatch = readbits(snippet, 56, 0, 7)
		    self.coinrewardrepeat = readbits(snippet, 60, 0, 14)
		    self.coinrewardfirst = readbits(snippet, 61, 6, 14)
		    self.trackid = readbits(snippet, 74, 0, 10)
		    self.difficulty = readbits(snippet, 76, 0, 3)
		    self.extrahp = readbits(snippet, 84, 0, 16)
		    self.layoutindex = readbits(snippet, 86, 0, 16)
		    self.defaultsetindex = readbits(snippet, 88, 0, 16)
		    self.moves = readbits(snippet, 90, 0, 8)
		    
		    #unknown for now
		    self.backgroundid = "??"
		
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


class StageData:
	databin = None
	records = []
	
	def __init__(self,stage_file):
		self.databin = BinStorage(stage_file)
		self.records = [None for item in range(self.databin.num_records)]
	
	def getStageInfo(self, index, mobile=False):
		if self.records[index] is None:
			self.records[index] = StageDataRecord(index, self.databin.getRecord(index), mobile=mobile)
		return self.records[index]
	
	def printdata(self, index, mobile=False):
		record = self.getStageInfo(index, mobile)
	
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
	    
	def printalldata(self, mobile=False):
		for record in range(self.databin.num_records):
			self.printdata(record, mobile=mobile)
			print #blank line between records!
	
	def printbinary(self,index):
		record = self.databin.getRecord(index)
		print "\n".join(format(ord(x), 'b') for x in record.binary)

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
