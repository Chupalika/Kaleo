import sys
import datetime
import pytz
from pokemoninfo import *
from bindata import *

#Item rewards from stages
itemrewards = {"0":"Moves +5", "1":"Time +10", "3":"Mega Start", "4":"Mega Start", "6":"Disruption Delay", "8":"Mega Speedup", "13":"Raise Max Level", "14":"Level Up", "15":"Exp. Booster S", "16":"Exp. Booster M", "17":"Exp. Booster L", "18":"Skill Booster S", "19":"Skill Booster M", "20":"Skill Booster L", "21":"Skill Swapper"}
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
    def __init__(self, index, snippet, stageBin, mobile=""):
        self.binary = snippet
        self.index = index
        
        #parse!
        self.stagetype = readbits(snippet, 1, 0, 4) #1:normal, 2:daily, 3:???, 4:meowth, 5:comp, 6:EB, 7:safari, 8:itemstage
        if mobile == "m":
            self.stagetype = readbits(snippet, 6, 4, 4)
        self.stageindex = readbits(snippet, 4, 0, 32)
        if mobile == "m":
            self.stageindex = readbits(snippet, 8, 0, 32)
        self.stage = stageBin.getStageInfo(self.stageindex, extra=mobile)
        self.stagepokemon = self.stage.pokemon.fullname
        
        #DAILY
        if self.stagetype == 2:
            stageindexes = [readbyte(snippet, i) for i in [4,8,12,16,20,24,28]]
            if mobile == "m":
                stageindexes = [readbyte(snippet, i) for i in [8,12,16,20,24,28,32]]
            self.stagepokemon = []
            self.stages = []
            entries = 0
            for stageindex in stageindexes:
                if stageindex == 255:
                    continue
                else:
                    stage = stageBin.getStageInfo(stageindex, extra=mobile)
                    self.stages.append(stage)
                    self.stagepokemon.append(stage.pokemon.fullname)
                    entries += 1
            
            self.dailystring = ""
            for i in range(entries):
                self.dailystring += " {} (Stage Index {})".format(self.stagepokemon[i], stageindexes[i])
        
        #escalation and safari stage index is not actually a stage index, it points to an entry in a separate file with extra data
        if self.stagetype == 6 or self.stagetype == 7:
            #dunno why, but I need to add 1
            self.stageindex += 1
            
            extraBin = BinStorage("Configuration Tables/eventStageExtendSetting.bin")

            self.stages = []
            self.extravalues = []
            entries = 0
            try:
                while True:
                    #read data
                    snippet2 = extraBin.getRecord(self.stageindex + entries)
                    stageindex = readbits(snippet2, 0, 0, 8)
                    value1 = readbits(snippet2, 4, 0, 16)
                    value2 = readbits(snippet2, 8, 0, 16)
                    #check for empty stage AND for invalid probs in safari block
                    if stageindex == 0 or (self.stagetype == 7 and value1 != value2): 
                        break
                    #process data
                    stage = stageBin.getStageInfo(stageindex, extra=mobile)
                    self.stages.append(stage)
                    self.extravalues.append(value1)
                    entries += 1
            except IndexError:
                pass #it's possible if the index is crowded we could run off the end, reading garbage data, and crash. This prevents the crash, but not the garbage data read. It's a pretty unlikely edge case anyway.
            self.stagepokemon = self.stages[0].pokemon.fullname
            
            #ESCALATION
            if self.stagetype == 6:
                self.ebstring = ""
                for i in range(entries):
                    self.ebstring += "Level {}: Stage Index {}\n".format(self.extravalues[i], self.stages[i].index)
                self.ebstring = self.ebstring[:-1]
            
            #SAFARI
            elif self.stagetype == 7:
                totalvalue = sum(self.extravalues)
                self.safaristring = ""
                for i in range(entries):
                    self.safaristring += "{} (Stage Index {}): {:0.2f}%\n".format(self.stages[i].pokemon.fullname, self.stages[i].index, float(self.extravalues[i] * 100) / totalvalue)
                self.safaristring = self.safaristring[:-1]
        
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
        self.unlockcosttype = readbits(snippet, 81, 0, 4)
        self.unlockcost = readbits(snippet, 84, 0, 16)
        self.unlocktimes = readbits(snippet, 118, 0, 4)
        
        if mobile == "m":
            self.startyear = readbits(snippet, 0, 0, 6)
            self.startmonth = readbits(snippet, 0, 6, 4)
            self.startday = readbits(snippet, 1, 2, 5)
            self.starthour = readbits(snippet, 1, 7, 5)
            self.startminute = readbits(snippet, 2, 4, 6)
            self.endyear = readbits(snippet, 3, 2, 6)
            self.endmonth = readbits(snippet, 4, 0, 4)
            self.endday = readbits(snippet, 4, 4, 5)
            self.endhour = readbits(snippet, 5, 1, 5)
            self.endminute = readbits(snippet, 5, 6, 6)
            
            self.triesavailable = readbits(snippet, 36, 0, 4)
            self.unlockcosttype = readbits(snippet, 40, 0, 4)
            self.unlockcost = readbits(snippet, 40, 0, 16)
            self.unlocktimes = readbits(snippet, 104, 0, 4)
    
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
        elif self.stagetype == 6:
            print "ESCALATION: {}".format(self.stagepokemon)
            print "Event Duration: {} to {} ({})".format(starttimestring, endtimestring, durationstring)
            print self.ebstring
        elif self.stagetype == 7:
            print "SAFARI"
            print "Event Duration: {} to {} ({})".format(starttimestring, endtimestring, durationstring)
            print self.safaristring
        else:
            print "{} (Stage Index {})".format(self.stagepokemon, self.stageindex)
            print "Event Duration: {} to {} ({})".format(starttimestring, endtimestring, durationstring)
        
        if self.unlockcost != 0:
            print "Costs {} {}(s) to unlock {} time(s)".format(self.unlockcost, ["Coin", "Jewel"][self.unlockcosttype], self.unlocktimes)
        if self.triesavailable != 0:
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
    stageRewardsBin = None
    stageRewards = None
    
    @classmethod
    def getStageReward(thisClass, stagetype, index):
        if thisClass.stageRewardsBin is None:
            thisClass = thisClass(stagetype=stagetype)
        try:
            return thisClass.stageRewards[index]
        except KeyError:
            return None
        except TypeError:
            return None
    
    def __init__(self, stagetype):
        if stagetype == "event":
            self.stageRewardsBin = BinStorage("Configuration Tables/stagePrizeEvent.bin")
        elif stagetype == "main":
            self.stageRewardsBin = BinStorage("Configuration Tables/stagePrize.bin")
        elif stagetype == "expert":
            return None
        else:
            print "Only 'main' and 'event' stages have stage rewards. '{}' is not one of those.".format(stagetype)
        
        self.stageRewards = {}
        
        for i in range(self.stageRewardsBin.num_records):
            entry = {}
            record = self.stageRewardsBin.getRecord(i)
            stageindex = readbits(record, 4, 0, 16)
            if stageindex == 0:
                continue
            
            entry["itemtype"] = readbyte(record, 8)
            entry["itemid"] = readbyte(record, 12)
            entry["itemamount"] = readbits(record, 16, 0, 16)
            entry["item"] = itemreward(entry["itemtype"], entry["itemid"])
            
            entry["itemtype2"] = readbyte(record, 32)
            entry["itemid2"] = readbyte(record, 36)
            entry["itemamount2"] = readbits(record, 40, 0, 16)
            entry["item2"] = itemreward(entry["itemtype2"], entry["itemid2"])
            
            entry["itemtype3"] = readbyte(record, 56)
            entry["itemid3"] = readbyte(record, 60)
            entry["itemamount3"] = readbits(record, 64, 0, 16)
            entry["item3"] = itemreward(entry["itemtype3"], entry["itemid3"])
            
            self.stageRewards[stageindex] = entry
    
    def printdata(self):
        for stageindex in self.stageRewards.keys():
            entry = self.stageRewards[stageindex]
            rewardstring = "{} x{}".format(entry["item"], entry["itemamount"])
            if entry["itemamount2"] != 0:
                rewardstring += " + {} x{}".format(entry["item2"], entry["itemamount2"])
            if entry["itemamount3"] != 0:
                rewardstring += " + {} x{}".format(entry["item3"], entry["itemamount3"])
            print "Stage Index {} reward: ".format(stageindex) + rewardstring
