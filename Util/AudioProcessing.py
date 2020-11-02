import contextlib
import uuid
import wave
import numpy
import math
import os
import time
import paho.mqtt.client as mqtt
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

        self.GetMaxRate(FileName)

    def initializeMQTT(self, host, port):
        self.clienteMqtt.on_connect = self.on_connect
        self.clienteMqtt.on_publish = self.on_publish
        self.clienteMqtt.connect(host, port, 15)
        self.clienteMqtt.loop_start()

    def on_connect(self, mqttc, obj, flags, rc):
        self.Logger.debug("Conectados a MQTT " + str(rc))

    def on_publish(self, mqttc, obj, mid):
        self.Logger.debug("Messagge sended " + str(mid))

    def publish(self, id):
        led = ledLevel()
        led.Level = id
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

    def GetMaxRate(self, FileName):
        with contextlib.closing(wave.open(FileName, 'rb')) as f:
            self.PeriodSize = int((f.getframerate() / 8))
            array = []
            data = f.readframes(self.PeriodSize)
            while data:
                #valor = int( audioop.rms( data,2) )
                data = numpy.fromstring(data, 'Int16')                
                valor = numpy.median( numpy.absolute(data))
                array.append( valor )
                data = f.readframes(self.PeriodSize)
            self.MaxRate = numpy.max( array )
        return self.MaxRate, self.PeriodSize

    def getQueueValue(self, ValorMax, ValorMedio, NumeroPines ):
        ValorIntermedio = (ValorMedio * NumeroPines) / ValorMax
        ValorNormalizado = int(abs(math.ceil(ValorIntermedio)))
        self.publish(ValorNormalizado)
        value='->#'
        #self.Logger.info(f".ljust(ValorNormalizado, '#'))
        #Antes se procesaba con queue ahora com mqtt
        #self.QueueProcess.put(ValorNormalizado)

    def PlayWavFile(self, FileName = None, NumeroPines=0):

        if FileName == None:
            FileName = self.WaveFile

        with contextlib.closing(wave.open(FileName, 'rb')) as WaveAudio:
            self.prepareDevice(self.Device, WaveAudio)
            data = WaveAudio.readframes(self.PeriodSize)
            while data:
                data1 = numpy.fromstring(data, 'Int16')

                valormedio = numpy.median(numpy.absolute(data1))
                self.getQueueValue( self.MaxRate, valormedio, NumeroPines)

                self.WriteFunctionObject.write(data)
                time.sleep(0.0125)
                data = WaveAudio.readframes(self.PeriodSize)

            if os.name != 'poxis':
                self.Stream.stop_stream()
                self.Stream.close()
                self.Device.terminate()


            #self.QueueProcess.join()

