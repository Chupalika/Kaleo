# -*- coding: utf_8 -*-

#!/usr/bin/python

import sys, os.path
sys.path.append("../")
from bindata import *

#Compares entries of binary files, searching for specific values
#Usage: python bincompare.py appdatafolder extdatafolder [entry_indexes] [entry_values] [bit_sizes]
#Example: python bincompare.py appdatafolder extdatafolder eventStage.bin 10,34,35 20000,1,1 16
#- appdatafolder is the folder that holds data extracted from the app itself
#- extdatafolder is the folder that holds data extracted from downloaded extra data (aka update data)
#- binfile is the file that will be analyzed (folder forced to Configuration Tables)
#- entry_indexes contains the index(es) of the data extracted from the file (comma separated)
#- entry_values contains the value(s) to search in the correspondent entry (comma separated)
#- bit_sizes contains the possible sizes of the searched values (comma separated)

class BinStorageCompare(BinStorage):
	def compare(self, indexes, values, bits):
		if not isinstance(indexes, list): indexes = [indexes]
		if not isinstance(values, list): values = [values]
		if not isinstance(bits, list): bits = [bits]
		bits.sort(reverse = True)
		values += [values[-1]] * len(indexes)
		print "Looking for entries {} with values {} and length {} bits...".format(indexes, values[: len(indexes)], bits)
		snippets = [self.getRecord(i) for i in indexes]
		results = []
		for i in range(0, len(snippets[0])):
			for j in range(8):
				isduplicate = False
				for b in bits:
					if isduplicate: break
					found = True
					for k in range(0, len(indexes)):
						if values[k] != readbits(snippets[k], i, j, b):
							found = False
							break
					if found:
						results.append([i, j, b])
						isduplicate = True
		if len(results) > 0:
			print "Found {} combination(s)!".format(len(results))
			for r in results: print "\tbyte {}-{}, {} bits".format(r[0], r[1], r[2])
		else: print "No results found!"
		return results

BinStorageCompare.workingdirs["ext"] = os.path.abspath(sys.argv[2])
BinStorageCompare.workingdirs["app"] = os.path.abspath(sys.argv[1])
try:
	bsc = BinStorageCompare("Configuration Tables" + os.sep + sys.argv[3])
	bsc.compare(map(int, sys.argv[4].split(",")), map(int, sys.argv[5].split(",")), map(int, sys.argv[6].split(",")))
except IOError:
	sys.stderr.write("Couldn't find the bin file to extract data from.\n")
	raise
