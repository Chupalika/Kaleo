#!/usr/bin/python
from __future__ import division

import sys, os.path
from pokemoninfo import *
from stageinfo import *
from bindata import *
import layoutimagegenerator

def main(args):
	#make sure correct number of arguments
	if len(args) < 4:
		print 'need 4 arguments: appdata folder, extdata folder, datatype, index'
		sys.exit()
	
	#parse arguments
	appfolder = args[0]
	extfolder = args[1]
	BinStorage.workingdirs["ext"] = os.path.abspath(extfolder)
	BinStorage.workingdirs["app"] = os.path.abspath(appfolder)
	datatype = args[2]
	index = args[3]
	extra = ""
	if (len(args) >= 5):
		extra = args[4]
	
	try:
		if datatype == "stage":
			sdata = StageData("Configuration Tables/stageData.bin")
			if index == "all":
				sdata.printalldata(mobile=extra)
			else:
				sdata.printdata(int(index), mobile=extra)
		
		elif datatype == "expertstage":
			sdata = StageData("Configuration Tables/stageDataExtra.bin")
			if index == "all":
				sdata.printalldata(mobile=extra)
			else:
				sdata.printdata(int(index), mobile=extra)
		
		elif datatype == "eventstage":
			sdata = StageData("Configuration Tables/stageDataEvent.bin")
			if index == "all":
				sdata.printalldata(mobile=extra)
			else:
				sdata.printdata(int(index), mobile=extra)
				
		elif datatype == "layout":
			ldata = StageLayout("Configuration Tables/stageLayout.bin")
			if index == "all":
				ldata.printalldata(generatelayoutimage=extra)
			else:
				ldata.printdata(int(index), generatelayoutimage=extra)
				
		elif datatype == "expertlayout":
			ldata = StageLayout("Configuration Tables/stageLayoutExtra.bin")
			if index == "all":
				ldata.printalldata(generatelayoutimage=extra)
			else:
				ldata.printdata(int(index), generatelayoutimage=extra)
				
		elif datatype == "eventlayout":
			ldata = StageLayout("Configuration Tables/stageLayoutEvent.bin")
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
