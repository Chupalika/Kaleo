# .bin Split and Dump

This tool takes a Pokémon Shuffle .bin file, splits its data segment into its component records, and generates separate .bin files for each record AS WELL AS a binary dump of same (the .bind file). Useful for figuring out formatting.

## Usage
```./binsplitndump.py file_to_dump [file_to_dump ...]```

For each file you list, it’ll assume it’s a Pokémon Shuffle .bin file and create a folder, with two files in the folder for each record. This will result in a folder with a lot of stuff in it.

# .bin Search

This tool performs an hexadecimal search through the binary files. It requires https://github.com/scott-griffiths/bitstring

It will display one row per result found and highlight the pattern

Each row is displayed they way most hexadecimal works: row address, bytes, characters and the last value is the address of the matched pattern. 

## Usage
```./binsearch.py "0x54 00 68 00 65 00 20 00 6D 00 6F 00 72 00 65 00" "..\..\data\App Data\*\*.bin"```

Spaces are optional in the pattern:

```./binsearch.py "0x54006800650020006D006F0072006500" "..\..\data\App Data\*\*.bin"```




