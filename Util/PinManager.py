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
# import RPi.GPIO as GPIO #importamos la libreria y cambiamos su nombre por "GPIO"

import os
import time  # necesario para los delays

import paho.mqtt.client as mqtt

from Util.ledStripMessage import ledLevel
import RPi.GPIO as GPIO

class PinControl(object):
    Logger = None
    Zones = None
    PinListRange = []
    PinList = []

    clienteMqtt: mqtt.Client = None
    token = ""

    def __init__(self, log, zones, host="", port=1883, token="PinManager"):
        self.Logger = log
        self.Zones = zones
        self.gpio_setup()
        self.clienteMqtt = mqtt.Client("PinManagerClient", True)
        self.PinList = []
        if host != "":
            self.initializeMQTT(host, port, token)

            self.PinListRange = []
            for zone in self.Zones.DefinedZones:
                if (zone.ZonePinType == "GPIO"):

                    for k in zone.ZonePins:
                        self.PinListRange.extend(zone.ZonePins[k])
                        pinttemp = [int(numeric_string) for numeric_string in zone.ZonePins[k]]
                        self.PinList.append(pinttemp)

            pins = list(dict.fromkeys(self.PinListRange))
            self.PinListRange = [int(numeric_string) for numeric_string in pins]
            self.gpio_setup_pins(self.PinListRange)

    def initializeMQTT(self, host, port, token):
        self.token = token
        self.clienteMqtt.on_connect = self.on_connect
        self.clienteMqtt.on_message = self.on_message
        self.clienteMqtt.on_publish = self.on_publish
        self.clienteMqtt.connect(host, port, 15)
        self.clienteMqtt.loop_start()

    def on_connect(self, mqttc, obj, flags, rc):
        print("rc: " + str(rc))
        mqttc.subscribe(self.token)

    def decodeMsg(self, msg):
        led = ledLevel()
        led.ParseFromString(msg.payload)
        #print("New Level {}".format(led.Level))
        #print("led.Level {} , Zones.MaxPinValue {}, self.PinList {} "
        #      .format(led.Level, self.Zones.MaxPinValue, self.PinList))
        self.ApagarTodo()
        if led.Level  < len(self.PinList):
            self.EncenderSpectrumZone(self.PinList[led.Level])
        if led.Level > self.Zones.MaxPinValue:
            self.EncenderTodo()

    def on_message(self, mqttc, obj, msg):
        #print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        self.decodeMsg(msg)

    def on_publish(self, mqttc, obj, mid):
        print("mid: " + str(mid))

    def publish(self, id):
        led = ledLevel()
        led.Level = id
        self.clienteMqtt.publish(self.token, led.SerializeToString(), 2, False)

    def publishList(self, list):
        led = ledLevel()
        for l in list:
            led.Level = l
            self.clienteMqtt.publish(self.token, led.SerializeToString(), 2, False)

    def gpio_setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

    def gpio_setup_pins(self, pinList):
        print("Set Pins {}".format(pinList))
        for p in pinList:
            print ("Set Pin {}".format(p))
            GPIO.setup(int(p), GPIO.OUT)
            GPIO.output(int(p), GPIO.LOW)
            GPIO.output(int(p), GPIO.HIGH)
            GPIO.output(int(p), GPIO.LOW)
        self.publish(0)

    def Encender(self, pin):
        GPIO.output(pin, True)

    def Apagar(self, pin):
        GPIO.output(pin, False)

    def EncenderyEsperar(self, pinList, time):
        for pin in pinList:
            self.Encender(pin)
            time.sleep(time)
            self.Apagar(pin)

    def EjecutarSecuencia(self, secuencia, intervalo):
        GPIO.output(secuencia, GPIO.HIGH)
        time.sleep(intervalo)
        GPIO.output(secuencia, GPIO.LOW)

        for pin in secuencia:
            self.Apagar(pin)

    def EncenderTodo(self):
        GPIO.output(self.PinListRange, GPIO.HIGH)
        #for p in self.PinListRange:
        #    GPIO.output(int(p), GPIO.HIGH)

    def ApagarTodo(self):
        #for p in self.PinListRange:
        #    GPIO.output(int(p), GPIO.LOW)
        GPIO.output(self.PinListRange, GPIO.LOW)

    def EncenderSpectrumZone(self, pins):
        #print(pins)
        if (len(pins) > 0):
            GPIO.output(pins, GPIO.HIGH)
            #for p in pins:
            #    GPIO.output(int(p), GPIO.HIGH)

    def EncenderInRangeZone(self, MaxValue):

        if MaxValue >= len(self.Zones.SpectrumPins):
            MaxValue = len(self.Zones.SpectrumPins) - 1
        pinstohigh = self.Zones.SpectrumPins[MaxValue]
        self.publish(MaxValue)
        self.EncenderSpectrumZone(pinstohigh)

    def EncenderInRange(self, MaxValue):
        valortemp = MaxValue

        secuencia = self.PinList[:valortemp]
        if os.name == 'poxis':
            GPIO.output(self.PinList, GPIO.LOW)

        if (MaxValue > 0):
            GPIO.output(secuencia, GPIO.HIGH)
        else:
            if os.name == 'poxis':
                GPIO.output(self.PinList, GPIO.LOW)
            else:
                GPIO.output(0, GPIO.LOW)

    def EjecutarPrograma(self, pinProgram, repeticiones, intervalo):
        iteracion = 0
        if repeticiones > 0:
            while iteracion < repeticiones:
                iteracion = iteracion + 1
                for secuencia in pinProgram:
                    self.EjecutarSecuencia(secuencia, intervalo)
        else:
            while True:
                for secuencia in pinProgram:
                    self.EjecutarSecuencia(secuencia, intervalo)
