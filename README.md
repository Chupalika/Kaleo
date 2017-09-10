# Kaleo
Pokémon Shuffle data parser, based off of [xJakub's parser](https://github.com/xJakub/ShuffleParser/) and named after [KaleoX](http://www.gamefaqs.com/community/KaleoX)

## Requirements
* The parser runs using Python 2.7. Using Python 3 will generate syntax errors...
* .bin files are needed for the parser to extract data from. They should be in the same folder as the parser. If it can't find it, it'll output an error with the name of the file needed.

## Usage
```python shuffleparser.py datatype index```

Possible values for datatype:  
* "stage"
* "expertstage"
* "eventstage"
* "layout"
* "expertlayout"
* "eventlayout"
* "pokemon"
* "ability"

Possible values for index: any integer, "all"  

## Layout Image Generation
When retrieving data for stage layouts, add a third argument "l" to enable layout image generation, which will create and save image files to the current directory. Things to note:
* At the moment, this feature requires a folder called "Icons" with png files of the Pokemon in it
* Python 32-bit can't generate more ~4 layouts in one sitting, it will crash with a Memory Error. Therefore, Python 64-bit is highly recommended.
* This feature requires OpenCV to be installed, follow steps 4-7 [here](http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_setup/py_setup_in_windows/py_setup_in_windows.html#install-opencv-python-in-windows)
* This feature requires numpy to be installed, just execute command ```pip install numpy```

Result is printed onto the console, it can be outputted to a file by adding "> output.txt" at the end of the command
