#!/usr/bin/python

#Reads binary files that are unpacked from Pokemon Shuffle game archives, parses requested data, and prints them out in a readable format
#Usage: python shuffleparser.py appdatafolder extdatafolder datatype index extraflag
#- appdatafolder is the folder that holds data extracted from the app itself
#- extdatafolder is the folder that holds data extracted from downloaded extra data (aka update data)
#- possible datatypes: stage, expertstage, eventstage, layout, expertlayout, eventlayout, pokemon, ability, escalationanger, items, eventdetails, escalationrewards, eventstagerewards, stagerewards
#- index is used for stage data, stage layouts, pokemon data, and ability data. It can be an integer or the keyword "all".
#- extraflag is optional: l to enable layout image generation, m to switch to parsing mobile stage data

from __future__ import division
import sys, os.path
from pokemoninfo import *
from stageinfo import *
from bindata import *
import layoutimagegenerator

#Item rewards from stages
itemrewards = {"0":"Moves +5", "1":"Time +10", "3":"Mega Start", "6":"Disruption Delay", "8":"Mega Speedup", "13":"Raise Max Level", "14":"Level Up", "15":"Exp. Booster S", "16":"Exp. Booster M", "17":"Exp. Booster L", "18":"Skill Booster S", "19":"Skill Booster M", "20":"Skill Booster L", "21":"Skill Swapper"}
def itemreward(itemtype, itemid):
    if itemtype == 1:
        item = "Jewel"
    elif itemtype == 2:
        item = "Heart"
    elif itemtype == 3:
        item = "Coin"
    elif itemtype == 4:
        try:
            item = itemrewards[str(itemid)]
        except KeyError:
            item = "Item {}".format(itemid)
    elif itemtype == 5:
        pokemonrecord = PokemonData.getPokemonInfo(itemid+1093)
        item = pokemonrecord.name
    else:
        item = "Item Type {}".format(itemtype)
    return item

def main(args):
	#make sure correct number of arguments
	if len(args) < 3:
		print "3-5 arguments: appdatafolder, extdatafolder, datatype, index, extraflag"
		print "- possible datatypes: stage, expertstage, eventstage, layout, expertlayout, eventlayout, pokemon, ability, escalationanger, items, eventdetails, escalationrewards, eventstagerewards, stagerewards"
		print "- index is optional with some datatypes, it can be an integer or the keyword all"
		print "- extraflag is optional: l to enable layout image generation, m to switch to parsing mobile stage data (which is incomplete at the moment)"
		print "- items doesn't print anything useful at the moment"
		sys.exit()
	
	#parse arguments
	appfolder = args[0]
	extfolder = args[1]
	BinStorage.workingdirs["ext"] = os.path.abspath(extfolder)
	BinStorage.workingdirs["app"] = os.path.abspath(appfolder)
	datatype = args[2]
	if (len(args) >= 4):
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
				
		elif datatype == "escalationanger":
			escBin = BinStorage("Configuration Tables/escalationSkipChance.bin")
			for record in range(escBin.num_records):
				thisRecord = escBin.getRecord(record)
				print "[{}, {}]".format(readbits(thisRecord, 0, 0, 4), readfloat(thisRecord, 4))
			print "Note that '15' is supposed to be '-1'. It's a signed/unsigned thing."
		
		elif datatype == "items":
		    itemBin = BinStorage("Configuration Tables/itemPattern.bin")
		    for i in range(itemBin.num_records):
		        record = itemBin.getRecord(i)
		        print "[{}, {}, {}, {}, {}, {}, {}, {}]".format(readbyte(record, 0), readbyte(record, 1), readbyte(record, 2), readbyte(record, 3), readbyte(record, 4), readbyte(record, 5), readbyte(record, 6), readbyte(record, 7))
		
		elif datatype == "eventdetails":
		    sdata = StageData("Configuration Tables/stageDataEvent.bin")
		    eventBin = BinStorage("Configuration Tables/eventStage.bin")
		    for i in range(eventBin.num_records):
		        record = eventBin.getRecord(i)
		        
		        stagetype = readbits(record, 1, 0, 4) #1:normal, 2:daily, 3:???, 4:meowth, 5:comp, 6:EB, 7:safari, 8:itemstage
		        stageindex = readbyte(record, 4)
		        stage = sdata.getStageInfo(stageindex)
		        stagepokemon = stage.pokemon.fullname
		        
		        if stagetype == 2:
		            stageindexes = [readbyte(record, i) for i in [4,8,12,16,20,24,28]]
		            stagepokemon = []
		            entries = 0
		            for stageindex in stageindexes:
		                if stageindex == 255:
		                    continue
		                else:
		                    stage = sdata.getStageInfo(stageindex)
		                    stagepokemon.append(stage.pokemon.fullname)
		                    entries += 1
		            
		            dailystring = ""
		            for i in range(entries):
		                dailystring += " {} (stage index {})".format(stagepokemon[i], stageindexes[i])
		        if stagetype == 7:
		            stagepokemon = "SAFARI"
		        
		        startyear = readbits(record, 48, 0, 6)
		        startmonth = readbits(record, 48, 6, 4)
		        startday = readbits(record, 49, 2, 5)
		        starthour = readbits(record, 49, 7, 5)
		        startminute = readbits(record, 50, 4, 6)
		        endyear = readbits(record, 51, 2, 6)
		        endmonth = readbits(record, 52, 0, 4)
		        endday = readbits(record, 52, 4, 5)
		        endhour = readbits(record, 53, 1, 5)
		        endminute = readbits(record, 53, 6, 6)
		        
		        triesavailable = readbits(record, 1, 4, 4)
		        unlockcosttype = readbits(record, 73, 0, 4)
		        unlockcost = readbits(record, 76, 0, 16)
		        unlocktimes = readbits(record, 98, 0, 4)
		        
		        if startminute == 0:
		            startminute = "00"
		        if endminute == 0:
		            endminute = "00"
		        
		        if unlockcosttype == 0:
		            unlockcosttype = "Coin"
		        elif unlockcosttype == 1:
		            unlockcosttype = "Jewel"
		        else:
		            unlockcosttype = "???"
		        
		        if stagetype == 2:
		            print "DAILY:{}".format(dailystring)
		            print "Event Duration: {}/{}/{} {}:{} to {}/{}/{} {}:{}".format(startmonth, startday, startyear, starthour, startminute, endmonth, endday, endyear, endhour, endminute)
		        else:
		            print "{} (stage index {})".format(stagepokemon, stageindex)
		            print "Event Duration: {}/{}/{} {}:{} to {}/{}/{} {}:{}".format(startmonth, startday, startyear, starthour, startminute, endmonth, endday, endyear, endhour, endminute)
		            if unlockcost != 0 and stagetype != 7:
		                print "Costs {} {}(s) to unlock {} time(s)".format(unlockcost, unlockcosttype, unlocktimes)
		            if triesavailable != 0 and stagetype != 7:
		                print "Stage is available to attempt {} times before it disappears".format(triesavailable)
		        print
		
		elif datatype == "escalationrewards":
		    EBrewardsBin = BinStorage("Configuration Tables/stagePrizeEventLevel.bin")
		    for i in range(EBrewardsBin.num_records):
		        record = EBrewardsBin.getRecord(i)
		        level = readbits(record, 8, 0, 16)
		        if level == 0:
		            continue
		        itemtype = readbyte(record, 12)
		        itemid = readbyte(record, 16)
		        itemamount = readbits(record, 20, 0, 16)
		        item = itemreward(itemtype, itemid)
		        
		        print "Level {} reward: {} x{}".format(level, item, itemamount)
		
		elif datatype == "eventstagerewards":
		    eventrewardsBin = BinStorage("Configuration Tables/stagePrizeEvent.bin")
		    for i in range(eventrewardsBin.num_records):
		        record = eventrewardsBin.getRecord(i)
		        stageindex = readbits(record, 4, 0, 16)
		        if stageindex == 0:
		            continue
		        
		        itemtype = readbyte(record, 8)
		        itemid = readbyte(record, 12)
		        itemamount = readbits(record, 16, 0, 16)
		        item = itemreward(itemtype, itemid)
		        
		        itemtype2 = readbyte(record, 32)
		        itemid2 = readbyte(record, 36)
		        itemamount2 = readbits(record, 40, 0, 16)
		        item2 = itemreward(itemtype2, itemid2)
		        
		        rewardstring = "{} x{}".format(item, itemamount)
		        if itemamount2 != 0:
		            rewardstring += " + {} x{}".format(item2, itemamount2)
		        print "Stage Index {} reward: ".format(stageindex) + rewardstring
		
		elif datatype == "stagerewards":
		    rewardsBin = BinStorage("Configuration Tables/stagePrize.bin")
		    for i in range(rewardsBin.num_records):
		        record = rewardsBin.getRecord(i)
		        stageindex = readbits(record, 4, 0, 16)
		        if stageindex == 0:
		            continue
		        
		        itemtype = readbyte(record, 8)
		        itemid = readbyte(record, 12)
		        itemamount = readbits(record, 16, 0, 16)
		        item = itemreward(itemtype, itemid)
		        
		        itemtype2 = readbyte(record, 32)
		        itemid2 = readbyte(record, 36)
		        itemamount2 = readbits(record, 40, 0, 16)
		        item2 = itemreward(itemtype2, itemid2)
		        
		        rewardstring = "{} x{}".format(item, itemamount)
		        if itemamount2 != 0:
		            rewardstring += " + {} x{}".format(item2, itemamount2)
		        print "Stage Index {} reward: ".format(stageindex) + rewardstring
		
		else:
			sys.stderr.write("datatype should be one of these: stage, expertstage, eventstage, layout, expertlayout, eventlayout, pokemon, ability, escalationanger, items, eventdetails, escalationrewards, eventstagerewards, stagerewards\n")
	except IOError:
		sys.stderr.write("Couldn't find the bin file to extract data from.\n")
		raise

if __name__ == "__main__":
	main(sys.argv[1:])
