import sys
import datetime
import pytz
from pokemoninfo import *
from bindata import *

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

class EventDetails:
    def __init__(self, index, snippet, stageBin):
        self.binary = snippet
        self.index = index
        
        #parse!
        self.stagetype = readbits(snippet, 1, 0, 4) #1:normal, 2:daily, 3:???, 4:meowth, 5:comp, 6:EB, 7:safari, 8:itemstage
        self.stageindex = readbyte(snippet, 4)
        self.stage = stageBin.getStageInfo(self.stageindex)
        self.stagepokemon = self.stage.pokemon.fullname
        
        if self.stagetype == 2:
            stageindexes = [readbyte(snippet, i) for i in [4,8,12,16,20,24,28]]
            self.stagepokemon = []
            self.stages = []
            entries = 0
            for stageindex in stageindexes:
                if stageindex == 255:
                    continue
                else:
                    stage = stageBin.getStageInfo(stageindex)
                    self.stages.append(stage)
                    self.stagepokemon.append(stage.pokemon.fullname)
                    entries += 1
            
            self.dailystring = ""
            for i in range(entries):
                self.dailystring += " {} (stage index {})".format(self.stagepokemon[i], stageindexes[i])
        if self.stagetype == 6:
            self.stagepokemon = "ESCALATION BATTLES"
        if self.stagetype == 7:
            self.stagepokemon = "SAFARI"
        
        self.startyear = readbits(snippet, 48, 0, 6)
        self.startmonth = readbits(snippet, 48, 6, 4)
        self.startday = readbits(snippet, 49, 2, 5)
        self.starthour = readbits(snippet, 49, 7, 5)
        self.startminute = readbits(snippet, 50, 4, 6)
        self.endyear = readbits(snippet, 51, 2, 6)
        self.endmonth = readbits(snippet, 52, 0, 4)
        self.endday = readbits(snippet, 52, 4, 5)
        self.endhour = readbits(snippet, 53, 1, 5)
        self.endminute = readbits(snippet, 53, 6, 6)
        
        self.triesavailable = readbits(snippet, 1, 4, 4)
        self.unlockcosttype = readbits(snippet, 73, 0, 4)
        self.unlockcost = readbits(snippet, 76, 0, 16)
        self.unlocktimes = readbits(snippet, 98, 0, 4)
        
        if self.unlockcosttype == 0:
            self.unlockcosttype = "Coin"
        elif self.unlockcosttype == 1:
            self.unlockcosttype = "Jewel"
        else:
            self.unlockcosttype = "???"
    
    def printdata(self):
        #datetime stuff
        timezone = pytz.timezone("Japan")
        starttime = datetime.datetime(self.startyear + 2000, self.startmonth, self.startday, self.starthour, self.startminute)
        starttime = timezone.localize(starttime).astimezone(pytz.timezone("UTC"))
        starttimestring = starttime.strftime("%Y-%m-%d %H:%M UTC")
        endtime = datetime.datetime(self.endyear + 2000, self.endmonth, self.endday, self.endhour, self.endminute)
        endtime = timezone.localize(endtime).astimezone(pytz.timezone("UTC"))
        endtimestring = endtime.strftime("%Y-%m-%d %H:%M UTC")
        duration = endtime - starttime
        durationstring = "{} days".format(duration.days)
        if duration.seconds != 0:
            hours = int(duration.seconds / 3600)
            durationstring += ", {} hours".format(hours)
        
        if self.stagetype == 2:
            print "DAILY:{}".format(self.dailystring)
            print "Event Duration: {} to {} ({})".format(starttimestring, endtimestring, durationstring)
        else:
            print "{} (stage index {})".format(self.stagepokemon, self.stageindex)
            print "Event Duration: {} to {} ({})".format(starttimestring, endtimestring, durationstring)
            if self.unlockcost != 0 and self.stagetype != 7:
                print "Costs {} {}(s) to unlock {} time(s)".format(self.unlockcost, self.unlockcosttype, self.unlocktimes)
            if self.triesavailable != 0 and self.stagetype != 7:
                print "Stage is available to attempt {} times before it disappears".format(self.triesavailable)
        print

class EscalationRewards:
    def __init__(self, EBrewardsBin):
        self.entries = []
        
        for i in range(EBrewardsBin.num_records):
            entry = {}
            record = EBrewardsBin.getRecord(i)
            entry["level"] = readbits(record, 8, 0, 16)
            if entry["level"] == 0:
                continue
            entry["itemtype"] = readbyte(record, 12)
            entry["itemid"] = readbyte(record, 16)
            entry["itemamount"] = readbits(record, 20, 0, 16)
            entry["item"] = itemreward(entry["itemtype"], entry["itemid"])
            
            self.entries.append(entry)
    
    def printdata(self):
        for entry in self.entries:
            print "Level {} reward: {} x{}".format(entry["level"], entry["item"], entry["itemamount"])

class StageRewards:
    def __init__(self, rewardsBin):
        self.entries = []
        
        for i in range(rewardsBin.num_records):
            entry = {}
            record = rewardsBin.getRecord(i)
            entry["stageindex"] = readbits(record, 4, 0, 16)
            if entry["stageindex"] == 0:
                continue
            
            entry["itemtype"] = readbyte(record, 8)
            entry["itemid"] = readbyte(record, 12)
            entry["itemamount"] = readbits(record, 16, 0, 16)
            entry["item"] = itemreward(entry["itemtype"], entry["itemid"])
            
            entry["itemtype2"] = readbyte(record, 32)
            entry["itemid2"] = readbyte(record, 36)
            entry["itemamount2"] = readbits(record, 40, 0, 16)
            entry["item2"] = itemreward(entry["itemtype2"], entry["itemid2"])
            
            self.entries.append(entry)
    
    def printdata(self):
        for entry in self.entries:
            rewardstring = "{} x{}".format(entry["item"], entry["itemamount"])
            if entry["itemamount2"] != 0:
                rewardstring += " + {} x{}".format(entry["item2"], entry["itemamount2"])
            print "Stage Index {} reward: ".format(entry["stageindex"]) + rewardstring