#!/usr/bin/python

from sys import argv, exit
from glob import glob
from bitstring import Bits
import os, os.path

def highlight(text):
	return '\x1b[6;30;42m' + text + '\x1b[0m' # this works on windows, not sure if it's portable

def hexDump(data, bitIndex, len):
	row = bitIndex - bitIndex % (16 * 8) # align on 16 bytes
	rowAddr = format(row / 8, '08x') # convert to bytes, as usually displayed in hex editors
	startAddr = format(bitIndex / 8, '08x')
	byteList = ''
	charList = ''
	for i in range(32):
		offset = row + i * 8
		byte = data[offset: offset + 8]
		byteList = byteList + (highlight(byte.hex + ' ') if offset >= bitIndex and offset < bitIndex + (len * 8) else byte.hex + ' ')
		charList = charList + (byte.tobytes() if byte.hex != '00' else '.')

	print "  {} {} {}  @{}".format(rowAddr, byteList, charList, startAddr)


if len(argv) < 3:
	print "Usage: hexsearch pattern files"
	print "	pattern can be hex (0x00ff) or binary (0b1100)"	
	exit(1)

pattern = argv[1].replace(' ', '') # findall handles spaces just fine but removing them makes calculating the length easier
patternLen = (len(pattern) - 2) / 2 # remove the 0x prefix and each byte is 2 characters

print 'Searching for pattern ' + pattern + ' of length ' + str(patternLen) + ' bytes'

for fileglob in argv[2:]:
	for file in glob(fileglob):
		if not os.access(file, os.R_OK):
			print "Can't read the file path '" + file + "'. Skipping."
			continue

		if os.path.isdir(file):
			print "'' is a directory. Skipping."
			continue
		
		f = open(file, "rb")
		s = Bits(f)
		results = list(s.findall(pattern, bytealigned=True)) # note the byte alignment

		if results:
			print 'Found match in ' + file
			for index in results:
				hexDump(s, index, patternLen)

print 'Done!'

