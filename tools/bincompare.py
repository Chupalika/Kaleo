#!/usr/bin/python

# -*- coding: utf_8 -*-

import sys, os.path
sys.path.append(".."+os.sep)
from bindata import *

#Tool used to compare entries of binary files, search for specific values and show raw data
#Usage: python bincompare.py <command="compare", "cross" or "show">
#Command = compare: appdatafolder extdatafolder binfile [entry_indexes] [entry_values] [bit_sizes]
#Example: python bincompare.py compare appdatafolder extdatafolder eventStage.bin 10,34,35 20000,1,1 16
#- appdatafolder is the folder that holds data extracted from the app itself
#- extdatafolder is the folder that holds data extracted from downloaded extra data (aka update data)
#- binfile is the file that will be analyzed (folder forced to Configuration Tables)
#- entry_indexes contains the index(es) of the data extracted from the file (comma separated)
#- entry_values contains the value(s) to search in the correspondent entry (comma separated)
#- bit_sizes contains the possible sizes of the searched values (comma separated) or the "float" string
#Command = cross: appdatafolder extdatafolder appdatafolder2 extdatafolder2 binfile location_byte location_bit bit_size
#Example: python bincompare.py cross appdatafolder extdatafolder appdatafolder2 extdatafolder2 stageData.bin 73 5 3
#- appdatafolder is the folder that holds data extracted from the app itself (the one with unknwon locations)
#- extdatafolder is the folder that holds data extracted from downloaded extra data (the one with unknwon locations)
#- appdatafolder2 is the folder that holds data extracted from the app itself (the one you know the locations)
#- extdatafolder2 is the folder that holds data extracted from downloaded extra data (the one you know the locations)
#- binfile is the file that will be analyzed (folder forced to Configuration Tables)
#- location_byte is the location of the field to search
#- location_bit is the starting bit shift of that location
#- bit_sizes is the size of the data
#Command = show: appdatafolder extdatafolder binfile entry_index
#Example: python bincompare.py show appdatafolder extdatafolder stageData.bin 700
#- appdatafolder is the folder that holds data extracted from the app itself
#- extdatafolder is the folder that holds data extracted from downloaded extra data (aka update data)
#- binfile is the file that will be analyzed (folder forced to Configuration Tables)
#- entry_index is the index of the data

def read_qword(text, offsetbyte):
	if (sys.version_info > (3, 0)):
		bytes = [b for b in text[offsetbyte:offsetbyte+8]]
	else:
		bytes = [ord(b) for b in text[offsetbyte: offsetbyte + 8]]
	val = 0
	if (sys.version_info > (3, 0)):
		for i in reversed(range(8 if len(bytes) > 8 else len(bytes))):
			val *= 256
			val += bytes[i]
	else:
		for i in reversed(xrange(8 if len(bytes) > 8 else len(bytes))):
			val *= 256
			val += bytes[i]
	val &= (1 << 64) -1
	return val

def read_qword(text, offsetbyte):
	bytes = [ord(b) for b in text[offsetbyte: offsetbyte + 8]]
	val = 0
	for i in reversed(xrange(8 if len(bytes) > 8 else len(bytes))):
		val *= 256
		val += bytes[i]
	val &= (1 << 64) - 1
	return val

class BinStorageCompare(BinStorage):
	def compare(self, indexes, values, bits, verbose=True):
		usefloat = bits == "float"
		if usefloat:
			bits = [32]
			startbits = [0]
		else: startbits = list(range(8))
		if not isinstance(indexes, list): indexes = [indexes]
		if not isinstance(values, list): values = [values]
		if not isinstance(bits, list): bits = [bits]
		bits.sort(reverse = True)
		values += [values[-1]] * len(indexes)
		if verbose: print("Looking for entries {} with values {} and length {} bits in {} mode...".format(indexes, values[: len(indexes)], bits, ["int", "float"][usefloat]))
		snippets = [self.getRecord(i) for i in indexes]
		results = []
		for i in range(len(snippets[0])):
			for j in startbits:
				isduplicate = False
				for b in bits:
					if isduplicate: break
					found = True
					for k in range(len(indexes)):
						if len(snippets[k]) > 0:
							if usefloat:
								try:
									if abs(values[k] - readfloat(snippets[k], i)) > 0.001:
										found = False
										break
								except:
									found = False
									break
							elif values[k] != readbits(snippets[k], i, j, b):
								found = False
								break
					if found:
						results.append([i, j, b])
						isduplicate = True
		if verbose:
			if len(results) > 0:
				print("\tFound {} location(s)!".format(len(results)))
				for r in results: print("\t\tbyte {}-{}, {} bits".format(r[0], r[1], r[2]))
			else: print("\tNo results found!")
		return results
	def cross_struct_compare(self, bs, loc_byte, loc_bit, bits = 8, value_shift = 0):
		usefloat = bits == "float"
		print("Looking for data compatible with location {}-{} with length {} bits in {} mode...".format(loc_byte, loc_bit, [bits, 32][usefloat], ["int", "float"][usefloat]))
		count = min(self.num_records, bs.num_records)
		if usefloat: results = self.compare(list(range(count)), [readfloat(bs.getRecord(i), loc_byte) + value_shift for i in range(count)], bits, False)
		else: results = self.compare(list(range(count)), [readbits(bs.getRecord(i), loc_byte, loc_bit, bits) + value_shift for i in range(count)], bits, False)
		if len(results) == 1:
			if results[0][0] == loc_byte and results[0][1] == loc_bit: print("\tOne location found in the same position!")
			else: print("\tOne location found in a new position! {}-{}".format(results[0][0], results[0][1]))
		elif len(results) > 1:
			print("\tFound {} locations, a manual search is suggested!".format(len(results)))
			if len(results) <= 5:
				for r in results: print("\t\tbyte {}-{}, {} bits".format(r[0], r[1], r[2]))
		else: print("\tNo results found!")
		return results
	def show_bytes(self, index):
		snippet = self.getRecord(index - 1) + self.getRecord(index) + self.getRecord(index + 1)
		size = len(self.getRecord(index))
		print("Struct size is {} bytes.\nDWORDs contained in entry {}:".format(size, index))
		for i in range(0, len(self.getRecord(index)) - 1, 4): print("\t{}\t{}".format(i, readbits(snippet, size + i, 0, 32)))
		print("QWORDs contained in entry {}:".format(index))
		for i in range(0, len(self.getRecord(index)) - 1, 8): print("\t{}\t{}".format(i, read_qword(snippet, size + i)))
		print("QWORDs (shifted -4) contained in entry {}:".format(index))
		for i in range(-4, len(self.getRecord(index)) - 5, 8): print("\t{}\t{}".format(i, read_qword(snippet, size + i)))

try:
	if sys.argv[1].lower() == "cross":
		BinStorageCompare.workingdirs["ext"] = os.path.abspath(sys.argv[3])
		BinStorageCompare.workingdirs["app"] = os.path.abspath(sys.argv[2])
		bsc = BinStorageCompare("Configuration Tables" + os.sep + sys.argv[6])
		BinStorage.workingdirs["ext"] = os.path.abspath(sys.argv[5])
		BinStorage.workingdirs["app"] = os.path.abspath(sys.argv[4])
		BinStorage.pathUsed = ""
		bs = BinStorage("Configuration Tables" + os.sep + sys.argv[6])
		bsc.cross_struct_compare(bs, int(sys.argv[7]), int(sys.argv[8]), [int(sys.argv[9]), "float"][sys.argv[9].lower() == "float"])
	elif sys.argv[1].lower() == "show":
		BinStorageCompare.workingdirs["ext"] = os.path.abspath(sys.argv[3])
		BinStorageCompare.workingdirs["app"] = os.path.abspath(sys.argv[2])
		bsc = BinStorageCompare("Configuration Tables" + os.sep + sys.argv[4])
		bsc.show_bytes(int(sys.argv[5]))
	else:
		BinStorageCompare.workingdirs["ext"] = os.path.abspath(sys.argv[3])
		BinStorageCompare.workingdirs["app"] = os.path.abspath(sys.argv[2])
		bsc = BinStorageCompare("Configuration Tables" + os.sep + sys.argv[4])
		if sys.argv[7].lower() == "float": bsc.compare(list(map(int, sys.argv[5].replace(" ","").split(","))), list(map(float, sys.argv[6].replace(" ","").split(","))), "float")
		else: bsc.compare(list(map(int, sys.argv[5].replace(" ","").split(","))), list(map(int, sys.argv[6].replace(" ","").split(","))), list(map(int, sys.argv[7].replace(" ","").split(","))))
except IOError:
	sys.stderr.write("Couldn't find the bin file to extract data from.\n")
	raise
