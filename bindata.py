#!/usr/bin/python

import sys
from os import chdir, getcwd
from struct import unpack

class BinStorage:

	workingdirs = {}
	pathUsed = None
	
	def __init__(self, binFile, source="ext"):
		
		#change path to working path if this is the first bin file being read - this change sticks and only needs to be done once per program run
		if source != BinStorage.pathUsed:
			chdir(BinStorage.workingdirs[source])
			BinStorage.pathUsed = source
		
		try:
			with open(binFile, "rb") as file:
				self.contents = file.read()
		except IOError:
			if source is None:
				sys.stderr.write("Couldn't open the file {}. Please check the file is present.\n".format(binFile))
			else:
				sys.stderr.write("Couldn't open the file {}. Please check the file is present.\n".format(self.workingdirs[source]+"/"+binFile))
			sys.exit(1)
		
		self.num_records = unpack("<I",self.contents[0:4])[0]
		self.record_len = unpack("<I",self.contents[4:8])[0] #Len of a single data "row"

		# 1st section - Text 
		self.text_start_point = unpack("<I",self.contents[8:12])[0]
		self.text_len = unpack("<I",self.contents[12:16])[0] #Total len of the text section

		# 2nd section - Data 
		self.data_start_point = unpack("<I",self.contents[16:20])[0]
		self.data_len = unpack("<I",self.contents[20:24])[0] #Total len of the data section, effectively num_records * record_len

		# 3rd section - Unknown, looks like an index 
		self.third_seg_start_point = unpack("<I",self.contents[24:28])[0]
		self.third_seg_len = unpack("<I",self.contents[28:32])[0] #Total len of the 3rd section (4 bytes * num_records)

		# 4th section - Unknown
		self.fourth_seg_start_point = unpack("<I",self.contents[32:36])[0]
		self.fourth_seg_len = unpack("<I",self.contents[36:40])[0]

		self.text_only_len = unpack("<I",self.contents[52:56])[0]
		#length of text segment sans file internal ID. Used for message bins.
		
	def getAll(self):
		return self.contents
		
	def getRecord(self,index):
		record_start = self.data_start_point + index * self.record_len
		return self.contents[record_start:record_start+self.record_len]	

	def getHeader(self):
		return self.contents[:self.text_start_point]
		
	def getTextSegment(self):
		return self.contents[self.text_start_point:self.text_start_point+self.text_len]
		
	def getMessage(self, index):
		#this gets a message from a message .bin. Important: IT ONLY WORKS ON MESSAGE BINS - their data segment is an index for their text segment. If you try it on any other .bin, expect gibberish.
		if index >= self.num_records:
			raise IndexError
		
		messageStart = unpack("<I", self.getRecord(index))[0]
		if index == self.num_records - 1:
			#last message:
			message = self.contents[messageStart:self.text_start_point+self.text_only_len-5]
			#the 5 is for the string 'data ' that sits after text but before name and data
		else:
			nextMessageStart = unpack("<I", self.getRecord(index+1))[0]
			message = self.contents[messageStart:nextMessageStart]
	
		# the binary string seems to be utf-16 little indian
		utf16 = message.decode('utf-16-le', 'replace')

		# convert to utf-8 for handling in python
		utf8 = utf16.encode('utf-8', 'replace')
		
		if (sys.version_info > (3, 0)):
		    return str(utf8[:-1].decode())
		else:
		    return str(utf8[:-1])
			
	def getAllRecords(self):
		return self.contents[self.data_start_point:self.third_start_point]
		
	def getThirdSegment(self):
		return self.contents[self.third_start_point:]

#a few more binary utilities...

#Reads a certain number of bits starting from an offset byte and bit and returns the value
def readbits(text, offsetbyte, offsetbit, numbits):
	if (sys.version_info > (3, 0)):
		bytes = [b for b in text[offsetbyte:offsetbyte+4]]
	else:
		bytes = [ord(b) for b in text[offsetbyte:offsetbyte+4]]
	val = 0
	if (sys.version_info > (3, 0)):
		for i in reversed(range(4 if len(bytes) > 4 else len(bytes))):
			val *= 256
			val += bytes[i]
	else:
		for i in reversed(xrange(4 if len(bytes) > 4 else len(bytes))):
			val *= 256
			val += bytes[i]
	val >>= offsetbit
	val &= (1 << numbits) -1
	return val

def readbyte(text, offsetbyte):
	if (sys.version_info > (3, 0)):
		return text[offsetbyte]
	else:
		return ord(text[offsetbyte])
	
def readfloat(text, startbyte, roundTo=2): #expects a 4 byte float
	return round(unpack("f", text[startbyte:startbyte+4])[0],roundTo)

#Checks the first 2 bytes of a file and returns the value
def getnumentries(filename):
	file = open(filename, "rb")
	contents = file.read()
	numentries = readbits(contents, 0, 0, 32)
	file.close()
	return numentries

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
		pokemonabilitylist = [""] #to prevent calling this function again

