#This tool searches for an integer value in a binary file by converting both to binary and comparing substrings of the binary file to the target binary
#Argument 1: binary file name
#Argument 2: target integer value

import sys

#Converting a byte to binary apparently strips off the 0's at the front. This fills the string with 0's back up to length 8.
def fillgapsinbinary(str):
    ans = str
    while len(ans) != 8:
        ans = "0" + ans
    return ans

#generate an entire string of binary from string data
def generatebinary(snippet):
    lines = []
    for x in snippet:
        lines.append(fillgapsinbinary(format(ord(x), 'b')))
    string = ""
    ugh = range(len(lines))
    ugh.reverse()
    for i in ugh:
        string += lines[i]
    return string

#read files, generate binary string
file = open(sys.argv[1])
filecontents = file.read()
binary = generatebinary(filecontents)

#convert target integer to binary
target = int(sys.argv[2])
targetbinary = "{0:b}".format(target)
targetlength = len(targetbinary)

#search for target binary in string binary and print any matches!
for i in range(len(binary) - targetlength + 1):
    snippet = binary[len(binary)-i-targetlength:len(binary)-i]
    if snippet == targetbinary:
        print "Match found at byte {} bit {}".format(i/8, i%8)