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

sdata = StageData("Configuration Tables/stageDataEvent.bin")
eventBin = BinStorage("Configuration Tables/eventStage.bin")
messagestemp = BinStorage("Message_US/messageEventStage_US.bin")

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
			swapstring += " / "
		entry += "{} | {} | {} | {} | {} {}{} | {} | {} | {}% + {}%/{} \n\n".format(pdata.fullname, pdata.type, pdata.bp, pdata.ability+swapstring, record.stage.attemptcost, ["Heart", "Coin"][record.stage.costtype], "s" if record.stage.attemptcost != 1 else "", record.stage.moves if untimed else record.stage.seconds // 60 + ":" + record.stage.seconds % 60, record.stage.hp,record.stage.basecatch, record.stage.bonuscatch, "move" if untimed else "3sec")
		
		entry += generateDrops(record.stage)
		
		#stage data table
		# if record.stage.drop1item != 0:
# 			try:
# 				drop1item = dropitems[str(record.stage.drop1item)]
# 			except KeyError:
# 				drop1item = str(record.stage.drop1item)
# 			try:
# 				drop2item = dropitems[str(record.stage.drop2item)]
# 			except KeyError:
# 				drop2item = str(record.stage.drop2item)
# 			try:
# 				drop3item = dropitems[str(record.stage.drop3item)]
# 			except KeyError:
# 				drop3item = str(record.stage.drop3item)
		
			
# 			if record.stage.drop1item == record.stage.drop2item and record.stage.drop2item == record.stage.drop3item:
# 			entry += "Drop | Rate #1 | Rate #2 | Rate #3\n-|-|-|-\n"
# 				entry += "{} | {}% | {}% | {}%\n".format(drop1item, str(1/pow(2,record.stage.drop1rate-1)*100), str(1/pow(2,record.stage.drop2rate-1)*100), str(1/pow(2,record.stage.drop3rate-1)*100))
# 			else:
# 				entry += "Drop #1 | Drop #2 | Drop #3\n-|-|-\n"
# 				entry += "{} - {}% | {} - {}% | {} - {}%\n".format(drop1item, str(1/pow(2,record.stage.drop1rate-1)*100), drop2item, str(1/pow(2,record.stage.drop2rate-1)*100), drop3item, str(1/pow(2,record.stage.drop3rate-1)*100))   
				
		 
		
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
				swapstring += " / "
			entry += "{} | {} | {} | {} | {} | {} | {} | {}% + {}%/move | \n".format(day, pdata.fullname, pdata.type, pdata.bp, pdata.ability+swapstring, dailystage.moves, dailystage.hp, dailystage.basecatch, dailystage.bonuscatch)
		entry += "\n"
		
		#drop rates table
		dailystage = record.stages[0]
		entry += generateDrops(record.stages[0])
		
		# if dailystage.drop1item != 0:
# 			try:
# 				drop1item = dropitems[str(dailystage.drop1item)]
# 			except KeyError:
# 				drop1item = str(dailystage.drop1item)
# 			try:
# 				drop2item = dropitems[str(dailystage.drop2item)]
# 			except KeyError:
# 				drop2item = str(dailystage.drop2item)
# 			try:
# 				drop3item = dropitems[str(dailystage.drop3item)]
# 			except KeyError:
# 				drop3item = str(dailystage.drop3item)
# 			
# 			if dailystage.drop1item == dailystage.drop2item and dailystage.drop2item == dailystage.drop3item:
# 		   		entry += "Drop | Rate #1 | Rate #2 | Rate #3\n-|-|-|-\n"
# 				entry += "{} | {}% | {}% | {}%\n".format(drop1item, str(1/pow(2,record.stage.drop1rate-1)*100), str(1/pow(2,record.stage.drop2rate-1)*100), str(1/pow(2,record.stage.drop3rate-1)*100))
# 			else:
# 				entry += "Drop #1 | Drop #2 | Drop #3\n-|-|-\n"
# 				entry += "{} - {}% | {} - {}% | {} - {}%\n".format(drop1item, str(1/pow(2,record.stage.drop1rate-1)*100), drop2item, str(1/pow(2,record.stage.drop2rate-1)*100), drop3item, str(1/pow(2,record.stage.drop3rate-1)*100))
		
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
		entry += "Pokémon | Type | BP | RMLs | Max AP | Skill | Swapper Skill(s) | Mega Power | Icons | MSUs | Items | Moves\n---|---|---|---|---|---|---|---|---|---|---|---\n"
		megapokemonindex = record.stage.pokemonindex
		mpdata = PokemonData.getPokemonInfo(megapokemonindex)
		pdata = PokemonData.getPokemonInfo(mpdata.megaindex)
		swapstring = "None"
		if len(pdata.ss) != 0:
			swapstring = ""
			for i in range(len(pdata.ss)):
				swapstring += "{}, ".format(pdata.ss[i])
			swapstring = swapstring[0:-2]
		entry += "{} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {}\n\n".format(mpdata.fullname, mpdata.type, pdata.bp, pdata.rmls, pdata.maxap, pdata.ability, swapstring, "Mega Power", mpdata.icons, mpdata.msu, "Items", record.stage.moves)
		
		#tiers and rewards table
		entry += "Rewards | Mobile Rank | NA 3DS Rank | EU 3DS Rank | JP 3DS Rank\n---|---|---|---|---\n"
		entry += "MegaStone + 5 MSUs + 15 RMLs | 1 - 600 | 1 - 100 | 1 - 100 | 1 - 300\n"
		entry += "MegaStone + 4 MSUs + 10 RMLs | 600 - 2,000 | 101 - 300 | 101 - 200 | 301 - 1,000\n"
		entry += "MegaStone + 4 MSUs + 6 RMLs | 2,001 - 5,000 | 301 - 600 | 201 - 500 | 1,001 - 2,500\n"
		entry += "MegaStone + 3 MSUs + 4 RMLs | 5,001 - 8,000 | 601 - 1,000 | 501 - 700 | 2,501 - 4,000\n"
		entry += "MegaStone + 3 MSUs + 2 RMLs | 8,001 - 16,000 | 1,001 - 2,100 | 701 - 1,500 | 4,001 - 8,000\n"
		entry += "MegaStone + 2 MSUs + 1 RML | 16,001 - 28,000 | 2,101 - 3,600 | 1,501 - 2,600 | 8,001 - 14,000\n"
		entry += "MegaStone + 1 MSU + 1 RML | 28,001 - 40,000 | 3,601 - 5,200 | 2,601 - 3,700 | 14,001 - 20,000\n"
		entry += "MegaStone + 1 MSU + 1 MS | 40,001 - 60,000 | 5,201 - 7,800 | 3,701 - 5,600 | 20,001 - 30,000\n"
		entry += "MegaStone + 1 MS + 1 M+5 | 60,001 - 80,000 | 7,801 - 10,400 | 5,601 - 7,400 | 30,001 - 40,000\n"
		entry += "1 APU + 1 M+5 + 3,000 Coins | 80,001 - 100,000 | 10,401 - 13,000 | 7,401 - 9,300 | 40,001 - 50,000\n"
		entry += "1 APU + 3,000 Coins| 100,001 - 130,000 | 13,001 - 16,800 | 9,301 - 12,100 | 50,001 - 65,000\n"
		entry += "3,000 Coins | 130,001+ | 16,801+ | 12101+ | 65,001+\n"
		
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
			swapstring += " / "
		entry += "{} | {} | {} | {}\n\n".format(pdata.fullname, pdata.type, pdata.bp, pdata.ability+swapstring)
		
		#rewards table
		entry += "Level | Reward\n-|-\n"
		EBrewardsBin = BinStorage("Configuration Tables/stagePrizeEventLevel.bin")
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
		entry += "Pokémon | Type | BP (RMLs/MaxAP) | Skill | Encounter Rate | HP | Moves | Catch Rate\n---|---|---|---|---|---|---|---|---\n"
		entry += "\n"
		
		#drop rates table
		entry += "Drop #1 | Drop #2 | Drop #3\n-|-|-\n"
		entry += "\n"
		
		entries.append(entry)

#print each entry!
for entry in entries:
	print entry
	print "----------------------------------------------------------------"