import ssl
import sys
from time import sleep

import paho.mqtt.client
from esp8266luces.esp82666luces.SimpleMessage import SimpleMessage
import random


def on_connect(client, userdata, flags, rc):
    print('connected (%s)' % client._client_id)
    client.subscribe(topic='inTopic', qos=2)
    simplem = SimpleMessage()
    for i in range(20):
        simplem.Pin = i
        simplem.RGBint = random.randint(255, 5000)
        simplem.End = (i % 2 == 1)
        mesgserializado = simplem.SerializeToString()
        client.publish('inTopic', payload=mesgserializado, qos=2, retain=False)

def send(client):
    simplem = SimpleMessage()
    for i in range(20):
        simplem.Pin = i
        simplem.RGBint = random.randint(255,5000)
        simplem.End = (i % 2 == 1)
        mesgserializado = simplem.SerializeToString()
        client.publish('inTopic', payload=mesgserializado, qos=2, retain=False)


def on_message(client, userdata, message):
    print('------------------------------')
    print('topic: %s' % message.topic)
    print('payload: %s' % message.payload)
    print('qos: %d' % message.qos)
    s = SimpleMessage();
    s.ParseFromString(message.payload)
    print (s)



def main():
    client = paho.mqtt.client.Client(client_id='albert-subs', clean_session=False)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host='192.168.1.196', port=1883)
    client.loop_forever()


if __name__ == '__main__':
    main()

sys.exit(0)