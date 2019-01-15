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
import time, datetime
import pytz
sys.path.append("../")
from pokemoninfo import *
from stageinfo import *
from miscdetails import *
from bindata import *

rotation = int((time.time()-datetime.datetime.strptime("2018-02-13 06:00","%Y-%m-%d %H:%M").timestamp()) // (24 * 7 * 24 * 60 * 60))

dropitems = {"0":"Nothing", "1":"RML", "2":"LU", "3":"EBS", "4":"EBM", "5":"EBL", "6":"SBS", "7":"SBM", "8":"SBL", "9":"SS", "10":"MSU", "11":"M+5", "12":"T+10", "13":"EXP1.5", "14":"MS", "15":"C-1", "16":"DD", "17":"APU", "18":"1 Heart", "19":"2 Hearts", "20":"5 Hearts", "21":"3 Hearts", "22":"20 Hearts", "23":"10 Hearts", "24":"100 Coins", "25":"300 Coins", "26":"1000 Coins", "27":"2000 Coins", "28":"200 Coins", "29":"400 Coins", "30":"5000 Coins", "31":"Jewel", "32":"PSB"}
megastones = {"Mega Banette":"Banettite", "Mega Garchomp":"Garchompite", "Mega Steelix":"Steelixite", "Mega Manectric":"Manectite", "Mega Gyarados":"Gyaradosite", "Mega Alakazam":"Alakazite", "Mega Pinsir":"Pinsirite", "Mega Camerupt":"Cameruptite", "Mega Beedrill":"Beedrillite", "Mega Houndoom":"Houndoominite", "Mega Gardevoir":"Gardevoirite", "Mega Charizard X":"Charizardite X"}

appfolder = sys.argv[1]
extfolder = sys.argv[2]
BinStorage.workingdirs["ext"] = os.path.abspath(extfolder)
BinStorage.workingdirs["app"] = os.path.abspath(appfolder)
week = int(sys.argv[3])
if len(sys.argv) >= 5:
    mobile = sys.argv[4]
else:
    mobile = ""

sdata = StageData("Configuration Tables/stageDataEvent.bin")
eventBin = BinStorage("Configuration Tables/eventStage.bin")

#this will hold the markup text for each event entry
comp = []
challenge = []
challenge2 = []
safari = []
eb = []
oad = []
daily = []

#for eb rewards...
ebnumber = 0

#for each entry in events...
for i in range(eventBin.num_records):
    snippet = eventBin.getRecord(i)
    record = EventDetails(i, snippet, sdata, mobile=mobile)
    
    if record.stagetype == 6:
        ebnumber += 1
    
    #weekly event?
    if record.repeattype != 1:
        continue
    #matches queried week number?
    if record.repeatparam1+1 != week:
        continue
    
    #skip the weekly stuff
    if record.stagepokemon in ["Victini", "Magearna", "Meowth", "Meowth (Alola Form)", "Eevee", "Wobbuffet (Male)", "Wobbuffet (Female)", "Carnivine", "Oranguru", "Passimian"]:
        continue
    
    #datetime stuff
    timezone = pytz.timezone("Japan")
    starttime = datetime.datetime(record.startyear + 2000, record.startmonth, record.startday, record.starthour, record.startminute)
    starttime = timezone.localize(starttime).astimezone(pytz.timezone("UTC"))
    starttimestring = starttime.strftime("%Y-%m-%d %H:%M UTC")
    
    duration = datetime.timedelta(0, 0, 0, 0, record.repeatduration)
    durationstring = "{} days".format(duration.days)
    if duration.seconds != 0:
        durationstring += ", {} hours".format(duration.seconds / 3600)
    
    advance = datetime.timedelta((24 * 7 * rotation) + (7 * record.repeatparam1))
    starttime = starttime + advance
    starttimestring = starttime.strftime("%Y-%m-%d %H:%M UTC")
    endtime = starttime + duration
    endtimestring = endtime.strftime("%Y-%m-%d %H:%M UTC")
    
    #################
    # Normal Stages #
    #################
    if record.stagetype == 1:
        if record.unlockcost == 20000:
            title = "UB Challenge"
        elif record.stage.drop3item == 1:
            title = "Special Challenge"
        elif len(challenge) >= 5:
            title = "Ultra Challenge"
        elif record.stage.timed:
            title = "High-Speed Challenge"
        else:
            title = "Great Challenge"
        entry = "#{}: {}\n\n".format(title, record.stagepokemon[0])
        
        entry += "**Event Period**: {} to {} ({})\n\n".format(starttimestring, endtimestring, durationstring)
        
        #pokemon data table
        entry += "Pokémon|Type|BP|RMLs|Max AP|Skill|Swapper Skill(s)\n:-:|:-:|:-:|:-:|:-:|:-:|:-:--\n"
        pokemonindex = record.stage.pokemonindex
        pdata = PokemonData.getPokemonInfo(pokemonindex, extra=mobile)
        swapstring = "None"
        if len(pdata.ss) != 0:
            swapstring = ""
            for i in range(len(pdata.ss)):
                swapstring += "{}, ".format(pdata.ss[i])
            swapstring = swapstring[0:-2]
        entry += "{}|{}|{}|{}|{}|{}|{}\n\n".format(pdata.fullname, pdata.type, pdata.bp, pdata.rmls, pdata.maxap, pdata.ability, swapstring)
        
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
            entry += "HP|{}|Catch Rate|Attempt Cost|Drop 1 - Rate|Drop 2 - Rate|Drop 3 - Rate\n:-:|:-:|:-:|:-:|:-:|:-:|:-:--\n".format(["Moves", "Seconds"][timed])
            entry += "{}|{}|{}% + {}%/{}|{} {}{}|{} - {}%|{} - {}%|{} - {}%\n".format(record.stage.hp, [record.stage.moves, record.stage.seconds][timed], record.stage.basecatch, record.stage.bonuscatch, ["move", "3sec"][timed], record.stage.attemptcost, ["Heart", "Coin"][record.stage.costtype], "s" if record.stage.attemptcost != 1 else "", drop1item, str(1/pow(2,record.stage.drop1rate-1)*100), drop2item, str(1/pow(2,record.stage.drop2rate-1)*100), drop3item, str(1/pow(2,record.stage.drop3rate-1)*100))
        else:
            entry += "HP|{}|Catch Rate|Attempt Cost\n:-:|:-:|:-:|:-:--\n".format(["Moves", "Seconds"][timed])
            entry += "{}|{}|{}% + {}%/{}|{} {}{}\n".format(record.stage.hp, [record.stage.moves, record.stage.seconds][timed], record.stage.basecatch, record.stage.bonuscatch, ["move", "3sec"][timed], record.stage.attemptcost, ["Heart", "Coin"][record.stage.costtype], "s" if record.stage.attemptcost != 1 else "")
        
        if title == "Great Challenge" or title == "High-Speed Challenge":
            challenge.append(entry)
        else:
            challenge2.append(entry)
    
    ###########
    # Dailies #
    ###########
    #assuming dailies are never timed and always cost 1 heart
    elif record.stagetype == 2:
        #once a day stages are dailies with identical pokemon in all days
        if record.stagepokemon[0] == record.stagepokemon[1]:
            entry = "#A Great Chance a Day!: {}\n\n".format(record.stagepokemon[0])
            
            entry += "**Event Period**: {} to {} ({})\n\n".format(starttimestring, endtimestring, durationstring)
            
            #pokemon data table
            entry += "Pokémon|Type|BP|RMLs|Max AP|Skill|Swapper Skill(s)\n:-:|:-:|:-:|:-:|:-:|:-:|:-:--\n"
            pokemonindex = record.stages[0].pokemonindex
            pdata = PokemonData.getPokemonInfo(pokemonindex, extra=mobile)
            swapstring = "None"
            if len(pdata.ss) != 0:
                swapstring = ""
                for i in range(len(pdata.ss)):
                    swapstring += "{}, ".format(pdata.ss[i])
                swapstring = swapstring[0:-2]
            entry += "{}|{}|{}|{}|{}|{}|{}\n\n".format(pdata.fullname, pdata.type, pdata.bp, pdata.rmls, pdata.maxap, pdata.ability, swapstring)
            
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
                entry += "HP|{}|Catch Rate|Attempt Cost|Drop 1 - Rate|Drop 2 - Rate|Drop 3 - Rate\n:-:|:-:|:-:|:-:|:-:|:-:|:-:--\n".format(["Moves", "Seconds"][timed])
                entry += "{}|{}|{}% + {}%/{}|{} {}{}|{} - {}%|{} - {}%|{} - {}%\n".format(record.stage.hp, [record.stage.moves, record.stage.seconds][timed], record.stage.basecatch, record.stage.bonuscatch, ["move", "3sec"][timed], record.stage.attemptcost, ["Heart", "Coin"][record.stage.costtype], "s" if record.stage.attemptcost != 1 else "", drop1item, str(1/pow(2,record.stage.drop1rate-1)*100), drop2item, str(1/pow(2,record.stage.drop2rate-1)*100), drop3item, str(1/pow(2,record.stage.drop3rate-1)*100))
            else:
                entry += "HP|{}|Catch Rate|Attempt Cost\n:-:|:-:|:-:|:-:--\n".format(["Moves", "Seconds"][timed])
                entry += "{}|{}|{}% + {}%/{}|{} {}{}\n".format(record.stage.hp, [record.stage.moves, record.stage.seconds][timed], record.stage.basecatch, record.stage.bonuscatch, ["move", "3sec"][timed], record.stage.attemptcost, ["Heart", "Coin"][record.stage.costtype], "s" if record.stage.attemptcost != 1 else "")
            
            oad.append(entry)
        
        #dailies
        else:
            entry = "#Daily Pokémon\n\n"
            
            entry += "**Event Period**: {} to {} ({})\n\n".format(starttimestring, endtimestring, durationstring)
            
            #pokemon + stage data table
            entry += "Day|Pokémon|Type|BP (RMLs/MaxAP)|Skill (Swapper Skills)|HP|Moves|Catch Rate\n-:-:|:-::-:|:-::-:|:-::-:|:-::-:|:-::-:|:-::-:|:-::-:|:-:-\n"
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
                entry += "{}|{}|{}|{} ({}/{})|{}{}|{}|{}|{}% + {}%/move\n".format(day, pdata.fullname, pdata.type, pdata.bp, pdata.rmls, pdata.maxap, pdata.ability, " ({})".format(swapstring) if swapstring != "None" else "", dailystage.hp, dailystage.moves, dailystage.basecatch, dailystage.bonuscatch)
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
                entry += "Item 1 - Drop Rate|Item 2 - Drop Rate|Item 3 - Drop Rate\n-:-:|:-::-:|:-:-\n"
                entry += "{} - {}%|{} - {}%|{} - {}%\n".format(drop1item, str(1/pow(2,record.stage.drop1rate-1)*100), drop2item, str(1/pow(2,record.stage.drop2rate-1)*100), drop3item, str(1/pow(2,record.stage.drop3rate-1)*100))
        
            daily.append(entry)
    
    ################
    # Competitions #
    ################
    #competitive stages
    #assuming comp stages are never timed and always cost 1 heart
    #rewards and tiers can't be datamined yet, so the table is preset (since they don't usually change) (mega stones should be filled in maually)
    #there are three identical entries, one for each region, but we only need one of them
    elif record.stagetype == 5 and len(comp) == 0:
        #title
        entry = "#Competitive Stage: {}\n\n".format(record.stagepokemon[0])
        
        entry += "**Event Period**: {} to {} ({})\n\n".format(starttimestring, endtimestring, durationstring)
        
        #pokemon + stage data table
        entry += "Pokémon|Type|BP|RMLs|Max AP|Skill|Swapper Skill(s)|Mega Power|Icons|MSUs|Items|Moves\n:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:--\n"
        megapokemonindex = record.stage.pokemonindex
        mpdata = PokemonData.getPokemonInfo(megapokemonindex, extra=mobile)
        pdata = PokemonData.getPokemonInfo(mpdata.megaindex, extra=mobile)
        
        swapstring = "None"
        if len(pdata.ss) != 0:
            swapstring = ""
            for i in range(len(pdata.ss)):
                swapstring += "{}, ".format(pdata.ss[i])
            swapstring = swapstring[0:-2]
        
        entry += "{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}\n\n".format(mpdata.fullname, mpdata.type, pdata.bp, pdata.rmls, pdata.maxap, pdata.ability, swapstring, mpdata.megapower, mpdata.icons, mpdata.msu, ", ".join(record.stage.items), record.stage.moves)
        
        #tiers and rewards table
        try:
            megastone = megastones[record.stagepokemon[0]]
        except KeyError:
            megastone = "MEGASTONE"
        
        entry += "Rewards|Percentiles\n:-:|:-:--\n"
        entry += "{} + Mega Speedup x5 + Raise Max Level x15|0% - 1%\n".format(megastone)
        entry += "{} + Mega Speedup x4 + Raise Max Level x10|1% - 2%\n".format(megastone)
        entry += "{} + Mega Speedup x4 + Raise Max Level x6|2% - 3%\n".format(megastone)
        entry += "{} + Mega Speedup x3 + Raise Max Level x4|3% - 5%\n".format(megastone)
        entry += "{} + Mega Speedup x3 + Raise Max Level x2|5% - 10%\n".format(megastone)
        entry += "{} + Mega Speedup x2 + Raise Max Level x1|10% - 20%\n".format(megastone)
        entry += "{} + Mega Speedup x1 + Raise Max Level x1|20% - 30%\n".format(megastone)
        entry += "{} + Mega Speedup x1 + Mega Start x1|30% - 40%\n".format(megastone)
        entry += "{} + Mega Start x1 + Moves +5 x1|40% - 50%\n".format(megastone)
        entry += "Attack Power ↑ x1 + Moves +5 x1 + Coins x3000|50% - 60%\n"
        entry += "Attack Power ↑ x1 + Coins x3000|60% - 80%\n"
        entry += "Coins x3000|80% - 100%\n"
        
        comp.append(entry)
    
    ######################
    # Escalation Battles #
    ######################
    #escalation battles
    #assuming EBs always cost 1 heart
    elif record.stagetype == 6:
        #title
        entry = "#Escalation Battles: {}\n\n".format(record.stagepokemon[0])
        
        entry += "**Event Period**: {} to {} ({})\n\n".format(starttimestring, endtimestring, durationstring)
        
        #pokemon data table
        entry += "Pokémon|Type|BP|RMLs|Max AP|Skill|Swapper Skill(s)\n:-:|:-:|:-:|:-:|:-:|:-:|:-:--\n"
        pokemonindex = record.stages[0].pokemonindex
        pdata = PokemonData.getPokemonInfo(pokemonindex, extra=mobile)
        swapstring = "None"
        if len(pdata.ss) != 0:
            swapstring = ""
            for i in range(len(pdata.ss)):
                swapstring += "{}, ".format(pdata.ss[i])
            swapstring = swapstring[0:-2]
        entry += "{}|{}|{}|{}|{}|{}|{}\n\n".format(pdata.fullname, pdata.type, pdata.bp, pdata.rmls, pdata.maxap, pdata.ability, swapstring)
        
        #rewards table
        entry += "Level|Reward\n:-:|:-:--\n"
        EBrewardsBin = BinStorage("Configuration Tables/stagePrizeEventLevel.bin")
        ebrewards = EscalationRewards(EBrewardsBin)
        
        #figure out where the rewards for this EB starts and ends in the eb rewards list
        currentindex = 0
        currentlevel = 0
        counter = 1
        
        while counter < ebnumber:
            while ebrewards.entries[currentindex]["level"] > currentlevel:
                e = ebrewards.entries[currentindex]
                currentlevel = e["level"]
                currentindex += 1
            counter += 1
            currentlevel = 0
        
        while currentindex < len(ebrewards.entries) and ebrewards.entries[currentindex]["level"] > currentlevel:
            e = ebrewards.entries[currentindex]
            entry += "{}|{} {}{}\n".format(e["level"], e["itemamount"], e["item"], "s" if e["itemamount"] != 1 else "")
            currentlevel = e["level"]
            currentindex += 1
        
        eb.append(entry)
    
    ###########
    # Safaris #
    ###########
    #assuming safaris are never timed and always cost 1 heart
    elif record.stagetype == 7:
        #title
        entry = "#Pokémon Safari\n\n"
        
        entry += "**Event Period**: {} to {} ({})\n\n".format(starttimestring, endtimestring, durationstring)
        
        #pokemon + stage data table
        entry += "Pokémon|Type|BP (RMLs/MaxAP)|Skill|Encounter Rate|HP|Moves|Catch Rate\n:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:--\n"
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
            entry += "{}|{}|{} ({}/{})|{}{}|{:0.2f}%|{}|{}|{}% + {}%/move\n".format(pdata.fullname, pdata.type, pdata.bp, pdata.rmls, pdata.maxap, pdata.ability, " ({})".format(swapstring) if swapstring != "None" else "", 100 * record.extravalues[i] / sum(record.extravalues), safaristage.hp, safaristage.moves, safaristage.basecatch, safaristage.bonuscatch)
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
            entry += "Item 1 - Drop Rate|Item 2 - Drop Rate|Item 3 - Drop Rate\n-:-:|:-::-:|:-:-\n"
            entry += "{} - {}%|{} - {}%|{} - {}%\n".format(drop1item, str(1/pow(2,record.stage.drop1rate-1)*100), drop2item, str(1/pow(2,record.stage.drop2rate-1)*100), drop3item, str(1/pow(2,record.stage.drop3rate-1)*100))
        
        safari.append(entry)

print("#Week {} Events - Cycle {}\n".format(week,rotation+1))
print("---")

#print each entry!
for entry in comp:
    print(entry)
    print("---")
for entry in challenge2:
    print(entry)
    print("---")
for entry in eb:
    print(entry)
    print("---")
for entry in challenge:
    print(entry)
    print("---")
for entry in safari:
    print(entry)
    print("---")
for entry in oad:
    print(entry)
    print("---")
for entry in daily:
    print(entry)
    print("---")