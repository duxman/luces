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

import time, sys
import paho.mqtt.client as mqtt
from Util.ledStripMessage import ledLevel

MAX_PACKET = 1024


class ServeLedStripAnimation():
    Logger = None
    token = ""
    clienteMqtt: mqtt.Client = None


    def __init__(self, test=False):
        self.clienteMqtt = mqtt.Client("LedStripServe", True)

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

    def publish(self,id):
        led = ledLevel()
        my_list = id.split(",")
        for l in my_list:
            led.Level = int(l)
            self.clienteMqtt.publish(self.token, led.SerializeToString(), 2, False)



def main(argv):
    host = ""
    port = ""
    token = ""
    try:
        opts, args = getopt.getopt(argv, "hpt:", ["host=", "port=", "token="])
    except getopt.GetoptError:
        print('LedStripAnimation.py -h <host> -p<port> -t<token>')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--host"):
            host = arg
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-t", "--token"):
            token = arg

    if (host != ""):
        ma = ServeLedStripAnimation(True)
        ma.initializeMQTT(host, int(port), token)
        salir=0
        while( salir == 0):
            try:
                print("Dime 1, 2 ,3")
                id=input();
                ma.publish(id)
            except (KeyboardInterrupt, SystemExit):
                salir=1
            print("Stopped")


if __name__ == "__main__":
    main(sys.argv[1:])
