#import RPi.GPIO as GPIO #importamos la libreria y cambiamos su nombre por "GPIO"

import os
import time  # necesario para los delays
if os.name == 'poxis':
    import RPi.GPIO as GPIO
else:
    import tool.EmulatorGUI as GPIODEV
    GPIO = GPIODEV.emulatorGPIO()


class PinControl(object):
    Logger = None
    Zones = None
    PinList = []

    def __init__(self, log , z):
        self.Logger = log
        self.Zones = z
        self.gpio_setup()
        for zone in self.Zones.DefinedZones:
            self.gpio_setup_pins(zone.ZonePins)
            for i in zone.ZonePins:
                self.PinList.append(i)


    def gpio_setup( self ):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

    def gpio_setup_pins(self, pinList):
        GPIO.setup(pinList, GPIO.OUT)
        GPIO.output(pinList, GPIO.LOW)

    def Encender( self,pin ):
        GPIO.output(pin, True )

    def Apagar( self,pin ):
        GPIO.output( pin, False)

    def EncenderyEsperar( self,pinList, time ):
        for pin in pinList:
            self.Encender( pin )
            time.sleep( time)
            self.Apagar( pin )

    def EjecutarSecuencia( self,secuencia, intervalo ):
        GPIO.output(secuencia, GPIO.HIGH)
        time.sleep( intervalo)
        GPIO.output(secuencia, GPIO.LOW)


        for pin in secuencia:
            self.Apagar( pin )

    def EncenderTodo(self):
        for pin in self.PinList:
            self.Encender(pin)

    def ApagarTodo(self):
        for pin in self.PinList:
            self.Apagar(pin)


    def EncenderInRangeZone(self,  MaxValue):

        zonestoup = self.Zones.DefinedZones[:MaxValue]
        data=[]
        if os.name == 'poxis':
            GPIO.output(self.PinList, GPIO.LOW)
        if( MaxValue > 0):
            for zone in zonestoup:
                data.extend(zone.ZonePins)
            data = list(set(data))
            GPIO.output(data, GPIO.HIGH)
        else:
            if os.name == 'poxis':
                GPIO.output(self.PinList, GPIO.LOW)
            else:
                GPIO.output(0, GPIO.LOW)

    def EncenderInRange(self,  MaxValue):
        valortemp = MaxValue

        secuencia = self.PinList[:valortemp]
        if os.name == 'poxis':
            GPIO.output(self.PinList, GPIO.LOW)
        if( MaxValue > 0):
            GPIO.output(secuencia, GPIO.HIGH)
        else:
            if os.name == 'poxis':
                GPIO.output(self.PinList, GPIO.LOW)
            else:
                GPIO.output(0, GPIO.LOW)



    def EjecutarPrograma( self,pinProgram , repeticiones , intervalo ):
        iteracion = 0
        if repeticiones > 0:
            while iteracion < repeticiones:
                iteracion = iteracion + 1
                for secuencia in pinProgram:
                    self.EjecutarSecuencia( secuencia, intervalo )
        else:
            while True:
                for secuencia in pinProgram:
                    self.EjecutarSecuencia( secuencia, intervalo )

