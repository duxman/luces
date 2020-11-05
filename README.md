# Duxman Luces
### More info y blog

TODO pero de los gordos(sorry in Spanish  :d )
* ~~Esp8266 (In Progress)~~ 
* ~~MQTT (usado AsyncMQTT)--~~
* ProtoBuffers para comunicacion ~~externa~~ e interna (In Progress)
* Zonas deslocalizadas (In Progress)
* ~~LedMatrix~~ ( ya lo tenemos )
* Integrar la led matrix en un hilo
* Integrar comandos en LedMatrix
* Acompasar ledmatrix con musica (animacion tipo baile)
* Animatronica ( esto seria lo mas de lo mas) 
* wifimanager en esp8266 con parametros para poder configurar MQTT (In Progress)

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
python -m pip install flask
python -m pip install paho-mqtt


Para hacer uso de las zonas remotas es necesario tener instalado Mosquito en la raspberry
o disponer de alguno servidor MQTT en nuestra red 
sudo apt-get install mosquitto*
````
For use with MP3 file you need ffmepg instaled in your system 
make sure you have ffmpeg and ffprobe in your path of execution

### Configure
Modify the following files y config directory.

**configuration.json**

It is the general configuration of the program

This file contains 

````  
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
        ZoneId   : it is the weight or the order of the zone
        ZoneName : Name of the zone
        ZonePins : Comma separated string with the used pins in this zone
        ZoneType : Indicate if the zone light alone or in spectrum mode.
                   It is usefull to highlight especific zones 
  ]                                     
````



### Execute

**For use the main program execute this command**
````
    sudo python luces/main.py
````

**For test a Song execute this command**
````
    Ahora permite zonas remotas con mqtt y esp12E
    sudo python luces/PlayMusic.py -i <Path to song in wav>
    
    example :
    sudo python luces/PlayMusic.py -i ./music/sample.wav
````

**For test a Sequence execute this command**
````
    sudo python luces/PlaySequence.py -i <Comma separated sequece>
    
    example :
    sudo python luces/PlaySequence.py -i 1,3,1,4,2,1,5,2,3,4,5    
````

**Convert mp3 to wav**
````
    sudo python luces/util/Mp3ToWav.py -i <Mp3FileNanme> -p <Path>
    
    example :
    sudo python luces/Mp3ToWav.py -i sample.mp3 -p ../music
    
    you'll get ../music/sample.mp3.wav    
````

**Serve Animation led Matrix**
````
    Now with a esp8266 ESP12E you can use my code in esp8266luces and flash your device
    With Platformio  this is a remote panel Code, controlled with WIFI
    The Comunication with MQTT and ProtoBuffers  
    sudo python serveAnimation.py -a <json animation data>'
    "{'ImageFile': 'file', 'CommandFile': '', 'width': 128, 'heigt': 8, 'Repetitions': 5, 'Speed': 0.1}"
            
    example :
    none        
````
[![Demo Video](./media/VID_20201031_234133.mp4)]("Demo Video")

