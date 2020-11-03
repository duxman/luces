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
import paho.mqtt.client as mqtt
from PIL import Image  # Use apt-get install python-imaging to install this

from LedMatrixAnimation import matrixAnimation
from config import configurationLedMatrix, animation, calculateMatrix

from Util.LedPanelMessage import led, display

MAX_PACKET = 1024


class ServeAnimation():
    Logger = None
    im = None
    txtlines = []
    myMatrix = []
    token = ""
    clienteMqtt: mqtt.Client = None
    ani: animation
    _protocol = mqtt.MQTTv311

    def __init__(self, test=False):
        self.clienteMqtt = mqtt.Client("ServeAnimation", True)
        if test == False:
            self.Config = configurationLedMatrix()
            for mtx in self.Config.Matrix:
                self.initializeMQTT(mtx.MQTT_HOST, int(mtx.MQTT_PORT), mtx.MQTT_TOKEN)
                for anim in mtx.Animations:
                    self.startAnimation( anim,mtx.myMatrix)

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
        ledpanel = display()
        ledpanel.ParseFromString(msg.payload)
        for l in ledpanel.frame:
            print("Pin {}, Color {}".format(l.Pin, l.Color))

    def on_message(self, mqttc, obj, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        self.decodeMsg(msg)

    def on_publish(self, mqttc, obj, mid):
        print("mid: " + str(mid))

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
        RGBint = (green << 16) + (red << 8) + blue
        return RGBint

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

                    cont_paquete = 0
                    ledpixel = led()
                    ledpanel = display()
                    ledpanel.Ini = True

                    for i in range(len(dots)):
                        id = myMatrix[i]
                        if self.colourTuple(dots[i]) != 0:
                            if cont_paquete >= MAX_PACKET:
                                self.clienteMqtt.publish("InData", ledpanel.SerializeToString(), 2, False)
                                ledpanel = display()
                                ledpanel.Ini = False
                                cont_paquete = 0
                            ledpixel.Pin = id
                            ledpixel.Color = self.colourTuple(dots[i])
                            ledpanel.frame.append(ledpixel)
                            cont_paquete = cont_paquete + 1
                    ledpanel.Fin = True

                    self.clienteMqtt.publish("InData", ledpanel.SerializeToString(), 2, False)

                    x = x + thisincrement
                    time.sleep(thissleep)

        except (KeyboardInterrupt, SystemExit):
            print("Stopped")


def main(argv):
    inputfile = ""
    host = ""
    port = ""
    token = ""
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



    if (host != ""):
        ani = animation(inputfile)
        myMatrix = calculateMatrix(ani.height, ani.width)
        ma = ServeAnimation(True)
        ma.initializeMQTT(host, int(port), token)
        ma.startAnimation(ani, myMatrix)
    else:
        ma = ServeAnimation(False)



if __name__ == "__main__":
    main(sys.argv[1:])
