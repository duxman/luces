# import RPi.GPIO as GPIO #importamos la libreria y cambiamos su nombre por "GPIO"

import os
import time  # necesario para los delays

from paho import mqtt

from Util.ledStripMessage import ledLevel

if os.name == 'poxis':
    import RPi.GPIO as GPIO
else:
    import tool.EmulatorGUI as GPIODEV

    GPIO = GPIODEV.emulatorGPIO()


class PinControl(object):
    Logger = None
    Zones = None
    PinList = []
    clienteMqtt: mqtt.Client = None
    token = ""

    def __init__(self, log, z, host="", port=1883, token="PinManager"):
        self.Logger = log
        self.Zones = z
        self.gpio_setup()
        for zone in self.Zones.DefinedZones:
            self.PinList.extend(zone.ZonePins)
            self.gpio_setup_pins(self.PinList)

        if host != "":
            self.initializeMQTT(host, port, token)

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
        print("New Level {}".format(led.Level))

    def on_message(self, mqttc, obj, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
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
        GPIO.setup(pinList, GPIO.OUT)
        GPIO.output(pinList, GPIO.LOW)
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
        for pin in self.PinList:
            self.Encender(pin)

    def ApagarTodo(self):
        for pin in self.PinList:
            self.Apagar(pin)

    def EncenderSpectrumZone(self, pins):
        self.Logger.info("item to show " + " ".join(pins))

        if os.name == 'poxis':
            GPIO.output(self.Zones.SpectrumPins, GPIO.LOW)

        if (len(pins) > 0):
            GPIO.output(pins, GPIO.HIGH)
        else:
            if os.name == 'poxis':
                GPIO.output(pins, GPIO.LOW)
            else:
                GPIO.output(0, GPIO.LOW)

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
