## Duxman Luces
###### Install
download the repository
````
https://github.com/duxman/luces.git
````
install the following packages
````
python -m pip install numpy
python -m pip install pyaudio
python -m pip install pydub
````
###### Configure
Modify the following files y config directory.

**configuration.json**

This file contains 

````
  "GeneralPins"   : General configured pines ( not in use)
  "MusicPath"     : Music directory
  "FfmpegPath"    : ffmpeg path , only for windows,
  "WebServerPort" : web server port
````

**programacion.json**

This file contains 

````
  "StartTime" : Start Time,
  "EndTime"   : End Time
  "State"     : Not in use
  "Programs"  : list of files led(1..n).json config files comma separated"
````

**led(1..n).json**

This file contains 

````
  "Name"         : Program name
  "Pins"         : Configured pins for this song
  "Music"        : wav file song,
  "Secuence"     : num of pins to activate
  "Interval"     : sleep time
  "Repeat"       : repeat times
  "Type"         : Execute mode
                   SEC   -> Execute Secuence
                   MUSIC -> execute with music file

````

###### Execute
````
sudo python luces/main.py
````
