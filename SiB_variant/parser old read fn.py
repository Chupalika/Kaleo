def fishOutBits(bindata, byte_to_start, bit_offset, bits_to_read):
	if bit_offset >= 8:
		byte_to_start += bit_offset // 8
		bit_offset = bit_offset % 8
	
	leftover_bits = 8 - bits_to_read % 8
	leftovers = bitstring.BitArray(uint=0,length=leftover_bits)

	bytes_needed = (bit_offset+bits_to_read) // 8 + (1 if (bit_offset+bits_to_read) % 8 else 0)
	bytes_to_read = bits_to_read+leftover_bits
	
	byte_subset = bitstring.BitStream(bytes=((bindata[byte_to_start:byte_to_start+bytes_needed])[::-1]))
	#print byte_subset.bin
	
	result = byte_subset.readlist('pad, bits:'+str(bits_to_read)+', pad:'+str(bit_offset))[0] #the whole thing is represented as a really really long big-endian number now. This slices out everything but the needed bit.
	#print result.bin
	result.prepend(leftovers)
	#print result.bin
	
	result.pos = 0
	result_int = result.read(bytes_to_read).uint
	return result_int
	
print fishOutBits(b'\x9E\x85',0,0,7)
print fishOutBits(b'\x9E\x85',0,7,7)
	