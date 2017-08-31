# Kaleo
Pokémon Shuffle data parser, based off of [xJakub's parser](https://github.com/xJakub/ShuffleParser/) and named after [KaleoX](http://www.gamefaqs.com/community/KaleoX)

## Requirements
* The parser runs using Python 2.7. Using Python 3 will generate syntax errors...
* .bin files are needed for the parser to extract data from. They should be in the same folder as the parser. If it can't find it, it'll output an error with the name of the file needed.

## Usage
```python shuffleparser.py datatype index```

Possible values for datatype: "stage", "expertstage", "eventstage", "pokemon", "ability"  
Possible values for index: any integer, "all"  

Result is printed onto the console, it can be outputted to a file by adding "> output.txt" at the end of the command
