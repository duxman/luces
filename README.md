# Duxman Luces
### More info y blog

http://duxnet.es/luces/

### Install
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
For use with MP3 file you need ffmepg instaled in your system 
make sure you have ffmpeg and ffprobe in your path of execution

### Configure
Modify the following files y config directory.

**configuration.json**

It is the general configuration of the program

This file contains 

````
  "GeneralPins"   : General configured pines ( not in use)
  "MusicPath"     : Music directory
  "FfmpegPath"    : ffmpeg path , only for windows,
  "WebServerPort" : web server port
````

**programacion.json**

It is the time config of the program
 
This file contains 

````
  "StartTime" : Start Time,
  "EndTime"   : End Time
  "State"     : Not in use
  "WaitTime"  : Wait Time between executions
````

**ProgramConfiguration.json**

In this file we configure the music file or the sequence string  

This file contains 

````
  "ProgramName"         : Program name
  "ProgramType"         : Indicate if the program use music o programed sequeneces
                          SEQ   -> Execute Secuence
                          MUSIC -> execute with music file 
  "ProgramInterval"     : Wait time between executions
  "Sequences"           : Array of Zones to activate 
  "MusicFiles"          : Arrray of songs wav or mp3 files
                          The mp3 files will beed converted to wav the first time we play then.                    
````
**Zones.json**

In this file we configure the predefines zones with the pins used in every zone

This file contains 

````
  "ZoneType"   : It is GPIO or MCP
                 (if we use MCP we need to configure I2CConfig.json file)
  "Zones"      : Array of Zones
  [
        ZoneName : Name of the zone
        ZonePins : Comma separated string with the used pins in this zone
  ]                                     
````

**I2CConfig.json**

In this file we configure the I2CDevices I use MCP23016 port expander 

This file contains 

````
  "Devices"   : Array of devices                   
  [
        BasePin    : Initial pin number for this I2C Device, 
                     in this way with MCP it is the first digital pin in this MCP 
        
        I2CAddress : Address of the MCP device
  ]                                     
````


### Execute

For use the main program execute this command
````
    sudo python luces/main.py
````

For test a Song execute this command
````
    sudo python luces/PlayMusic.py -i <Path to song in wav>
    
    example :
    sudo python luces/PlayMusic.py -i ./music/sample.wav
````

For test a Sequence execute this command
````
    sudo python luces/PlaySequence.py -i <Comma separated sequece>
    
    example :
    sudo python luces/PlaySequence.py -i 1,3,1,4,2,1,5,2,3,4,5    
````

Convert mp3 to wav
````
    sudo python luces/util/Mp3ToWav.py -i <Mp3FileNanme> -p <Path>
    
    example :
    sudo python luces/PlaySequence.py -i sample.mp3 -p ../music
    
    you'll get ../music/sample.mp3.wav    
````

