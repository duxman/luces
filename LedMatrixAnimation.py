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


# Credits to Andrew Oakley www.aoakley.com
# Thanks a lot for the inspiration of this program
# By parameter takes resolution and image and create animation
import getopt
import json
import time, sys, os
import paho.mqtt.client

# if os == 'poxis':

# else:
# from Util.neopixelsimulator import NeoPixel, RGB

from PIL import Image  # Use apt-get install python-imaging to install this

from config import animation


class matrixAnimation(object):
    Logger = None
    ImageFile = ""
    Config = None
    loadIm = None
    origIm = None
    im = None
    txtlines = []
    myMatrix = []
    token =""
    clienteMqtt = None
    ani : animation

    def __init__(self, test=False):
        if test == False:
            self.Config = configurationLedMatrix()
            self.initializeNeoPixel(self.Config.LedPin, self.Config.LedCount)

    def initializeNeoPixel(self, ledPin, LedCount):
        # Create NeoPixel object with appropriate configuration.
        self.LedStrip = neopixel.NeoPixel(ledPin,
                                          LedCount,
                                          brightness=1.0,
                                          auto_write=False,
                                          pixel_order=neopixel.GRB)

        self.initLeds(self.LedStrip)

    def initializeNeoPixelMQTT(self, port, host, token):
        self.host = host
        self.port = port
        self.token = token

        self.clienteMqtt = paho.mqtt.client.Client( )
        self.clienteMqtt.on_publish = on_publish
        #self.clienteMqtt.on_connect = matrixAnimation.on_connect
        self.clienteMqtt.connect(host=host, port=int(port))
        self.clienteMqtt.loop_start()
        self.serveAnimation(self.ani, self.myMatrix)

    def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))


    def initializeImages(self):
        del self.loadIm
        del self.origIm
        del self.im
        del self.txtlines
        self.loadIm = None
        self.origIm = None
        self.im = None
        self.txtlines = []

        # Load the animation config
        self.loadAnimationConfig()

    def allonecolour(self, strip, colour):

        # Paint the entire matrix one colour
        strip.fill(colour)
        strip.show()

    def colour(self, r, g, b):
        # Fix for Neopixel RGB->GRB, also British spelling
        return self.colourTuple([g, r, b])

    def colourTuple(self, rgbTuple):
        red = rgbTuple[0]
        green = rgbTuple[1]
        blue = rgbTuple[2]
        RGBint = (red << 16) + (green << 8) + blue
        return RGBint

    def initLeds(self, strip):
        # Intialize the library (must be called once before other functions).
        # strip.begin()
        # Wake up the LEDs by briefly setting them all to white
        self.allonecolour(strip, self.colour(255, 255, 255))
        time.sleep(0.01)

    def startAnimation(self, Anim: animation, myMatrix):
        # And here we go.
        try:
            rep = Anim.Repetitions
            if Anim.Repetitions < 0:
                rep = sys.maxsize
            for i in range(rep):
                # Loop through the image widthways
                # Can't use a for loop because Python is dumb
                # and won't jump values for FLIP command
                x = 0
                # Initialise a pointer for the current line in the text file
                tx = 0

                while x < Anim.image.size[0] - Anim.width:

                    # Set the sleep period for this frame
                    # This might get changed by a textfile command
                    thissleep = Anim.Speed

                    # Set the increment for this frame
                    # Typically advance 1 pixel at a time but
                    # the FLIP command can change this
                    thisincrement = 1

                    rg = Anim.image.crop((x, 0, x + Anim.width, Anim.height))
                    dots = list(rg.getdata())

                    for i in range(len(dots)):
                        id = myMatrix[i]
                        self.LedStrip[id] = self.colourTuple(dots[i])
                        # self.strip.setPixelColor(self.Config.myMatrix[i], self.colourTuple(dots[i]))

                    self.LedStrip.show()

                    # by the moment without instructions

                    x = x + thisincrement
                    time.sleep(thissleep)

        except (KeyboardInterrupt, SystemExit):
            print("Stopped")
            self.allonecolour(self.LedStrip, self.colour(0, 0, 0))

    def serveAnimation(self, Anim: animation, myMatrix):
        # And here we go.
        try:
            rep = Anim.Repetitions
            if Anim.Repetitions < 0:
                rep = sys.maxsize
            for i in range(rep):
                # Loop through the image widthways
                # Can't use a for loop because Python is dumb
                # and won't jump values for FLIP command
                x = 0
                # Initialise a pointer for the current line in the text file
                tx = 0

                while x < Anim.image.size[0] - Anim.width:

                    # Set the sleep period for this frame
                    # This might get changed by a textfile command
                    thissleep = Anim.Speed

                    # Set the increment for this frame
                    # Typically advance 1 pixel at a time but
                    # the FLIP command can change this
                    thisincrement = 1

                    rg = Anim.image.crop((x, 0, x + Anim.width, Anim.height))
                    dots = list(rg.getdata())

                    led = SimpleMessage();
                    imax = len(dots) - 1
                    for i in range(imax):
                        id = myMatrix[i]
                        led.Pin = id
                        led.RGBint= self.colourTuple(dots[i])
                        led.End=False
                        msgser = led.SerializeToString()
                        self.clienteMqtt.publish(self.token, msgser, 2, True)
                        time.sleep(0.1)

                    id = myMatrix[imax]
                    led.Pin = id
                    led.RGBint = self.colourTuple(dots[imax])
                    led.End = True
                    msgser = led.SerializeToString()
                    self.clienteMqtt.publish(self.token, msgser, 2, True)
                    time.sleep(0.1)

                    # by the moment without instructions

                    x = x + thisincrement
                    time.sleep(thissleep)

        except (KeyboardInterrupt, SystemExit):
            print("Stopped")
            self.allonecolour(self.LedStrip, self.colour(0, 0, 0))

ma = matrixAnimation(True)

def main(argv):
    inputfile = ""
    host = ""
    port = ""
    token= ""
    ##"{\"ImageFile\": \"prueba.png\", \"CommandFile\": \"\", \"width\": 12, \"heigth\": 8, \"Repetitions\": 5, \"Speed\": 0.1 }"
    try:
        opts, args = getopt.getopt(argv, "ahpt:", ["AnimationData=", "host=", "port=", "token="])
    except getopt.GetoptError:
        print('LedMatrixAnimation.py -a <json animation data>')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-a", "--AnimationData"):
            inputfile = arg
        elif opt in ("-h", "--host"):
            host = arg
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-t", "--token"):
            token = arg


    ani = animation(inputfile)
    myMatrix = calculateMatrix(ani.height, ani.width)


    
    if(host != ""):
        ma.ani = ani
        ma.myMatrix = myMatrix
        ma.initializeNeoPixelMQTT(port, host, token)
        #ma.serveAnimation( ani,myMatrix)
    else:
        import neopixel  # See https://learn.adafruit.com/neopixels-on-raspberry-pi/software
        import board
        ma.initializeNeoPixel(board.D18, len(myMatrix))
       # ma.startAnimation(ani, myMatrix)


def initializeNeoPixelMQTT(p, h):
    client = paho.mqtt.client.Client()
    client.on_message = on_publish
    client.connect(host=h, port=int(p))

def on_publish(client, userdata, mid):
    print('------------------------------')
    print('userdata: %s' % userdata)
    print('client_id: %s' % client._client_id)


if __name__ == "__main__":
    main(sys.argv[1:])

