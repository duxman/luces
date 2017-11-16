#import RPi.GPIO as GPIO #importamos la libreria y cambiamos su nombre por "GPIO"

import time  # necesario para los delays

import EmulatorGUI as GPIO   # import RPi.GPIO as GPIO


def gpio_setup( pinList ):

    GPIO.setmode(GPIO.BCM)
    for pin in pinList:
       GPIO.setup( pin,GPIO.OUT)
       GPIO.output( pin, False)

def Encender( pin ):
    GPIO.output(pin, True )

def Apagar( pin ):
    GPIO.output( pin, False)

def EncenderyEsperar( pinList, time ):
    for pin in pinList:
        Encender( pin )
        time.sleep( time)
        Apagar( pin )

def EjecutarSecuencia( secuencia, intervalo ):
    for pin in secuencia:
        Encender( pin )

    time.sleep( intervalo)

    for pin in secuencia:
        Apagar( pin )

def EjecutarPrograma( pinProgram , repeticiones , intervalo ):
    iteracion = 0
    if repeticiones > 0:
        while iteracion < repeticiones:
            iteracion = iteracion + 1
            for secuencia in pinProgram:
                EjecutarSecuencia( secuencia, intervalo )
    else:
        while True:
            for secuencia in pinProgram:
                EjecutarSecuencia( secuencia, intervalo )

pinlist = {2,3,4,17,27,22,10,9,11,5,6,13,19,26}
programa  = [[2,3,4,17],[27,22,10,9],[11,5,6],[13,19,26]]
gpio_setup( pinlist )
EjecutarPrograma(programa,10,0.5)
