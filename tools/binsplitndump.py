#!/usr/bin/python

from sys import argv, exit
import os, os.path
import io
from struct import unpack_from as unpack
from math import log10

def read_int(file,start=None):
	global file_pointer
	if start is None:
		start = file_pointer
		file_pointer += 4
	return unpack("<I",file[start:start+4])[0]
		
def read_data(file,lenR,start=None):
	global file_pointer
	if start is None:
		start = file_pointer
		file_pointer += lenR
	return file[start:start+lenR]


if len(argv) < 2:
	print "Sorry, I need a file to dump."
	exit(1)
	
for file in argv[1:]:
	if not os.access(file, os.R_OK):
		print "Can't read the file path '"+file+"'. Skipping."
		continue

	if os.path.isdir(file):
		print "'' is a directory. Skipping."
		continue
	
	_, short_filename = os.path.split(file)
	
	try:
		os.mkdir(short_filename+" dumps") #make output dir, fail silently if it's already here.	
	except OSError:
		pass
	
		
	with io.open(file, mode='rb') as file_to_dump:
		file_contents = file_to_dump.read()
		
	os.chdir(short_filename+" dumps")
		
	file_pointer = 0
	
	num_records = read_int(file_contents)
	record_digits = int(log10(num_records))+1
	record_length = read_int(file_contents)
	
	file_pointer += 8
	
	start_point = read_int(file_contents)
	
	filename_format_string = "{}_{:0"+str(record_digits)+"d}.bin"
	print filename_format_string
	#+.bind for binary dump
	
	for record in range(num_records):
		this_record = read_data(file_contents,record_length,start=start_point+record*record_length)
		
		this_filename = filename_format_string.format(short_filename[:-4],record)
		
		with io.open(this_filename, mode='wb') as record_file:
			record_file.write(this_record)
	
		this_output = ""	
	
		for char in this_record:
			equiv_int = ord(char)
		
			indx = 128
			while indx > 0:
				this_output += str(equiv_int / indx)
				equiv_int %= indx 
				indx /= 2
		
			this_output += " "
		
		
		with io.open(this_filename+".bind", mode='wb') as dumpfile:
			dumpfile.write(this_output)
	
		print "Wrote '"+this_filename+".bind'."