#
# Copyright (c) 2020-2037 duxman.
#
# This file is part of Duxman Luces 
# (see https://github.com/duxman/luces).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import threading
import os
import time
if os.name == 'poxis':
    import RPi.GPIO as GPIO
else:
    import tool.EmulatorGUI as GPIODEV
    GPIO = GPIODEV.emulatorGPIO()

# basado en https://www.eetimes.com/author.asp?doc_id=1323030&page_number=3
# Codigo de arduino aqui es obligatorio usar wiringpi y softpwm
# pensar la posibilidad de cambiarlo a wiringPi
# En caso de usar esto seria conveniente tener solo 7 zonas que son las que usamos en el chip  solo analiza 7 bandas
# Para que tenga sentido tendremos que jugar con la intensidad de los led aqui no tiene sentido encender y apagar tipo strobe
# usamos MSGEQ7 placa ya con las resistencias
# https://www.ebay.es/itm/MSGEQ7-breakout-board-7-band-graphic-equalizer-for-audio-for-Arduino-RPi-PIC-/301210655107
# https://www.ebay.com/itm/251977940811


class MSGEQ7Data(object):
    Levels = []
    def __init__(self,niveles = []):
        self.Levels = niveles

class MSGEQ7ThreatManagerConsumer(threading.Thread):
    ColaDatos = None
    Stop = False
    def __init__(self, cola_datos):
        self.ColaDatos = cola_datos
        threading.Thread.__init__(self)

    def run(self):
        while self.Stop == False:
            data = self.ColaDatos.get()
            i=0
            for e in data.Levels:
                i = 1+1
                GPIO.analogwrite(i,e)

class MSGEQ7ThreatManagerReader(threading.Thread):
    ColaDatos = None
    ResetPin = 23
    StrobePin = 22
    ChannelPin = 15
    Stop = False


    def __init__(self, cola_datos, mmsgeq7_confgiuration):
        self.ColaDatos = cola_datos
        self.inicializaPins()
        threading.Thread.__init__(self)

    def inicializaPins(self):
        GPIO.setup(self.ResetPin, GPIO.OUT)
        GPIO.setup(self.StrobePin, GPIO.OUT)
        GPIO.setup(self.ChannelPin, GPIO.IN)
        GPIO.output(self.ResetPin,GPIO.LOW)
        GPIO.output(self.StrobePinPin, GPIO.HIGH)

    def readData(self):
        GPIO.output(self.ResetPin, GPIO.HIGH)
        GPIO.output(self.ResetPin, GPIO.LOW)
        self.sleepMicroseconds(75)
        analogData = MSGEQ7Data()
        for i in range(7):
            GPIO.output(self.StrobePinPin, GPIO.LOW)
            self.sleepMicroseconds(40)
            analogData.Levels.append( GPIO.analogread(self.ChannelPin)/4 )
            GPIO.output(self.StrobePinPin, GPIO.HIGH)
            self.sleepMicroseconds(40)
        return  analogData

    def sleepMicroseconds(self, microsconds):
        timetosleep = microsconds/1000000
        time.sleep(timetosleep)

    def run(self):
        while self.Stop == False:
            self.ColaDatos.put( self.readData() )

