#import RPi.GPIO as GPIO #importamos la libreria y cambiamos su nombre por "GPIO"

import time  # necesario para los delays

import EmulatorGUI as GPIO   # import RPi.GPIO as GPIO

class PinManager(object):
    Logger = None
    PinList = None

    def __init__(self, log , pinlist):
        self.Logger = log
        self.PinList = pinlist
        self.gpio_setup( self.PinList)

    def gpio_setup( self, pinList ):
        GPIO.setmode(GPIO.BCM)
        for pin in pinList:
           GPIO.setup( pin,GPIO.OUT)
           GPIO.output( pin, False)

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
        for pin in secuencia:
            self.Encender( pin )

        time.sleep( intervalo)

        for pin in secuencia:
            self.Apagar( pin )

    def EncenderTodo(self):
        for pin in self.PinList:
            self.Encender(pin)

    def ApagarTodo(self):
        for pin in self.PinList:
            self.Apagar(pin)

    def EncenderInRange(self,  MaxValue):
        i = 0
        self.ApagarTodo()
        while i< MaxValue:
            self.Encender( self.PinList[i] )
            i = i + 1

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

