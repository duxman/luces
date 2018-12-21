#import RPi.GPIO as GPIO #importamos la libreria y cambiamos su nombre por "GPIO"

import os
import time  # necesario para los delays

import RPi.GPIO as GPIO

class PinManager(object):
    Logger = None
    PinList = None

    def __init__(self, log , pinlist):
        self.Logger = log
        self.PinList = pinlist
        self.gpio_setup( self.PinList)


    def gpio_setup( self, pinList ):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
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

    def EncenderInRange(self,  MaxValue):
        valortemp = MaxValue

        #valortemp = valortemp + (MaxValue - 1)
        ListPines =  self.PinList.split(',');
        secuencia = ListPines[:valortemp]
        if os.name == 'poxis':
            GPIO.output(ListPines, GPIO.LOW)
        if( MaxValue > 0):
            GPIO.output(secuencia, GPIO.HIGH)
        else:
            GPIO.output(ListPines, GPIO.LOW)


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

