# -*- coding: utf_8 -*-

#!/usr/bin/python

import sys, os.path, random
sys.path.append("../")
from bindata import *
from stageinfo import *

#Calculate the number of hearts required to clear an EB, always playing with the same number of hearts to abuse different skip probabilities
#Usage: python eb_hearts.py appdatafolder extdatafolder [repeats] [mobile=m]
#Example1: python eb_hearts.py appdatafolder extdatafolder 10000 m
#Example2: python eb_hearts.py appdatafolder extdatafolder m
#- appdatafolder is the folder that holds data extracted from the app itself
#- extdatafolder is the folder that holds data extracted from downloaded extra data (aka update data)
#- repeats is number of EB executed
#- mobile determine the data structure

skips_quota=[3, 5]
fallback_skips_prob={0:0.3, 2:0.22, 4:0.15, -1:0.35}
skips_prob={}

class EB_Hearts(EventDetails):
	def simulate_eb(self, repeats = 10000):
		if self.stagetype != 6: return
		s = self.extravalues
		while s[-1] % 50 == 1 or s[-2] > s[-1]: s.pop()
		if s[-1] % 50 != 0: s.append(s[-1] + 50 - (s[-1] % 50))
		stages = zip(s, [r - 1 for r in s[1: ] + [s[-1] + 1]])
		start_level = 1
		start_stage = 0
		ret = []
		for k in skips_prob.keys():
			hearts = 0
			for i in range(repeats):
				curlevel = start_level
				canskip = -1
				curstage = start_stage
				while curlevel <= stages[-1][0]:
					if canskip >= 0 and random.random() <= skips_prob[k] and stages[curstage][1] > stages[curstage][0]:
						skip = max(0, min(random.randint(skips_quota[0], skips_quota[1]), stages[curstage][1] - curlevel))
						if skip >= skips_quota[0]:
							curlevel += skip
							canskip = -skips_quota[0]
					hearts += 1
					canskip += 1
					curlevel += 1
					if len(stages[curstage]) == 1 or curlevel > stages[curstage][1]: curstage += 1
			ret.append({"hs": k, "hearts": float(hearts) / float(repeats)})
		ret = sorted(ret, key = lambda x: x["hearts"])
		print "{} EB, {} stages, {} skips:".format(self.stagepokemon, stages[-1][0], skips_quota)
		for j, v in enumerate(ret): print "\tHearts {}:\t{}\t{}".format(v["hs"], round(v["hearts"], 1), ["+{}".format(round(v["hearts"] - ret[0]["hearts"], 1)), ""][j == 0])

BinStorage.workingdirs["ext"] = os.path.abspath(sys.argv[2])
BinStorage.workingdirs["app"] = os.path.abspath(sys.argv[1])
mobile = ""
eb_repeats = 10000
if (len(sys.argv) > 3):
	if sys.argv[3] == "m": mobile = "m"
	else:
		eb_repeats = int(sys.argv[3])
		if (len(sys.argv) > 4 and sys.argv[4] == "m"): mobile = "m"
try:
	escBin = BinStorage("Configuration Tables/levelUpAngryParam.bin")
	prevdata = 0.
	for record in range(escBin.num_records)[::-1]:
		thisRecord = escBin.getRecord(record)
		newdata = readfloat(thisRecord, 4)
		if newdata != prevdata:
			sid = readbits(thisRecord, 0, 0, 4)
			if sid == 15: sid = -1
			skips_prob[sid] = newdata
			prevdata = newdata
except:
	skips_prob = fallback_skips_prob
	print "Using fallback skip probabilities {}.\n".format(fallback_skips_prob)
try:
	sdata = StageData("Configuration Tables/stageDataEvent.bin")
	eventBin = BinStorage("Configuration Tables/eventStage.bin")
	for i in range(eventBin.num_records):
		snippet = eventBin.getRecord(i)
		record = EB_Hearts(i, snippet, sdata, mobile = mobile)
		record.simulate_eb(eb_repeats)
except IOError:
	sys.stderr.write("Couldn't find the bin file to extract data from.\n")
	raise
