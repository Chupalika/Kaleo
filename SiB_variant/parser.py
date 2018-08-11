from __future__ import division
import math
import bitstring #if you get an error message, go to https://github.com/scott-griffiths/bitstring and install the module
from struct import unpack_from as unpack

#in loving memory of KaleoX. RIP. You brought a community together.

drop_item_master_list = {1:"RML", 3:"Exp. Booster S", 4:"Exp. Booster M", 5:"Exp. Booster L", 6:"Skill Booster S", 7:"Skill Booster M", 8:"Skill Booster L", 10:"MSU", 23:"10 Hearts", 30:"5000 Coins", 32:"PSB"} #as determined by Sonansu
	#not determined: '1000 coins', '100 / 300 / 2000' coins - TODO

def split_records(binfile):
	with io.open(binfile, mode='rb') as file_to_split:
		file_contents = file_to_dump.read()
		
	num_records = unpack("<I",file_contents[0:4])[0]
	record_len = unpack("<I",file_contents[4:8])[0]
	start_point = unpack("<I",file_contents[16:20])[0]
	
	for record in range(num_records):
		yield file_contents[start_point+record_len*record:start_point+record_len*(record+1)]


def setupBits(bindata):
	newBits = bitstring.BitStream(bytes=bindata[::-1])
	newBits.reverse()
	#it's as though each bit was flipped in place, allowing reading from LSB to MSB in the traditional L/R pattern. Must reverse() any bit string read out.
	return newBits
	
def readBool(bitstream_to_read):
	return bitstream_to_read.read(1).bool

def readBits(bitstream_to_read, bits_to_read):
	#this works because the bitstream's "pos" property is updated on each read. It's like a little file pointer! You can reset it if you want to read elsewhere.
	print(bitstream_to_read.bin)
	theseBits = bitstream_to_read.read(bits_to_read) #get the section of the bits themselves
	
	leftover_bits = 8 - bits_to_read % 8
	leftovers = bitstring.BitArray(uint=0,length=leftover_bits) #generate padding
	theseBits.append(leftovers) #pad with 0s on unused MSBs
	theseBits.reverse() #flip for big-endian binary integer reading
	
	bits_needed = bits_to_read+leftover_bits #how many bits do we want to read? ALWAYS a multiple of 8 - needed for conversion.
	
	return theseBits.read(bits_needed).uint
	
	
	
#bittest = setupBits(b'\x9E\x85')
#print(readBits(bittest,7))
#print(readBits(bittest,7))

def parseStageData(datarecord):
	stageBits = setupBits(datarecord)
	
	output = ""

	indexNo = readBits(stageBits,10) #purpose: unknown
	isMega = readBits(stageBits,4) ##not all bits of this may be used for this
	
	
	skyfallCount = readBits(stageBits,4) ##how many distinct items are in the skyfall pool? normally '4' for most stages, '3' for 3-mon stages, '5' for stages with a fifth support...
	
	
	
	if skyfallCount > 7:
		#NOTE: the 4th (MSB) bit of skyfallCount may not be part of skyfallCount at all. Need to investigate this. 
		print("That's interesting. This is supposedly an 8+-support stage, which seems a tad off. Please send the info of which stage you were reading to SoItBegins.")
	
	
	timeActive = readBool(stageBits)
	
	time = readBits(stageBits,13)
	
	if timeActive and time > 511:
		print("That's interesting. Either this is the longest stage ever, or the back half of the 'time' field might be being used for something else. Please send the info of the stage you were reading to SoItBegins.")
	
	if not timeActive and time != 0:
		print("That's interesting. There's something in the 'time' field even though this stage isn't a timed stage (I think). This message might or might not appear in error... anyway, please notify SoItBegins.")



	hp = readBits(stageBits,20) #is this really 20 bits long?
	

	
	stageBits.pos = 48*8+2 #skip ahead - disruptions in here but don't know how to read them
	
	rank_threshold = [0,0,0] #S, A, B move threshold
	for item, _ in enumerate(rank_threshold):
		rank_threshold[item] = readBits(stageBits, 10)
		
	catch_base = readBits(stageBits,7) #the 'X' in X+Y%
	catch_bonus = readBits(stageBits,7)# the 'Y'
	
	stageBits.pos = 56*8+7 #25 bits unaccounted for
	
	coins_repeat = readBits(stageBits,16)
	idk59 = readBits(stageBits,9) #mystery
	coins_once = readBits(stageBits,16)
	idk62 = readBits(stageBits,16) #mystery
	xp = readBits(stageBits,16)
	
	idk66 = readBits(stageBits,8) #mystery? may be unused
	
	#DROP RATES EXPLAINED
	#each drop slot is a 12-bit segment.
	#the first 8 bits say what drops.
	#"32" (00100000) = PSB. 
	#TBD for other drops.
	#the next 4 bits are the drop rate.
	#0 = no drop. 
	#>0 = 1/(2^(N-1)) - so 1 = 1/1 = 100%, 2 = 1/2 = 50%, 3 = 1/4 = 25%, ETC
	
	drop_rates = []
	drop_items = []
	
	for drop_slot in range(3):
		drop_item = readBits(stageBits,8)
		drop_rate = readBits(stageBits,4)
		if drop_rate > 0:
			drop_rates.append(drop_rate)
			drop_items.append(drop_item)
			
	drop_rates, drop_items = zip(*sorted(zip(drop_rates,drop_items))) #sorts them by decreasing drop frequency
	
	idk71 = readBits(stageBits,7) #these bits after the drop rate are still unaccounted for.
	
	musicID = readBits(stageBits,16)
	
	stageBits.pos += 5*8+5 #5 bytes + 5 bits unaccounted for
	
	extra_hp = readBits(stageBits,16) #wtf is this?
	layout_id = readBits(stageBits,16)
	default_supp = readBits(stageBits,16)
	moves = readBits(stageBits,8)
	idk87 = readBits(stageBits,10) #another unknown
	bgid = readBits(stageBits,8) 
	
	
	output += "{} {}\n".format(("Mega " if isMega else ""), "NAME TODO")
	
	output += str(hp)+" HP\n"
	if timeActive:
		output += "Time: "
		if time > 59:
			movesStr += str(time//60)+":"+str(time%60)
		else:
			movesStr += str(time)+" seconds"
	else:
		output += "Moves: "+str(moves)
	output += "\n"
	output += "Catch Rate: {}+{}%\n".format(catch_base,catch_bonus)
	output += "S/A/B rank: {} {}\n\n".format([str(x) for x in rank_threshold].join("/"), "seconds" if timeActive else "moves")

	
	output += "Starting layout: TODO ("+str(layout_id)+")\n"
	
	output += str(skyfallCount)+"-support Stage\n"
	output += "Supports: TODO ("+str(default_supp)+")\n"
	
	output += "Disruptions are TODO.\n\n"
	
	
	output += "{} Coins the first time, {} thereafter\n".format(coins_once,coins_repeat)
	output += "{} XP \n".format(xp)
	
	output += "Drops: " 
	if len(drop_item) == 0:
		output += "None.\n\n"
	else:
		drop_item_str = ""
		drop_rate_str = "("
		first = True
		for index, item in enumerate(drop_items):
			if first:
				first = False
			else:
				drop_item_str += " / "
				drop_rate_str += "/"
			if item in drop_item_master_list.keys():
				drop_item_str += drop_item_master_list[item]
			else:
				drop_item_str += "UNKNOWN ("+str(item)+")"
			drop_rate_str += "{.2g}".format(1/(2**(drop_rates-1))
				
		
		output += drop_item_str + " " + drop_rate_str + "%)\n\n"

	
	output += "BG: "+str(bgid)+" Music: "+str(musicID)+"XHP: "+str(extra_hp)+"\n"
	output += "IDKs: {} {} {} {} {}".format(idk59,idk62,idk66,idk71,idk87)
	
	return output
	
	
	#there are 2 bytes, 6 bits leftover.
	
	
	#BITS UNACCOUNTED FOR:
	#from byte 6, bit 5 to byte 48, bit 2 (almost certainly disruptions) [41 bytes, 6 bits (334)]
	#from byte 53, bit 7 to byte 56, bit 7 [3 bytes, 1 bit (25)]
	#byte 56, bit 8 and all of byte 57 [9 bits]
	#bytes 62 and 63
	#byte 66
	#4 bits of byte 71 and 3 bits of byte 72 [(7)]
	#5 bits of byte 74, bytes 75-79 [(45)]
	#byte 87 and 2 bits of byte 88
	#6 bits of byte 89, and then bytes 90-91
	
	#STAGE QUALITIES UNDISCOVERED:
	#Disruptions. 
	#Entry fee. lock entry fee.
	# # plays allowed (before disappearing).
	# same (before 'locking' and after and all that nonsense).
	#start/end dates? or is this found elsewhere?
	
	
#	Jakub's parser does:
#	
#     private function parseV13($line)
#     {
#         $this->pokemonIndex = readBits($line, 0, 0, 10);
#         $this->skyfallCount = readBits($line, 1, 6, 4);
#         $this->time = readBits($line, 2, 3, 15);
#         $this->hp = readBits($line, 4, 0, 20);
# 
#         $this->Srank = readBits($line, 48, 2, 10);
#         $this->Arank = readBits($line, 49, 4, 10);
#         $this->Brank = readBits($line, 50, 6, 10);
#         $this->catchRate = readBits($line, 52, 0, 7);
#         $this->bonusRate = readBits($line, 52, 7, 7);
#         $this->repeatCoins = readBits($line, 56, 7, 16);
#         $this->firstTimeCoins = readBits($line, 60, 0, 16);
#         $this->expYield = readBits($line, 64, 0, 16);
#         $this->trackId = readBits($line, 72, 3, 16);
#         $this->backgroundId = readBits($line, 88, 2, 8);
#         $this->extraHp = readBits($line, 80, 0, 16);
#         $this->layoutIndex = readBits($line, 82, 0, 16);
#         $this->defaultSetIndex = readBits($line, 84, 0, 16);
#         $this->moves = readBits($line, 86, 0, 8);
# 
#     }


def parsePokemonData(datarecord):
	pokeBits = setupBits(datarecord)
	
	
	
	
	
	#worth checking: 'show in dex? y/n' - in 1420, Bulu is noshow, in 1421 he is.
	#not in jakub's: RMLs, alt abilities

	
	
#    {
#         $this->dexNumber = readBits($line, 0, 0, 10);
#         $this->typeIndex = readBits($line, 1, 3, 5);
#         $this->abilityIndex = readBits($line, 2, 0, 7);
#         $this->growthId = readBits($line, 3, 0, 4);
#         $this->nameIndex = readBits($line, 6, 5, 11);
#         if ($this->formeNameIndex = readBits($line, 8, 0, 8)) {
#             $this->formeNameIndex += 768;
#         }
#         $this->class = readBits($line, 9, 4, 3);
#         $this->megaEvolutionIcons = readBits($line, 10, 0, 7);
#         $this->speedups = readBits($line, 10, 7, 7);
# 
#         if ($mega = readBits($line, 12, 0, 11)) {
#             $this->megaIndexes[] = $mega;
#         }
#         if ($mega = readBits($line, 13, 3, 11)) {
#             $this->megaIndexes[] = $mega;
#         }
#     }