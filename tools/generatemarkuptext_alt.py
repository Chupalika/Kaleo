#!/usr/bin/python
# -*- coding: utf_8 -*-

#THINGS TO NOTE:
#- One Chance a Day! stages will not grab the correct messages
#- Start-of-Month Challenges and Mid-month Challenges will not grab the correct messages
#- Competitive Stage rewards and tiers are unable to be datamined at the moment, so the tables are a set output because they don't usually change (the mega stone still needs to be changed though), but just be aware of this
#- Mega Pokemon's Mega Powers and Competitive Stage items are unable to be datamined at the moment, so they need to be manually filled in
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

dropitems = {"0":"Nothing", "1":"RML", "2":"LU", "3":"EBS", "4":"EBM", "5":"EBL", "6":"SBS", "7":"SBM", "8":"SBL", "9":"SS", "10":"MSU", "11":"M+5", "12":"T+10", "13":"EXP1.5", "14":"MS", "15":"C-1", "16":"DD", "17":"APU", "18":"1 Heart", "19":"2 Hearts", "20":"5 Hearts", "21":"3 Hearts", "22":"20 Hearts", "23":"10 Hearts", "24":"100 Coins", "25":"300 Coins", "26":"1000 Coins", "27":"2000 Coins", "28":"200 Coins", "29":"400 Coins", "30":"5000 Coins", "31":"Jewel", "32":"PSB"}

appfolder = sys.argv[1]
extfolder = sys.argv[2]
BinStorage.workingdirs["ext"] = os.path.abspath(extfolder)
BinStorage.workingdirs["app"] = os.path.abspath(appfolder)
week = int(sys.argv[3])
messageindices = sys.argv[4].split(",")
if len(sys.argv) >= 6:
    mobile = sys.argv[5]
else:
    mobile = ""

messagecounter = 0

sdata = StageData("Configuration Tables/stageDataEvent.bin")
eventBin = BinStorage("Configuration Tables/eventStage.bin")
messagestemp = BinStorage("Message_US/messageEventStage_US.bin")

#grab the messages
messages = []
for index in range(messagestemp.num_records):
    message = messagestemp.getMessage(index)
    
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
    record = EventDetails(i, snippet, sdata, mobile=mobile)
    
    if record.repeattype != 1:
        continue
    if record.repeatparam1+1 != week:
        continue
    
    #skip the weekly stuff
    if record.stagepokemon in ["Victini", "Magearna", "Meowth", "Meowth (Alola Form)", "Eevee", "Wobbuffet (Male)", "Wobbuffet (Female)", "Carnivine", "Oranguru", "Passimian"]:
        continue
    
    #message
    if messagecounter < len(messageindices):
        THEmessage = messages[int(messageindices[messagecounter])]
        messagecounter += 1
    else:
        THEmessage = ""
    
    #datetime stuff
    timezone = pytz.timezone("Japan")
    starttime = datetime.datetime(record.startyear + 2000, record.startmonth, record.startday, record.starthour, record.startminute)
    starttime = timezone.localize(starttime).astimezone(pytz.timezone("UTC"))
    starttimestring = starttime.strftime("%Y-%m-%d %H:%M UTC")
    
    duration = datetime.timedelta(0, 0, 0, 0, record.repeatduration)
    durationstring = "{} days".format(duration.days)
    if duration.seconds != 0:
        durationstring += ", {} hours".format(duration.seconds / 3600)
    
    advance = datetime.timedelta(7 * record.repeatparam1)
    starttime = starttime + advance
    starttimestring = starttime.strftime("%Y-%m-%d %H:%M UTC")
    endtime = starttime + duration
    endtimestring = endtime.strftime("%Y-%m-%d %H:%M UTC")
    
    #Messages:
    #31: Daily
    #32: Special Daily
    #33: Competitive Stage
    #34: One Chance a Day
    #36: Special Challenge (expert)
    #37: Special Challenge (main)
    #39: Great Challenge
    #40: Great Challenge (legendary)
    #41: Great Challenge (mythical)
    #44: High-Speed Challenge
    #45: High-Speed Challenge (legendary)
    #46: High-Speed Challenge (mythical)
    #49: Ultra Challenge (legendary)
    #50: Ultra Challenge (mythical)
    #53: UB Challenge
    #54: Pokemon Safari
    #55: Pokemon Safari (Pikachu)
    #56: Escalation Battles
    
    #################
    # Normal Stages #
    #################
    if record.stagetype == 1:
        #the title might be different! but for the most part it's just "Pokemon Appears"
        entry = ""
        entry += "* **{} Appears!**  \n".format(record.stagepokemon)
        entry += THEmessage + "\n\n"
        
        entry += "**Event Period**: {} to {} ({})\n\n".format(starttimestring, endtimestring, durationstring)
        
        #pokemon data table
        entry += "Pokémon | Type | BP | RMLs | Max AP | Skill | Swapper Skill(s)\n---|---|---|---|---|---|---\n"
        pokemonindex = record.stage.pokemonindex
        pdata = PokemonData.getPokemonInfo(pokemonindex, extra=mobile)
        swapstring = "None"
        if len(pdata.ss) != 0:
            swapstring = ""
            for i in range(len(pdata.ss)):
                swapstring += "{}, ".format(pdata.ss[i])
            swapstring = swapstring[0:-2]
        entry += "{} | {} | {} | {} | {} | {} | {}\n\n".format(pdata.fullname, pdata.type, pdata.bp, pdata.rmls, pdata.maxap, pdata.ability, swapstring)
        
        #stage data table
        if record.stage.timed == 0:
            timed = 0
        else:
            timed = 1
        if record.stage.drop1item != 0:
            try:
                drop1item = dropitems[str(record.stage.drop1item)]
            except KeyError:
                drop1item = str(record.stage.drop1item)
            try:
                drop2item = dropitems[str(record.stage.drop2item)]
            except KeyError:
                drop2item = str(record.stage.drop2item)
            try:
                drop3item = dropitems[str(record.stage.drop3item)]
            except KeyError:
                drop3item = str(record.stage.drop3item)
            entry += "HP | {} | Catch Rate | Attempt Cost | Drop 1 - Rate | Drop 2 - Rate | Drop 3 - Rate\n---|---|---|---|---|---|---\n".format(["Moves", "Seconds"][timed])
            entry += "{} | {} | {}% + {}%/{} | {} {}{} | {} - {}% | {} - {}% | {} - {}%\n".format(record.stage.hp, [record.stage.moves, record.stage.seconds][timed], record.stage.basecatch, record.stage.bonuscatch, ["move", "3sec"][timed], record.stage.attemptcost, ["Heart", "Coin"][record.stage.costtype], "s" if record.stage.attemptcost != 1 else "", drop1item, str(1/pow(2,record.stage.drop1rate-1)*100), drop2item, str(1/pow(2,record.stage.drop2rate-1)*100), drop3item, str(1/pow(2,record.stage.drop3rate-1)*100))
        else:
            entry += "HP | {} | Catch Rate | Attempt Cost\n---|---|---|---\n".format(["Moves", "Seconds"][timed])
            entry += "{} | {} | {}% + {}%/{} | {} {}{}\n".format(record.stage.hp, [record.stage.moves, record.stage.seconds][timed], record.stage.basecatch, record.stage.bonuscatch, ["move", "3sec"][timed], record.stage.attemptcost, ["Heart", "Coin"][record.stage.costtype], "s" if record.stage.attemptcost != 1 else "")
        
        entries.append(entry)
    
    ###########
    # Dailies #
    ###########
    #assuming dailies are never timed and always cost 1 heart
    elif record.stagetype == 2:
        #title
        entry = ""
        entry += "* **Daily Pokémon Are Here!**  \n"
        entry += THEmessage + "\n\n"
        
        entry += "**Event Period**: {} to {} ({})\n\n".format(starttimestring, endtimestring, durationstring)
        
        #pokemon + stage data table
        entry += "Day | Pokémon | Type | BP (RMLs/MaxAP) | Skill (Swapper Skills) | HP | Moves | Catch Rate\n--|--|--|--|--|--|--|--|--\n"
        for i in range(len(record.stagepokemon)):
            day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][i]
            dailystage = record.stages[i]
            pokemonindex = dailystage.pokemonindex
            pdata = PokemonData.getPokemonInfo(pokemonindex, extra=mobile)
            swapstring = "None"
            if len(pdata.ss) != 0:
                swapstring = ""
                for i in range(len(pdata.ss)):
                    swapstring += "{}, ".format(pdata.ss[i])
                swapstring = swapstring[0:-2]
            entry += "{} | {} | {} | {} ({}/{}) | {}{} | {} | {} | {}% + {}%/move\n".format(day, pdata.fullname, pdata.type, pdata.bp, pdata.rmls, pdata.maxap, pdata.ability, " ({})".format(swapstring) if swapstring != "None" else "", dailystage.hp, dailystage.moves, dailystage.basecatch, dailystage.bonuscatch)
        entry += "\n"
        
        #drop rates table
        dailystage = record.stages[0]
        if dailystage.drop1item != 0:
            try:
                drop1item = dropitems[str(dailystage.drop1item)]
            except KeyError:
                drop1item = str(dailystage.drop1item)
            try:
                drop2item = dropitems[str(dailystage.drop2item)]
            except KeyError:
                drop2item = str(dailystage.drop2item)
            try:
                drop3item = dropitems[str(dailystage.drop3item)]
            except KeyError:
                drop3item = str(dailystage.drop3item)
            entry += "Item 1 - Drop  Rate | Item 2 - Drop Rate | Item 3 - Drop Rate\n--|--|--\n"
            entry += "{} - {}% | {} - {}% | {} - {}%\n".format(drop1item, str(1/pow(2,record.stage.drop1rate-1)*100), drop2item, str(1/pow(2,record.stage.drop2rate-1)*100), drop3item, str(1/pow(2,record.stage.drop3rate-1)*100))
        
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
        #title
        entry = ""
        entry += "* **Competitive Stage Now Live!**  \n"
        entry += THEmessage + "\n\n"
        
        entry += "**Event Period**: {} to {} ({})\n\n".format(starttimestring, endtimestring, durationstring)
        
        #pokemon + stage data table
        entry += "Pokémon | Type | BP | RMLs | Max AP | Skill | Swapper Skill(s) | Mega Power | Icons | MSUs | Items | Moves\n---|---|---|---|---|---|---|---|---|---|---|---\n"
        megapokemonindex = record.stage.pokemonindex
        mpdata = PokemonData.getPokemonInfo(megapokemonindex, extra=mobile)
        pdata = PokemonData.getPokemonInfo(mpdata.megaindex, extra=mobile)
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
        entry += "1 APU + 1 3,000 Coins| 100,001 - 130,000 | 13,001 - 16,800 | 9,301 - 12,100 | 50,001 - 65,000\n"
        entry += "3,000 Coins | 130,001+ | 16,801+ | 12101+ | 65,001+\n"
        
        entries.append(entry)
    
    ######################
    # Escalation Battles #
    ######################
    #escalation battles
    #assuming EBs always cost 1 heart
    elif record.stagetype == 6:
        #title
        entry = ""
        entry += "* **Take on Escalation Battles!**  \n"
        entry += THEmessage + "\n\n"
        
        entry += "**Event Period**: {} to {} ({})\n\n".format(starttimestring, endtimestring, durationstring)
        
        #pokemon data table
        entry += "Pokémon | Type | BP | RMLs | Max AP | Skill | Swapper Skill(s)\n---|---|---|---|---|---|---\n"
        pokemonindex = record.stages[0].pokemonindex
        pdata = PokemonData.getPokemonInfo(pokemonindex, extra=mobile)
        swapstring = "None"
        if len(pdata.ss) != 0:
            swapstring = ""
            for i in range(len(pdata.ss)):
                swapstring += "{}, ".format(pdata.ss[i])
            swapstring = swapstring[0:-2]
        entry += "{} | {} | {} | {} | {} | {} | {}\n\n".format(pdata.fullname, pdata.type, pdata.bp, pdata.rmls, pdata.maxap, pdata.ability, swapstring)
        
        #rewards table
        entry += "Level | Reward\n---|---\n"
        EBrewardsBin = BinStorage("Configuration Tables/stagePrizeEventLevel.bin")
        ebrewards = EscalationRewards(EBrewardsBin)
        for e in ebrewards.entries:
            entry += "{} | {} {}{}\n".format(e["level"], e["itemamount"], e["item"], "s" if e["itemamount"] != 1 else "")
        
        entries.append(entry)
    
    ###########
    # Safaris #
    ###########
    #assuming safaris are never timed and always cost 1 heart
    elif record.stagetype == 7:
        #title
        entry = ""
        entry += "* **Pokémon Safari is Here!**  \n"
        entry += THEmessage + "\n\n"
        
        entry += "**Event Period**: {} to {} ({})\n\n".format(starttimestring, endtimestring, durationstring)
        
        #pokemon + stage data table
        entry += "Pokémon | Type | BP (RMLs/MaxAP) | Skill | Encounter Rate | HP | Moves | Catch Rate\n---|---|---|---|---|---|---|---|---\n"
        for i in range(len(record.stages)):
            safaristage = record.stages[i]
            pokemonindex = safaristage.pokemonindex
            pdata = PokemonData.getPokemonInfo(pokemonindex, extra=mobile)
            swapstring = "None"
            if len(pdata.ss) != 0:
                swapstring = ""
                for i in range(len(pdata.ss)):
                    swapstring += "{}, ".format(pdata.ss[i])
                swapstring = swapstring[0:-2]
            entry += "{} | {} | {} ({}/{}) | {}{} | {:0.2f}% | {} | {} | {}% + {}%/move\n".format(pdata.fullname, pdata.type, pdata.bp, pdata.rmls, pdata.maxap, pdata.ability, " ({})".format(swapstring) if swapstring != "None" else "", 100 * record.extravalues[i] / sum(record.extravalues), safaristage.hp, safaristage.moves, safaristage.basecatch, safaristage.bonuscatch)
        entry += "\n"
        
        #drop rates table
        safaristage = record.stages[0]
        if safaristage.drop1item != 0:
            try:
                drop1item = dropitems[str(safaristage.drop1item)]
            except KeyError:
                drop1item = str(safaristage.drop1item)
            try:
                drop2item = dropitems[str(safaristage.drop2item)]
            except KeyError:
                drop2item = str(safaristage.drop2item)
            try:
                drop3item = dropitems[str(safaristage.drop3item)]
            except KeyError:
                drop3item = str(safaristage.drop3item)
            entry += "Item 1 - Drop  Rate | Item 2 - Drop Rate | Item 3 - Drop Rate\n--|--|--\n"
            entry += "{} - {}% | {} - {}% | {} - {}%\n".format(drop1item, str(1/pow(2,record.stage.drop1rate-1)*100), drop2item, str(1/pow(2,record.stage.drop2rate-1)*100), drop3item, str(1/pow(2,record.stage.drop3rate-1)*100))
        
        entries.append(entry)

#print each entry!
for entry in entries:
    print entry
    print "----------------------------------------------------------------"