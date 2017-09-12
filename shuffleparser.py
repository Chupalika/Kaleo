#!/usr/bin/python
from __future__ import division

import sys
from pokemoninfo import *
from stageinfo import *
import layoutimagegenerator

def main(args):
	#make sure correct number of arguments
	if len(args) < 2:
		print 'need 2 arguments: datatype, index'
		sys.exit()
	
	#parse arguments
	datatype = args[0]
	index = args[1]
	extra = ""
	if (len(args) >= 3):
		extra = args[2]
	
	try:
		if datatype == "stage":
			sdata = StageData("stageData.bin")
			if index == "all":
				sdata.printalldata(mobile=extra)
			else:
				sdata.printdata(int(index), mobile=extra)
		
		elif datatype == "expertstage":
			sdata = StageData("stageDataExtra.bin")
			if index == "all":
				sdata.printalldata(mobile=extra)
			else:
				sdata.printdata(int(index), mobile=extra)
		
		elif datatype == "eventstage":
			sdata = StageData("stageDataEvent.bin")
			if index == "all":
				sdata.printalldata(mobile=extra)
			else:
				sdata.printdata(int(index), mobile=extra)
				
		elif datatype == "layout":
			ldata = StageLayout("stageLayout.bin")
			if index == "all":
				ldata.printalldata(generatelayoutimage=extra)
			else:
				ldata.printdata(int(index), generatelayoutimage=extra)
				
		elif datatype == "expertlayout":
			ldata = StageLayout("stageLayoutExtra.bin")
			if index == "all":
				ldata.printalldata(generatelayoutimage=extra)
			else:
				ldata.printdata(int(index), generatelayoutimage=extra)
				
		elif datatype == "eventlayout":
			ldata = StageLayout("stageLayoutEvent.bin")
			if index == "all":
				ldata.printalldata(generatelayoutimage=extra)
			else:
				ldata.printdata(int(index), generatelayoutimage=extra)
				
		elif datatype == "pokemon":
			if index == "all":
				PokemonData.printalldata()
			else:
				PokemonData.printdata(int(index))
		
		elif datatype == "ability":
			if index == "all":
				PokemonAbility.printalldata()
			else:
				PokemonAbility.printdata(int(index))
		
		else:
			sys.stderr.write("datatype should be stage, expertstage, eventstage, layout, expertlayout, eventlayout, pokemon, or ability\n")
	except IOError:
		sys.stderr.write("Couldn't find the bin file to extract data from.\n")
		raise

if __name__ == "__main__":
	main(sys.argv[1:])
