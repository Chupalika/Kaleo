#!/usr/bin/python
# -*- coding: utf-8 -*-

#THINGS TO NOTE:
#- One Chance a Day! stages will not grab the correct messages
#- Start-of-Month Challenges and Mid-month Challenges will not grab the correct messages
#- Safari stage and pokemon info are unable to be datamined at the moment, so the tables need to be manually filled in
#- Competitive Stage rewards and tiers are unable to be datamined at the moment, so the tables are a set output because they don't usually change (the mega stone still needs to be changed though), but just be aware of this
#- Mega Pokemon's Mega Powers and Competitive Stage items are unable to be datamined at the moment, so they need to be manually filled in
#- For Escalation Battles, the event data points to the wrong stage for some reason, so Pokemon data will be incorrect and should be changed
#- First clear rewards won't be included for now

from __future__ import division

import sys, os.path
import datetime
import pytz
sys.path.append("../")
from pokemoninfo import *
from stageinfo import *
from miscdetails import *
from bindata import *

dropitems = {"1":"RML", "2":"LU", "3":"EBS", "4":"EBM", "5":"EBL", "6":"SBS", "7":"SBM", "8":"SBL", "9":"SS", "10":"MSU", "23":"10 Hearts", "24":"100 Coins", "25":"300 Coins", "27":"2000 Coins", "30":"5000 Coins", "32":"PSB"}

def generateDrops(stageRecord):
	dropStr = ""
	
	if stageRecord.drop1item == 0:
		return ""
	
	try:
		drop1item = dropitems[str(stageRecord.drop1item)]
	except KeyError:
		drop1item = str(stageRecord.drop1item)
	try:
		drop2item = dropitems[str(stageRecord.drop2item)]
	except KeyError:
		drop2item = str(stageRecord.drop2item)
	try:
		drop3item = dropitems[str(stageRecord.drop3item)]
	except KeyError:
		drop3item = str(stageRecord.drop3item)
	
	if stageRecord.drop1item == stageRecord.drop2item and stageRecord.drop2item == stageRecord.drop3item:
		dropStr += "Drop | Rate #1 | Rate #2 | Rate #3\n-|-|-|-\n"
		dropStr += "{} | {}% | {}% | {}%\n".format(drop1item, str(1/pow(2,stageRecord.drop1rate-1)*100), str(1/pow(2,stageRecord.drop2rate-1)*100), str(1/pow(2,stageRecord.drop3rate-1)*100))
	else:
		dropStr += "Drop #1 | Drop #2 | Drop #3\n-|-|-\n"
		dropStr += "{} - {}% | {} - {}% | {} - {}%\n".format(drop1item, str(1/pow(2,stageRecord.drop1rate-1)*100), drop2item, str(1/pow(2,stageRecord.drop2rate-1)*100), drop3item, str(1/pow(2,stageRecord.drop3rate-1)*100)) 
		
	return dropStr  


appfolder = sys.argv[1]
extfolder = sys.argv[2]
if len(sys.argv) < 4:
	startindex = 1 #do 'em all. gulp
else:
	startindex = int(sys.argv[3])
BinStorage.workingdirs["ext"] = os.path.abspath(extfolder)
BinStorage.workingdirs["app"] = os.path.abspath(appfolder)

sdata = StageData("Configuration Tables/stageData.bin")


print "Stage | Pokémon | Type | Base Power | Ability | Turns | HP | Catch Rate | Drop Rate | Notes"
print "-|-|-|-|-|-|-|-|-|-"

for index in range(startindex, len(sdata.records)):
	stage_record = sdata.getStageInfo(index)
	swapstring = " / ".join(["*"+abil+"*" for abil in stage_record.pokemon.ss])
	if swapstring != '':
		swapstring = " / " + swapstring
	notes = ""
	if stage_record.numsupports == 3:
		notes = "**3-mon stage.**"
		
	stage_supports = StageDefaultSupports.getSupportNames(stage_record.defaultsetindex, stage_record.numsupports)
		
	if stage_record.numsupports == 5:
		notes = "**5th support: {}.**".format(stage_supports[0])
	elif stage_supports[0] == "Rock" or stage_supports[0] == "Block":
		notes += " If you leave {}{} support empty, {}s are added.".format(stage_record.numsupports, "rd" if stage_record.numsupports == 3 else "th", stage_supports[0].lower())
		
	
	print "{} | {} | {} | {} | {} | {} | {} | {}% + {}%/move | {} | {}".format(stage_record.index, stage_record.pokemon.name+(" ({})".format(stage_record.pokemon.modifier) if stage_record.pokemon.modifier != "" else ""), stage_record.pokemon.type, stage_record.pokemon.bp, stage_record.pokemon.ability+swapstring, stage_record.moves, stage_record.hp, stage_record.basecatch, stage_record.bonuscatch, "{:g}% / {:g}% / {:g}%".format((1/pow(2,stage_record.drop1rate-1))*100, (1/pow(2,stage_record.drop2rate-1))*100, (1/pow(2,stage_record.drop3rate-1))*100) if stage_record.drop1item != 0 else "-", notes)