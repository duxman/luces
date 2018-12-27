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
  "Pines"       : General configured pines ( not in use)
  "RutaMusica"  : Music directory
  "Rutaffmpeg"  : ffmpeg path , only for windows,
  "WebServerPort" : web server port
````

**programacion.json**

This file contains 

````
  "HoraDesde" : Start Time,
  "HoraHasta" : End Time
  "Estado"    : Not in use
  "Programa"  : list of files led(1..n).json config files comma separated"
````

**led(1..n).json**

This file contains 

````
  "pines"         : Configured pins for this song
  "musica"        : wav file song,
  "secuencia"     : Not in use
  "intervalo"     : sleep time
  "repeticiones"  : repeat times
````

###### Execute
````
sudo python luces/main.py
````
