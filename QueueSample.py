import contextlib
import uuid
import wave
import audioop

import os

from pydub import AudioSegment

import PinManager
#import pyaudio
import alsaaudio
import threading
import Queue
from datetime import datetime

class parameters(object):
    pass

class Consumer(threading.Thread):
    ConsumerQueue = None
    def __init__(self, queue, **attrs):
        self.ConsumerQueue = queue
        e = parameters()

        for k, v in attrs.iteritems():
            setattr(e, k, v)
        self.Target = getattr(e, "target", None)
        self.Name = getattr(e, "name", 'DefaultConsumer')
        self.SleepPeriod = getattr(e, "sleep", 0)

        """ constructor, setting initial variables """
        self._stopevent = threading.Event( )
        self._sleepperiod = self.SleepPeriod

        threading.Thread.__init__(self, name=self.Name)

    def stop(self, timeout=None):
        """ Stop the thread and wait for it to end. """
        self._stopevent.set( )
        threading.Thread.join(self, timeout)


    def isRunning(self):
        return not self._stopevent.isSet( )

    def run(self):
        print "%s starts" % (self.getName(),)
        count = 0
        while self.isRunning():
            try:
                valor = self.ConsumerQueue.get( False, self._sleepperiod)
                count += 1
                if self.Target == None:
                    print "Loop %d Valor %s" % (count, valor,)
                else:
                    self.Target(valor)

                if(self._sleepperiod > 0):
                    self._stopevent.wait(self._sleepperiod)
                self.ConsumerQueue.task_done()

            except Queue.Empty as e:
                pass
                #print "Empty...  " + e.message

        print "%s ends" % (self.getName(),)

def prepareDevice(device, f):
    # Set attributes
    device.setchannels(f.getnchannels())
    device.setrate(f.getframerate())

    # 8bit is unsigned in wav files
    if f.getsampwidth() == 1:
        device.setformat(alsaaudio.PCM_FORMAT_U8)
    # Otherwise we assume signed data, little endian
    elif f.getsampwidth() == 2:
        device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    elif f.getsampwidth() == 3:
        device.setformat(alsaaudio.PCM_FORMAT_S24_3LE)
    elif f.getsampwidth() == 4:
        device.setformat(alsaaudio.PCM_FORMAT_S32_LE)
    else:
        raise ValueError('Unsupported format')

    periodsize = f.getframerate() / 8
    device.setperiodsize(periodsize)

def ConvertWavFile(FileName):
    extension   =  os.path.splitext(FileName)[1].upper()
    WaveFile = FileName
    if extension == ".MP3":
        sound = AudioSegment.from_mp3( FileName )
        WaveFile = "music/temp/"+str( uuid.uuid4())+".wav"
        sound.export(WaveFile , format="wav")
    return WaveFile


def PlayWavFile(FileName, **attrs):
    ConvertWavFile(FileName)
    e = parameters()
    for k, v in attrs.iteritems():
        setattr(e, k, v)
    ValorQueue = getattr(e, "queue", None )
    with contextlib.closing(wave.open(FileName, 'rb')) as analizer:
        periodsize = analizer.getframerate() / 8
        max = audioop.rms( analizer.readframes( -1 ) , 2)

    with contextlib.closing(wave.open(FileName, 'rb')) as f:
        device = alsaaudio.PCM()
        prepareDevice(device, f)

        data = f.readframes(periodsize)

        i = 0
        while data:
            valor = int(round( audioop.rms(data, 2) * 5 / max ))
            ValorQueue.put( valor )
            device.write(data)
            data = f.readframes(periodsize)

        ValorQueue.join()

class targetclass():

    def printfunction(self, valor):
        array = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        arr = array[:valor]
        #print "Target value %s" % (valor,)
        print(arr)

if __name__ == "__main__":
    q = Queue.Queue()
    pinman = PinManager.PinManager(None,[2,3,4,17,27,22,10,9,11,5])
    testthread = Consumer( q,target =pinman.EncenderInRange, name="MiConsumidor" )
    testthread.start( )

    producer = threading.Thread(target=PlayWavFile("music/sample3.wav",queue=q))
    producer.start()
    q.join()
    #producer.join()

    print "fin"
    testthread.stop(timeout=0.3 )
    print "finStop"

    print str ( producer.is_alive() )

