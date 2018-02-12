# -*- coding: utf_8 -*-

#!/usr/bin/python

#Reads binary files that are unpacked from Pokemon Shuffle game archives, parses requested data, and prints them out in a readable format
#Usage: python shuffleparser.py appdatafolder extdatafolder datatype parameters
#- appdatafolder is the folder that holds data extracted from the app itself
#- extdatafolder is the folder that holds data extracted from downloaded extra data (aka update data)
#- possible datatypes: stage, expertstage, eventstage, layout, expertlayout, eventlayout, pokemon, ability, escalationanger, eventdetails, escalationrewards,
#exptable, comprewards, noticedurations, message, appmessage, trainerrank, monthlypikachu, stampbonus
#- parameters: up to three can be given (as of now, no command uses all three), and they serve different purposes depending on the datatype (read additional descriptions below)
#- index is used for stage data, stage layouts, pokemon data, and ability data. It can be an integer or the keyword "all".
#- extraflag is optional: l to enable layout image generation, m to switch to parsing mobile data, d to print stage disruptions, md for both m and d

from __future__ import division
import sys, os.path
from pokemoninfo import *
from stageinfo import *
from miscdetails import *
from bindata import *
import layoutimagegenerator

#Item rewards from stages
itemrewards = {"0":"Moves +5", "1":"Time +10", "3":"Mega Start", "6":"Disruption Delay", "7":"Attack Power", "8":"Mega Speedup", "13":"Raise Max Level", "14":"Level Up", "15":"Exp. Booster S", "16":"Exp. Booster M", "17":"Exp. Booster L", "18":"Skill Booster S", "19":"Skill Booster M", "20":"Skill Booster L", "21":"Skill Swapper"}
itemrewards2 = {"0":"Attack Power ↑", "1":"Moves +5", "3":"Exp. Points x1.5", "4":"Mega Start", "6":"Disruption Delay", "7":"Attack Power ↑", "8":"Mega Speedup", "13":"Raise Max Level", "14":"Level Up", "15":"Exp. Booster S", "16":"Exp. Booster M", "17":"Exp. Booster L", "18":"Skill Booster S", "19":"Skill Booster M", "20":"Skill Booster L", "21":"Skill Swapper"}
def itemreward(itemtype, itemid):
    if itemtype in [1, 7]:
        item = "Jewel"
    elif itemtype == 2:
        item = "Heart"
    elif itemtype in [3, 31, 33]:
        item = "Coin"
    elif itemtype == 4:
        try:
            item = itemrewards[str(itemid)]
        except KeyError:
            item = "Item {}".format(itemid)
    elif itemtype in [8, 9, 10, 25, 26, 50]:
        try:
            item = itemrewards2[str(itemid)]
        except KeyError:
            item = "Item {}".format(itemid)
    elif itemtype in [5, 11, 27]:
        pokemonrecord = PokemonData.getPokemonInfo(itemid+1093)
        item = pokemonrecord.name
    else:
        item = "Item Type {}".format(itemtype)
    return item

def main(args):
    #make sure correct number of arguments
    if len(args) < 3:
        print "3-5 arguments: appdatafolder, extdatafolder, datatype, index, extraflag"
        print "- possible datatypes: stage, expertstage, eventstage, layout, expertlayout, eventlayout, pokemon, ability, escalationanger, eventdetails, escalationrewards, exptable, comprewards, noticedurations, message, appmessage, trainerrank, monthlypikachu, stampbonus"
        print "- index is optional with some datatypes, it can be an integer or the keyword all"
        print "- extraflag is optional: l to enable layout image generation, m to switch to parsing mobile stage data, d to include stage disruptions in output, md for both m and d"
        sys.exit()
    
    #parse arguments
    appfolder = args[0]
    extfolder = args[1]
    BinStorage.workingdirs["ext"] = os.path.abspath(extfolder)
    BinStorage.workingdirs["app"] = os.path.abspath(appfolder)
    datatype = args[2]
    parameters = ["", "", ""]
    
    if (len(args) >= 4):
        parameters[0] = args[3]
    if (len(args) >= 5):
        parameters[1] = args[4]
    if (len(args) >= 6):
        parameters[2] = args[5]
    
    try:
        if datatype == "stage" or datatype == "expertstage" or datatype == "eventstage":
            #parameters: [index/range, extra, ..]
            if datatype == "stage":
                stagetype = 0
            elif datatype == "expertstage":
                stagetype = 1
            elif datatype == "eventstage":
                stagetype = 2
            
            sdata = StageData("Configuration Tables/stageData{}.bin".format(["", "Extra", "Event"][stagetype]))
            if parameters[0] == "all":
                sdata.printalldata(stagetype=["main", "expert", "event"][stagetype], extra=parameters[1])
            else:
                indices = parameters[0].split("-")
                #startindex and endindex provided
                if len(indices) >= 2:
                    for index in range(int(indices[0]), int(indices[1])+1):
                        sdata.printdata(index, stagetype=["main", "expert", "event"][stagetype], extra=parameters[1])
                        print
                #index provided
                elif indices[0].isdigit():
                    sdata.printdata(int(indices[0]), stagetype=["main", "expert", "event"][stagetype], extra=parameters[1])
                #query pokemon provided
                else:
                    sdata.printdata2(indices[0], stagetype=["main", "expert", "event"][stagetype], extra=parameters[1])
                
        elif datatype == "layout" or datatype == "expertlayout" or datatype == "eventlayout":
            #parameters: [index, extra, ..]
            if datatype == "layout":
                stagetype = 0
            elif datatype == "expertlayout":
                stagetype = 1
            elif datatype == "eventlayout":
                stagetype = 2
            
            ldata = StageLayout("Configuration Tables/stageLayout{}.bin".format(["", "Extra", "Event"][stagetype]))
            if parameters[0] == "all":
                ldata.printalldata(generatelayoutimage=parameters[1])
            else:
                ldata.printdata(int(parameters[0]), generatelayoutimage=parameters[1])
                
        elif datatype == "pokemon":
            #parameters: [index, extra, ..]
            if parameters[0] == "all":
                PokemonData.printalldata(extra=parameters[1])
            else:
                try:
                    PokemonData.printdata(int(parameters[0]), extra=parameters[1])
                except ValueError:
                    PokemonData.printdata2(parameters[0], extra=parameters[1])
        
        elif datatype == "ability":
            #parameters: [index, .., ..]
            if parameters[0] == "all":
                PokemonAbility.printalldata()
            else:
                try:
                    PokemonAbility.printdata(int(parameters[0]))
                except ValueError:
                    PokemonAbility.printdata2(parameters[0])
                
        elif datatype == "escalationanger":
            #parameters: [.., .., ..]
            escBin = BinStorage("Configuration Tables/levelUpAngryParam.bin")
            for record in range(escBin.num_records):
                thisRecord = escBin.getRecord(record)
                print "[{}, {}]".format(readbits(thisRecord, 0, 0, 4), readfloat(thisRecord, 4))
            print "Note that '15' is supposed to be '-1'. It's a signed/unsigned thing."
               
        elif datatype == "eventdetails":
            #parameters: [extra, .., ..]
            sdata = StageData("Configuration Tables/stageDataEvent.bin")
            eventBin = BinStorage("Configuration Tables/eventStage.bin")
            for i in range(eventBin.num_records):
                snippet = eventBin.getRecord(i)
                record = EventDetails(i, snippet, sdata, mobile=parameters[0])
                record.printdata()
        
        elif datatype == "escalationrewards":
            #parameters: [.., .., ..]
            EBrewardsBin = BinStorage("Configuration Tables/stagePrizeEventLevel.bin")
            ebrewards = EscalationRewards(EBrewardsBin)
            ebrewards.printdata()
        
        elif datatype == "exptable":
            #parameters: [.., .., ..]
            printExpTable()
        
        elif datatype == "comprewards":
            #parameters: [.., .., ..]
            rankingPrizeInfo = BinStorage("Configuration Tables/rankingPrizeInfo.bin")
            for i in range(rankingPrizeInfo.num_records):
                snippet = rankingPrizeInfo.getRecord(i)
                threshold = readbits(snippet, 4, 0, 24)
                rewards = []
                for j in range(0, 48, 16):
                    rewards.append({"itemamount":readbits(snippet, j+12, 0, 16), "itemtype":readbyte(snippet, j+20), "itemid":readbyte(snippet, j+22)})
                
                rewardstring = "{}: {} / ".format(i, threshold)
                for j in range(3):
                    if rewards[j]["itemamount"] != 0:
                        rewardstring += "{} x{} + ".format(itemreward(rewards[j]["itemtype"], rewards[j]["itemid"]), rewards[j]["itemamount"])
                
                rewardstring = rewardstring[:-3]
                print rewardstring
        
        elif datatype == "test":
            rankingPrize = BinStorage("Configuration Tables/rankingPrize.bin")
            for i in range(rankingPrize.num_records):
                snippet = rankingPrize.getRecord(i)
                print "{}: {} {}".format(i, readbits(snippet, 0, 0, 12)-474, readbits(snippet, 4, 0, 12)-474)
        
        elif datatype == "noticedurations":
            #parameters: [.., .., ..]
            notice = BinStorage("Configuration Tables/notice.bin")
            for i in range(notice.num_records):
                snippet = notice.getRecord(i)
                
                startyear = readbits(snippet, 0, 0, 6)
                startmonth = readbits(snippet, 0, 6, 4)
                startday = readbits(snippet, 1, 2, 5)
                starthour = readbits(snippet, 1, 7, 5)
                startminute = readbits(snippet, 2, 4, 6)
                endyear = readbits(snippet, 3, 2, 6)
                endmonth = readbits(snippet, 4, 0, 4)
                endday = readbits(snippet, 4, 4, 5)
                endhour = readbits(snippet, 5, 1, 5)
                endminute = readbits(snippet, 5, 6, 6)
                
                value = readbits(snippet, 12, 3, 5)
                
                #datetime stuff
                timezone = pytz.timezone("Japan")
                starttime = datetime.datetime(startyear + 2000, startmonth, startday, starthour, startminute)
                starttime = timezone.localize(starttime).astimezone(pytz.timezone("UTC"))
                starttimestring = starttime.strftime("%Y-%m-%d %H:%M UTC")
                endtime = datetime.datetime(endyear + 2000, endmonth, endday, endhour, endminute)
                endtime = timezone.localize(endtime).astimezone(pytz.timezone("UTC"))
                endtimestring = endtime.strftime("%Y-%m-%d %H:%M UTC")
                
                print "{}: {} to {}".format(i, starttimestring, endtimestring)
        
        elif datatype == "message":
            #parameters: [category, .., ..]
            messages = BinStorage("Message_US/message{}_US.bin".format(parameters[0]))
            for i in range(messages.num_records):
                print "========== MESSAGE {} ==========".format(i)
                print messages.getMessage(i)
        
        elif datatype == "appmessage":
            #parameters: [category, .., ..]
            messages = BinStorage("Message_US/message{}_US.bin".format(parameters[0]), "app")
            for i in range(messages.num_records):
                print "========== MESSAGE {} ==========".format(i)
                print messages.getMessage(i)
        
        elif datatype == "trainerrank":
            #parameters: [.., .., ..]
            trainerrank = BinStorage("Configuration Tables/trainerRank.bin", "app")
            for i in range(trainerrank.num_records):
                snippet = trainerrank.getRecord(i)
                print "Rank {}: {}".format(i+2, readbits(snippet, 16, 0, 16))
        
        elif datatype == "monthlypikachu":
            #parameters: [.., .., ..]
            monthlypikachu = BinStorage("Configuration Tables/monthlyPikachu.bin", "app")
            for i in range(monthlypikachu.num_records):
                snippet = monthlypikachu.getRecord(i)
                data = readbits(snippet, 0, 0, 8)
                pokemon = PokemonData.getPokemonInfo(869+data)
                print "{} - {}".format(i, pokemon.fullname)
        
        elif datatype == "stampbonus":
            #parameters: [.., .., ..]
            stampbonus = BinStorage("Configuration Tables/stampBonus.bin", "app")
            for i in range(stampbonus.num_records):
                snippet = stampbonus.getRecord(i)
                type = readbyte(snippet, 4)
                amount = readbyte(snippet, 6)
                id = readbyte(snippet, 0)
                print "{} - {} x{}".format(i+1, itemreward(type, id), amount)
        
        else:
            sys.stderr.write("datatype should be one of these: stage, expertstage, eventstage, layout, expertlayout, eventlayout, pokemon, ability, escalationanger, items, eventdetails, escalationrewards, eventstagerewards, stagerewards\n")
    except IOError:
        sys.stderr.write("Couldn't find the bin file to extract data from.\n")
        raise

if __name__ == "__main__":
    main(sys.argv[1:])
