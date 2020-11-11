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
import contextlib
import struct
import uuid
import wave
import numpy
import math
import os
import time
import paho.mqtt.client as mqtt
import statistics as stats
from Util.ledStripMessage import ledLevel
from Util.logger import clienteLog

if os.name == 'posix':
    import alsaaudio
else:
    import pyaudio
from pydub import AudioSegment



class AudioProcessing():
    PeriodSize = 1024
    MaxRate = 1024
    WaveFile = None
    SongName = None
    Device  = None
    Logger = None
    clienteMqtt: mqtt.Client = None
    Tokens = []

    def __init__(self,FileName=None, Host="", Port=1883, Tokens = []):
        cliente = clienteLog()
        self.Logger = cliente.InicializaLog(filename="./log/PlayMusic.log")
        self.SongName = FileName
        self.Tokens = Tokens
        self.clienteMqtt = mqtt.Client("LedStripServe", True)
        #Inicializamos MQTT
        self.initializeMQTT(Host, Port)


        if os.name == 'posix':
            self.Device = alsaaudio.PCM()
        else:
            self.Device = pyaudio.PyAudio()

    def initializeMQTT(self, host, port):
        self.clienteMqtt.on_connect = self.on_connect
        self.clienteMqtt.on_publish = self.on_publish
        self.clienteMqtt.connect(host, port, 15)
        self.clienteMqtt.loop_start()

    def on_connect(self, mqttc, obj, flags, rc):
        self.Logger.debug("Conectados a MQTT " + str(rc))

    def on_publish(self, mqttc, obj, mid):
        self.Logger.debug("Messagge sended " + str(mid))

    def publish(self, id = -1 , rng=-1):
        led = ledLevel()
        if id!=-1:
            led.Level = id
            for t in self.Tokens:
                self.clienteMqtt.publish(t, led.SerializeToString(), 2, False)

        else:
            for idx in range(rng):
                led.Level = idx
                for t in self.Tokens:
                    self.clienteMqtt.publish(t, led.SerializeToString(), 2, False)

    def setFfmpegPath(self, path):
        AudioSegment.converter = path

    def prepareDevice(self, AudioDevice, WaveAudio):
        if os.name == 'posix':
            # Set attributes
            AudioDevice.setchannels(WaveAudio.getnchannels())
            AudioDevice.setrate(WaveAudio.getframerate())

            # 8bit is unsigned in wav files
            if WaveAudio.getsampwidth() == 1:
                AudioDevice.setformat(alsaaudio.PCM_FORMAT_U8)
            # Otherwise we assume signed data, little endian
            elif WaveAudio.getsampwidth() == 2:
                AudioDevice.setformat(alsaaudio.PCM_FORMAT_S16_LE)
            elif WaveAudio.getsampwidth() == 3:
                AudioDevice.setformat(alsaaudio.PCM_FORMAT_S24_3LE)
            elif WaveAudio.getsampwidth() == 4:
                AudioDevice.setformat(alsaaudio.PCM_FORMAT_S32_LE)
            else:
                raise ValueError('Unsupported format')

            periodsize = WaveAudio.getframerate() / 8
            AudioDevice.setperiodsize(periodsize)
            self.WriteFunctionObject = AudioDevice
        else:
            self.Stream =  AudioDevice.open(format=AudioDevice.get_format_from_width(WaveAudio.getsampwidth()),
                             channels=WaveAudio.getnchannels(),
                             rate=WaveAudio.getframerate(),
                             output=True)
            self.WriteFunctionObject = self.Stream

    def ConvertWavFile(self,FileName):
        extension   =  os.path.splitext(FileName)[1].upper()
        self.WaveFile = FileName
        if extension == ".MP3":
            sound = AudioSegment.from_mp3( FileName )
            self.WaveFile = "./music/temp/"+str( uuid.uuid4())+".wav"
            sound.export(self.WaveFile , format="wav")

        self.GetMaxRate(self.WaveFile)
        return self.WaveFile

    def GetMaxRate(self, FileName,numPines):
        self.MaxRate = 0
        with contextlib.closing(wave.open(FileName, 'rb')) as f:
            self.PeriodSize = int((f.getframerate() / 8))
            data = f.readframes(self.PeriodSize)
            while data:
                count = len(data) / 2
                data = struct.unpack("%dh" % count, data)
                valor = int(stats.median_low(numpy.absolute(data)))
                if valor > self.MaxRate:
                    self.MaxRate = int(valor);
                data = f.readframes(self.PeriodSize)

        return self.MaxRate, self.PeriodSize

    def getQueueValue(self, ValorMax, ValorMedio, NumeroPines ):
        ValorIntermedio = (ValorMedio * NumeroPines) / ValorMax
        ValorNormalizado = int(abs(math.ceil(ValorIntermedio)))
        self.publish(id=ValorNormalizado)
        print(ValorNormalizado * '*')

        #Antes se procesaba con queue ahora com mqtt
        #self.QueueProcess.put(ValorNormalizado)

    def PlayWavFile(self, FileName = None, NumeroPines=0):

        if FileName == None:
            FileName = self.WaveFile

        self.GetMaxRate(FileName,NumeroPines)

        with contextlib.closing(wave.open(FileName, 'rb')) as WaveAudio:
            self.prepareDevice(self.Device, WaveAudio)
            data = WaveAudio.readframes(self.PeriodSize)
            while data:
                data1 = numpy.fromstring(data, 'Int16')

                valormedio = int(stats.median_low(numpy.absolute(data1)))
                #valormedio = numpy.median(numpy.absolute(data1))
                self.getQueueValue( self.MaxRate, valormedio, NumeroPines)

                self.WriteFunctionObject.write(data)
                time.sleep(0.0125)
                data = WaveAudio.readframes(self.PeriodSize)

            if os.name != 'poxis':
                self.Stream.stop_stream()
                self.Stream.close()
                self.Device.terminate()


            #self.QueueProcess.join()

