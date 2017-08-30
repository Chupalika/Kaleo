# .bin Split and Dump

This tool takes a Pokémon Shuffle .bin file, splits its data segment into its component records, and generates separate .bin files for each record AS WELL AS a binary dump of same (the .bind file). Useful for figuring out formatting.

## Usage
```./binsplitndump.py file_to_dump [file_to_dump ...]```

For each file you list, it’ll assume it’s a Pokémon Shuffle .bin file and create a folder, with two files in the folder for each record. This will result in a folder with a lot of stuff in it.
