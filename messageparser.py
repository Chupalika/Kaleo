#!/usr/bin/python
from __future__ import division

import sys
from bindata import *

def main(args):
	#make sure correct number of arguments
	if len(args) < 2:
		print 'need 2 arguments: message file, index'
		sys.exit()
	
	#parse arguments
	msgfile = args[0]
	index = args[1]
	
	try:
		messages = BinStorage(msgfile, source=None) #the NONE prevents the path-changing code that normally handles path swapping from firing.
		if index == "all":
			for message in range(messages.num_records):
				print "Message {}:".format(message)
				print messages.getMessage(message)
				print
		else:
			print messages.getMessage(int(index))
		

	except IOError:
		sys.stderr.write("Couldn't find the bin file to extract data from.\n")
		raise

if __name__ == "__main__":
	main(sys.argv[1:])
