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
sys.path.append(".."+os.sep)
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
BinStorage.workingdirs["ext"] = os.path.abspath(extfolder)
BinStorage.workingdirs["app"] = os.path.abspath(appfolder)

sdata = StageData("Configuration Tables"+os.sep+"stageDataEvent.bin")
eventBin = BinStorage("Configuration Tables"+os.sep+"eventStage.bin")
messagestemp = BinStorage("Message_US"+os.sep+"messageEventStage_US.bin")

#grab the messages, ignore the ones that are titles (they won't have double breaks like the other messages will (hopefully) always have)
messages = []
for index in range(messagestemp.num_records):
	message = messagestemp.getMessage(index)
	splitindex = message.find("\n\n")
	if splitindex == -1:
		continue
	#replace all breaks with spaces
	message.replace("\n", " ")
	#correct some funky characters
	message = message.replace(chr(145), "↑")
	message = message.replace(chr(233), "é")
	messages.append(message)

#this will hold the markup text for each event entry
entries = []

#for each entry in events...
for i in range(eventBin.num_records):
	snippet = eventBin.getRecord(i)
	record = EventDetails(i, snippet, sdata)
	
	#skip the weekly stuff
	if record.stagepokemon in ["Victini", "Magearna", "Meowth", "Meowth (Alola Form)", "Eevee", "Wobbuffet (Male)", "Wobbuffet (Female)", "Carnivine", "Oranguru", "Passimian"]:
		continue
	
	#datetime stuff
	timezone = pytz.timezone("Japan")
	starttime = datetime.datetime(record.startyear + 2000, record.startmonth, record.startday, record.starthour, record.startminute)
	starttime = timezone.localize(starttime).astimezone(pytz.timezone("UTC"))
	starttimestring = starttime.strftime("%Y-%m-%d %H:%M UTC")
	endtime = datetime.datetime(record.endyear + 2000, record.endmonth, record.endday, record.endhour, record.endminute)
	endtime = timezone.localize(endtime).astimezone(pytz.timezone("UTC"))
	endtimestring = endtime.strftime("%Y-%m-%d %H:%M UTC")
	duration = endtime - starttime
	if duration.days % 7 == 0:
		durationstring = "{} week{}".format(duration.days // 7, "s" if duration.days // 7 > 1 else "")
	else:
		durationstring = "{} days".format(duration.days)
	if duration.seconds != 0:
		hours = duration.seconds // 3600
		durationstring += ", {} hours".format(hours)
	
	#################
	# Normal Stages #
	#################
	if record.stagetype == 1:
		#find the message by looking for the pokemon name in the first line... this could use a better method
		THEmessage = ""
		for message in messages:
			splitindex = message.find("\n\n")
			firstline = message[0:splitindex]
			if firstline.find(record.stagepokemon) != -1:
				THEmessage = message
				break
		
		#the title might be different! but for the most part it's just "Pokemon Appears"
		entry = ""
		entry += "* **{} Appears**  \n".format(record.stagepokemon)
		entry += THEmessage + "\n\n"
		
		entry += "**Event Period**: {} to {} ({})\n\n".format(starttimestring, endtimestring, durationstring)
		
		#pokemon data table
		entry += "Pokémon | Type | BP | Skill | Attempt Cost | {} | HP | Catch Rate\n-|-|-|-|-|-|-|-\n".format("Moves" if record.stage.timed == 0 else "Time")
		pokemonindex = record.stage.pokemonindex
		untimed = (record.stage.timed == 0)
		pdata = PokemonData.getPokemonInfo(pokemonindex)
		swapstring = " / ".join(["*"+abil+"*" for abil in pdata.ss])
		if swapstring != '':
			swapstring = " / " + swapstring
		entry += "{} | {} | {} | {} | {} {}{} | {} | {} | {}% + {}%/{} \n\n".format(pdata.fullname, pdata.type, pdata.bp, pdata.ability+swapstring, record.stage.attemptcost, ["Heart", "Coin"][record.stage.costtype], "s" if record.stage.attemptcost != 1 else "", record.stage.moves if untimed else str(record.stage.seconds // 60) + ":" + str(record.stage.seconds % 60), record.stage.hp,record.stage.basecatch, record.stage.bonuscatch, "move" if untimed else "3sec")
		
		entry += generateDrops(record.stage)
		
		#stage data table
		
		entries.append(entry)
	
	###########
	# Dailies #
	###########
	#assuming dailies are never timed and always cost 1 heart
	elif record.stagetype == 2:
		#find the message by looking for Daily in the first line... this could use a better method
		#one chance a day stages will grab the wrong message here
		THEmessage = ""
		for message in messages:
			splitindex = message.find("\n\n")
			firstline = message[0:splitindex]
			if firstline.find("Daily") != -1:
				THEmessage = message
				break
		
		#title
		entry = ""
		entry += "* **Daily Pokémon Are Here!**  \n"
		entry += THEmessage + "\n\n"
		
		entry += "**Event Period**: {} to {} ({})\n\n".format(starttimestring, endtimestring, durationstring)
		
		entry += "Day | Pokémon | Type | BP | Skill | Moves | HP | Catch Rate | Notes\n-|-|-|-|-|-|-|-|-\n"
		
		#pokemon + stage data table
		for i in range(len(record.stagepokemon)):
			day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][i]
			dailystage = record.stages[i]
			pokemonindex = dailystage.pokemonindex
			pdata = PokemonData.getPokemonInfo(pokemonindex)
			swapstring = " / ".join(["*"+abil+"*" for abil in pdata.ss])
			if swapstring != '':
				swapstring = " / " + swapstring
			entry += "{} | {} | {} | {} | {} | {} | {} | {}% + {}%/move | \n".format(day, pdata.fullname, pdata.type, pdata.bp, pdata.ability+swapstring, dailystage.moves, dailystage.hp, dailystage.basecatch, dailystage.bonuscatch)
		entry += "\n"
		
		#drop rates table
		dailystage = record.stages[0]
		entry += generateDrops(record.stages[0])
		
		entries.append(entry)
	
	################
	# Competitions #
	################
	#competitive stages
	#assuming comp stages are never timed and always cost 1 heart
	#there'll be three entries, one for each region
	#rewards and tiers can't be datamined yet, so the table is preset (since they don't usually change) (mega stones should be filled in maually)
	#mega power also can't be datamined yet, so that needs to be manually filled in
	elif record.stagetype == 5:
		#find the message by looking for the pokemon name in the first line... this could use a better method
		THEmessage = ""
		for message in messages:
			splitindex = message.find("\n\n")
			firstline = message[0:splitindex]
			if firstline.find(record.stagepokemon) != -1:
				THEmessage = message
				break
		
		#title
		entry = ""
		entry += "* **Competitive Stage Now Live!**  \n"
		entry += THEmessage + "\n\n"
		
		entry += "**Event Period**: {} to {} ({})\n\n".format(starttimestring, endtimestring, durationstring)
		
		#pokemon + stage data table
		entry += "Pokémon | Type | BP | Skill | Moves | Mega Power | Icons | Items\n-|-|-|-|-|-|-|-\n"
		megapokemonindex = record.stage.pokemonindex
		mpdata = PokemonData.getPokemonInfo(megapokemonindex)
		pdata = PokemonData.getPokemonInfo(mpdata.megaindex)
		swapstring = " / ".join(["*"+abil+"*" for abil in pdata.ss])
		if swapstring != '':
			swapstring = " / " + swapstring
		entry += "{} | {} | {} | {} | {} | {} | {}-{} ({} MSUs) | {} \n\n".format(mpdata.fullname, mpdata.type, pdata.bp, pdata.ability+swapstring, record.stage.moves, "Mega Power", mpdata.icons-mpdata.msu, mpdata.icons, mpdata.msu, "Items")
		
		#tiers and rewards table
		entry += """Tier | Prize | 3DS-NA | 3DS-EU | 3DS-JP | Mobile
-|-|-|-|-|-
1 | MegaStone, 5x MSU, 15x RML | 1-100 | 1 - 100 | 1 - 300 | 1-600
2 | MegaStone, 4x MSU, 10x RML | 101-300 | 101 - 200 | 301 - 1000 | 601-2000
3 | MegaStone, 4x MSU, 6x RML | 301-600 | 201 - 500 | 1001 - 2500 | 2001-5000
4 | MegaStone, 3x MSU, 4x RML | 601-1000 | 501 - 700 | 2501 - 4000 | 5001-8000
5 | MegaStone, 3x MSU, 2x RML | 1001-2100 | 701 - 1500 | 4001 - 8000 | 8001-16000
6 | MegaStone, 2x MSU, 1x RML | 2101-3600 | 1501 - 2600 | 8001 - 14000 | 16001-28000
7 | MegaStone, 1x MSU, 1x RML | 3601-5200 | 2601 - 3700 | 14001 - 20000 | 28001-40000
8 | MegaStone, 1x MSU, Mega Start | 5201-7800 | 3701 - 5600 | 20001 - 30000 | 40001-60000
9 | MegaStone, Mega Start, Moves+5 | 7801-10400 | 5601 - 7400 | 30001 - 40000 | 60001-80000
10 | Attack Power+, Moves+5, 3000 Coins | 10401-13000 | 7401 - 9300 | 40001 - 50000 | 80001-100000
11 | Attack Power+, 3000 Coins | 13001-16800 | 9301 - 12100 | 50001 - 65000 | 100001-130000
12 | 3000 Coins | 16801- | 12101- | 65001- | 130001-"""
		
		entries.append(entry)
	
	######################
	# Escalation Battles #
	######################
	#escalation battles
	#assuming EBs always cost 1 heart
	#for some reason eventdetails point to the incorrect stage, so pokemon info will be incorrect
	elif record.stagetype == 6:
		#find the message by looking for escalation in the first line... this could use a better method
		THEmessage = ""
		for message in messages:
			splitindex = message.find("\n\n")
			firstline = message[0:splitindex]
			if firstline.find("escalation") != -1:
				THEmessage = message
				break
		
		#title
		entry = ""
		entry += "* **Take on Escalation Battles!**  \n"
		entry += THEmessage + "\n\n"
		
		entry += "**Event Period**: {} to {} ({})\n\n".format(starttimestring, endtimestring, durationstring)
		
		#pokemon data table
		entry += "Pokémon | Type | BP | Skill \n-|-|-|-\n"
		pokemonindex = record.stage.pokemonindex
		pdata = PokemonData.getPokemonInfo(pokemonindex)
		swapstring = " / ".join(["*"+abil+"*" for abil in pdata.ss])
		if swapstring != '':
			swapstring = " / " + swapstring
		entry += "{} | {} | {} | {}\n\n".format(pdata.fullname, pdata.type, pdata.bp, pdata.ability+swapstring)
		
		#rewards table
		entry += "Level | Reward\n-|-\n"
		EBrewardsBin = BinStorage("Configuration Tables"+os.sep+"stagePrizeEventLevel.bin")
		ebrewards = EscalationRewards(EBrewardsBin)
		for e in ebrewards.entries:
			entry += "{} | {} {}{}\n".format(e["level"], e["itemamount"], e["item"], "s" if e["itemamount"] != 1 else "")
		
		entries.append(entry)
	
	###########
	# Safaris #
	###########
	#assuming safaris are never timed and always cost 1 heart
	#at the moment safari info can't be datamined so the tables will have to be manually filled out
	elif record.stagetype == 7:
		#find the message by looking for Safari in the first line... this could use a better method
		#start-of-month challenges will grab the wrong message here
		THEmessage = ""
		for message in messages:
			splitindex = message.find("\n\n")
			firstline = message[0:splitindex]
			if firstline.find("Safari") != -1:
				THEmessage = message
				break
		
		#title (if it's new, it'll say "A New Pokémon Safari!")
		entry = ""
		entry += "* **Head Back into the Safari!**  \n"
		entry += THEmessage + "\n\n"
		
		entry += "**Event Period**: {} to {} ({})\n\n".format(starttimestring, endtimestring, durationstring)
		
		#pokemon + stage data table
		entry += "Pokémon | Type | BP | Skill | Encounter Rate | Moves | HP | Catch Rate\n-|-|-|-|-|-|-|-\n"
		entry += "\n"
		
		#drop rates table
		entry += "Drop #1 | Drop #2 | Drop #3\n-|-|-\n"
		entry += "\n"
		
		entries.append(entry)

#print each entry!
for entry in entries:
	print(entry)
	print("----------------------------------------------------------------")