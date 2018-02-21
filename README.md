# Kaleo
Pokémon Shuffle data parser, based off of [xJakub's parser](https://github.com/xJakub/ShuffleParser/) and named after [KaleoX](http://www.gamefaqs.com/community/KaleoX)

## Requirements
* The parser runs using Python 2.7. Using Python 3 will generate syntax errors...
* .bin files are needed for the parser to extract data from. [Chopra](https://github.com/bkimmett/Chopra) should output the files with the correct folders and file names. Just provide the folder names in the arguments. If it can't find a needed file, it'll output an error with the name.

## Usage
```python shuffleparser.py appdatafolder extdatafolder datatype parameters```

appdatafolder: The folder that holds data extracted from the app itself  
extdatafolder: The folder that holds data extracted from downloaded extra data (aka update data)  
datatype: The type of data to parse. Should be one of these values:  
* "stage", "expertstage", "eventstage"  
-- Outputs stage data  
-- Parameters: index, extraflag ("m", "d", "md")
* "layout", "expertlayout", "eventlayout"  
-- Outputs board layout info  
-- Parameters: index, extraflag ("l")
* "pokemon"  
-- Outputs pokemon data  
-- Parameters: index, extraflag ("m")
* "ability"  
-- Outputs skill data  
-- Parameters: index
* "escalationanger"  
-- Outputs the probability rates for skips on Escalation Battles  
* "eventdetails"  
-- Outputs details of each event in the event schedule  
-- Parameters: extraflag ("m")
* "escalationrewards", "comprewards", "stagerewards"  
-- Outputs rewards for Escalation Battles, Competitive Stages, or Main Stages
* "exptable"  
-- Outputs an EXP table
* "noticedurations"  
-- Outputs durations of notices (not yet able to tell which notice each duration points to)
* "message", "appmessage"  
-- Formats and outputs messages from a message file in the extdatafolder or appdatafolder  
-- Parameters: category
* "trainerrank"  
-- Outputs a list of number of Pokemon needed to catch to reach a trainer rank
* "monthlypikachu"  
-- Outputs a list of Pikachu that are given out per month
* "stampbonus"  
-- Outputs the rewards from the stamp card feature

parameters: Depends on which datatype is being requested. In general, the first parameter is an index, and the second parameter is an extra flag.  
index: Used for stage data, stage layouts, pokemon, and ability. Should be an integer or "all".  
extraflag: An extra flag. Can be any of these values:  
* "l" to enable layout image generation when parsing for stage layouts
* "m" to switch to mobile data parsing when parsing for stage data
* "d" to enable output of Disruptions when outputting stage data
* "md" is a combination of "m" and "d"

category: Used for outputting messages. What should be passed in here is the part of the file name after "message" and before "_US". For example, if outputting from "messagePokedex_US.bin", "Pokedex" should be passed in as the parameter.

Result is printed onto the console, it can be outputted to a file by adding "> output.txt" at the end of the command.

## Layout Image Generation
When retrieving data for stage layouts, use the extraflag "l" to enable layout image generation, which will create and save image files to the current directory. Things to note:
* At the moment, this feature requires a folder called "Icons" with png files of the Pokemon in it
* Python 32-bit can't generate more ~4 layouts in one sitting, it will crash with a Memory Error. Therefore, Python 64-bit is highly recommended.
* This feature requires OpenCV to be installed, follow steps 4-7 [here](http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_setup/py_setup_in_windows/py_setup_in_windows.html#install-opencv-python-in-windows)
* This feature requires numpy to be installed, just execute command ```pip install numpy```

## 3DS vs Mobile
Mobile files, for the most part, have the same format as 3DS files. There are some discrepancies, such as stage data pokemon data, and event details. When parsing for stage data from Mobile files, use the extraflag "m" to set a flag which will parse a little differently.
