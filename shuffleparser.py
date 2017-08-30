from __future__ import division

import sys, getopt

initialoffset = 80
stagedatalength = 92
pokemondatalength = 36

pokemonlist = []

class PokemonData:
    def __init__(self, index):
        self.index = index
        
        #open file and extract the snippet we need
        file = open("pokemonData.bin", "rb")
        contents = file.read()
        begin = initialoffset + (pokemondatalength * self.index)
        end = begin + pokemondatalength
        snippet = contents[begin:end]
        self.binary = snippet
        file.close()
        
        #this is for finding the names
        if len(pokemonlist) == 0:
            definepokemonlist()

        #parse!
        self.nameindex = readbits(snippet, 6, 5, 11)
        self.name = pokemonlist[self.nameindex]
        self.modifierindex = readbits(snippet, 8, 0, 8)
        if self.modifierindex != 0:
            self.modifierindex += 768
            self.modifier = pokemonlist[self.modifierindex]
        else:
            self.modifier = ""
        self.dex = readbits(snippet, 0, 0, 10)
        self.classtype = readbits(snippet, 9, 4, 3) #0 means it's a Pokemon, 2 means it's a Mega Pokemon
        self.icons = readbits(snippet, 10, 0, 7)
        self.msu = readbits(snippet, 10, 7, 7)

        #unknown values for now"
        self.typeindex = readbits(snippet, 1, 3, 5)
        self.abilityindex = readbits(snippet, 2, 0, 7)
        self.apindex = readbits(snippet, 3, 0, 4)
        self.megaindex1 = readbits(snippet, 12, 0, 11)
        self.megaindex2 = readbits(snippet, 13, 3, 11)
    
    def printdata(self):
        pokemonfullname = self.name
        if (self.modifier != ""):
            pokemonfullname += " (" + self.modifier + ")"
        print "Name: " + pokemonfullname
        print "Dex: " + str(self.dex)
    
    def printbinary(self):
        print "\n".join(format(ord(x), 'b') for x in self.binary)

class StageData:
    def __init__(self, index, event=False):
        self.index = index
        
        #open file and extract the snippet we need
        if event:
            file = open("StageDataEvent.bin", "rb")
        else:
            file = open("stageData.bin", "rb")
        contents = file.read()
        begin = initialoffset + (stagedatalength * index)
        end = begin + stagedatalength
        snippet = contents[begin:end]
        self.binary = snippet
        file.close()
        
        #parse!
        self.pokemonindex = readbits(snippet, 0, 0, 10)
        self.megapokemon = readbits(snippet, 1, 2, 4) #determines if the pokemon is a mega pokemon
        self.numsupports = readbits(snippet, 1, 6, 4)
        self.timed = readbits(snippet, 2, 2, 1)
        self.seconds = readbits(snippet, 2, 3, 8)
        self.hp = readbits(snippet, 4, 0, 20)
        self.srank = readbits(snippet, 48, 2, 10)
        self.arank = readbits(snippet, 49, 4, 10)
        self.brank = readbits(snippet, 50, 6, 10)
        self.basecatch = readbits(snippet, 52, 0, 7)
        self.bonuscatch = readbits(snippet, 52, 7, 7)
        self.coinrewardrepeat = readbits(snippet, 56, 7, 16)
        self.coinrewardfirst = readbits(snippet, 60, 0, 16)
        self.exp = readbits(snippet, 64, 0, 16)
        self.drop1item = readbits(snippet, 67, 0, 8)
        self.drop1rate = readbits(snippet, 68, 0, 4)
        self.drop2item = readbits(snippet, 68, 4, 8)
        self.drop2rate = readbits(snippet, 69, 4, 4)
        self.drop3item = readbits(snippet, 70, 0, 8)
        self.drop3rate = readbits(snippet, 71, 0, 4)
        self.trackid = readbits(snippet, 72, 3, 6)
        self.extrahp = readbits(snippet, 80, 0, 16)
        self.moves = readbits(snippet, 86, 0, 8)
        self.backgroundid = readbits(snippet, 88, 2, 8)

        #unknown values for now
        self.defaultsetindex = readbits(snippet, 84, 0, 16)
        self.layoutindex = readbits(snippet, 82, 0, 16)
        
        if self.megapokemon == 1:
            self.pokemonindex += 1024
        self.pokemon = PokemonData(self.pokemonindex)
    
    def printdata(self):
        print "Stage " + str(self.index)
        
        pokemonfullname = self.pokemon.name
        if (self.pokemon.modifier != ""):
            pokemonfullname += " (" + self.pokemon.modifier + ")"
        print "Pokemon: " + pokemonfullname
        
        print "mystery: " + str(self.megapokemon)
        
        hpstring = "HP: " + str(self.hp)
        if (self.extrahp != 0):
            hpstring += " + " + str(self.extrahp)
        print hpstring
        if (self.timed == 0):
            print "Moves: " + str(self.moves)
        else:
            print "Seconds: " + str(self.seconds)
        print "Experience: " + str(self.exp)
        
        if (self.timed == 0):
            print "Catchability: " + str(self.basecatch) + "% + " + str(self.bonuscatch) + "%/move"
        else:
            print "Catchability: " + str(self.basecatch) + "% + " + str(self.bonuscatch) + "%/3sec"
        
        print "# of Support Pokemon: " + str(self.numsupports)
        print "Rank Requirements: " + str(self.srank) + " / " + str(self.arank) + " / " + str(self.brank)
        
        print "Coin reward (first clear): " + str(self.coinrewardfirst)
        print "Coin reward (repeat clear): " + str(self.coinrewardrepeat)
        print "Background ID: " + str(self.backgroundid)
        print "Track ID: " + str(self.trackid)
        
        if (self.drop1item != 0 or self.drop2item != 0 or self.drop3item != 0):
            print "Drop Items: " + str(self.drop1item) + " / " + str(self.drop2item) + " / " + str(self.drop3item)
            print "Drop Rates: " + str(1/pow(2,self.drop1rate-1)) + " / " + str(1/pow(2,self.drop2rate-1)) + " / " + str(1/pow(2,self.drop3rate-1))
    
    def printbinary(self):
        print "\n".join(format(ord(x), 'b') for x in self.binary)

def main(args):
    #make sure correct number of arguments
    if len(args) != 2:
        print 'need 2 arguments: datatype, index'
        sys.exit()
    
    #parse arguments
    datatype = args[0]
    index = args[1]
    
    if datatype == "stage":
        if index == "all":
            numentries = getnumentries("stageData.bin")
            for i in range(numentries):
                sdata = StageData(i)
                sdata.printdata()
                print
        else:
            sdata = StageData(int(index))
            sdata.printdata()
    
    elif datatype == "eventstage":
        if index == "all":
            numentries = getnumentries("stageDataEvent.bin")
            for i in range(numentries):
                sdata = StageData(i, True)
                sdata.printdata()
                print
        else:
            sdata = StageData(int(index), True)
            sdata.printdata()
    
    elif datatype == "pokemon":
        if index == "all":
            numentries = getnumentries("pokemonData.bin")
            for i in range(numentries):
                sdata = PokemonData(i)
                sdata.printdata()
                print
        else:
            pdata = PokemonData(int(index))
            pdata.printdata()
    
    else:
        print "datatype should be stage or pokemon"

def readbits(text, offsetbyte, offsetbit, numbits):
    ans = ""
    bytes = [ord(b) for b in text[offsetbyte:offsetbyte+4]]
    val = 0
    for i in reversed(xrange(4)):
        val *= 256
        val += bytes[i]
    val >>= offsetbit
    val &= (1 << numbits) -1
    return val

def getnumentries(filename):
    file = open(filename, "rb")
    contents = file.read()
    numentries = readbits(contents, 0, 0, 32)
    file.close()
    return numentries

def definepokemonlist():
    listfile = open("pokemonlist.txt", "r")
    thewholething2 = listfile.read()
    global pokemonlist
    pokemonlist = thewholething2.split("\n")

if __name__ == "__main__":
    main(sys.argv[1:])