import time

import neopixel
import board
# See https://learn.adafruit.com/neopixels-on-raspberry-pi/software
#sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
#sudo python3 -m pip install --force-reinstall adafruit-blinka
from Animation import Animation
from Panel import Panel


class AnimationServer():

    velocidad = 0.075
    panel: Panel = None


    ################################################################
    #               Probably not configurable
    ################################################################
    LedPin = 18  # GPIO pin connected to the pixels (must support PWM!).
    LedFreqHz = 800000  # LED signal frequency in hertz (usually 800khz)
    LedDma = 5  # DMA channel to use for generating signal (try 5)
    LedBrigh = 255  # Set to 0 for darkest and 255 for brightest
    LedInvert = False  # True to invert the signal (when using NPN transistor level shift)
    LedStrip: neopixel.NeoPixel = None

    def __init__(self, panel: Panel, velocidad: float):

        self.velocidad=velocidad
        self.panel = panel
        self.LedStrip = neopixel.NeoPixel(board.D18,
                                          panel.total_leds,
                                          auto_write=False
                                          )

        ORDER = neopixel.GRB

        #self.LedStrip = neopixel.NeoPixel(self.LedPin, panel.total_leds, auto_write=False)

        print("inicilizamos ledstrip {0}".format(panel.total_leds))
        #self.LedStrip = neopixel.NeoPixel(board.D18, panel.total_leds)

    def allonecolour(self, strip, colour):
        # Paint the entire matrix one colour
        strip.fill(colour)
        strip.show()

    def colour(self, r, g, b):
        # Fix for Neopixel RGB->GRB, also British spelling
        return self.colourTuple([g, r, b])

    def colourrgb(self, r, g, b):
        # Fix for Neopixel RGB->GRB, also British spelling
        return [g, r, b]

    def colourTuple(self, rgbTuple):
        red = rgbTuple[1]
        green = rgbTuple[0]
        blue = rgbTuple[2]
        RGBint = (green << 16) + (red << 8) + blue
        return RGBint

    def colourTupleRGB(self, rgbTuple):
        red = rgbTuple[0]
        green = rgbTuple[1]
        blue = rgbTuple[2]

        return ( red,green, blue)

    def startAnimation(self, animation: Animation, panel: Panel):
        # And here we go.

        try:
            # Loop through the image widthways
            # Can't use a for loop because Python is dumb
            # and won't jump values for FLIP command
            x = 0
            # Initialise a pointer for the current line in the text file
            tx = 0

            print("Iniciamos reproduccion {0}<{1}-{2}".format(x,animation.imagen_final.size[0],animation.imagen_final.width))
            while x < animation.imagen_final.size[0] - panel.width:
                # Set the sleep period for this frame
                # This might get changed by a textfile command
                thissleep = self.velocidad

                # Set the increment for this frame
                # Typically advance 1 pixel at a time but
                # the FLIP command can change this
                thisincrement = 1

                rg = animation.imagen_final.crop((x, 0, x + animation.width, animation.height))
                #rg = animation.imagen_final.crop((x, 0, x + animation.imagen_final.width * panel.paneles_horizontal, animation.imagen_final.height * panel.paneles_vertical))
                dots = list(rg.getdata())
                #print("tamaño {0}".format(len(panel.matriz)))
                #print(panel.matriz)

                self.LedStrip.fill((0, 0, 0))
                for i in range(len(dots)):
                    #print("id={0}".format(i))
                    id = panel.matriz[i]
                    #print("id={0} pin={1}".format(i,id))
                    if self.colourTuple(dots[i]) != 0:
                        self.LedStrip[id] = self.colourTuple(dots[i])


                self.LedStrip.show()
                x = x + thisincrement
                time.sleep(thissleep)

        except (KeyboardInterrupt, SystemExit):
            print("Stopped")