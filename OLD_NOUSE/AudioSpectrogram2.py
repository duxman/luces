
import contextlib
import threading
import uuid

import os
from pydub import AudioSegment
import wave
import pyaudio
import Queue
import audioop


AudioSegment.converter = "C://DATOS/PRUEBAS/DuxmanLigths/www/tool/ffmpeg/bin/ffmpeg.exe"
class parameters(object):
    pass

class EventLed(object):
    pass

class WaveSynchronize(object):
    Logger = None
    callbacks = None
    SongFile = None
    WaveFile = None
    SoundInfoSample = None
    QueueObject = None

    def __init__(self, Logger, Song, q):
        self.Logger = Logger
        self.QueueObject = q
        self.SongFile = Song

    def ExecuteWav(self):
        self.ConvertToWavFile( self.SongFile )
        self.PlayWavFileWithQueue( self.WaveFile, self.QueueObject, tiempo = 1024, max = 9)

    def PlayWavFileWithQueue(self, FileName, Queue,**attrs):
        #self.Logger.info(" Play File")
        e = parameters()
        for k, v in attrs.iteritems():
            setattr(e, k, v)
        ValorTiempo = getattr(e,"tiempo", 250)
        ValorMax = getattr(e, "max", 10)

        if Queue is None:
            return

        with contextlib.closing(wave.open(FileName, 'rb')) as fileanalize:
            data = fileanalize.readframes(-1)
            maxValue = audioop.rms(data,2)
            maxPeakValue = audioop.max(data,2)
            interval = int( round( ( maxPeakValue  ) / maxValue ) )

        with contextlib.closing(wave.open(FileName, 'rb')) as f:
            rate = (f.getframerate() / ValorTiempo)/2
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                            channels=f.getnchannels(),
                            rate=f.getframerate(),
                            output=True)

            data = f.readframes(rate)

            i = 0
            while data:
                stream.write(data)
                valor = int(round( ( audioop.rms(data,2) * interval / maxValue ) ) )
                Queue.put( valor )
                print "."
                data = f.readframes(rate+1)

            stream.stop_stream()
            stream.close()
            p.terminate()
            Queue.join()


    def ConvertToWavFile(self, FileName):


        extension   =  os.path.splitext(FileName)[1].upper()

        if extension == ".MP3":
            sound = AudioSegment.from_mp3( self.SongFile )
            self.WaveFile = "music/temp/"+str( uuid.uuid4())+".wav"
            sound.export(self.WaveFile , format="wav")
        else:
            self.WaveFile = self.SongFile

        return self.WaveFile

class StopableConsumer( threading.Thread):
    def __init__(self):
        super(StopableConsumer, self).__init__()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

def Consume(Queue):
    t = threading.currentThread()
    while getattr(t, "do_run", True):
    #while (True):
        valor = Queue.get();
        print ''.ljust(valor, "#") + str(valor)
        Queue.task_done()
    print "Finish"


q = Queue.Queue(maxsize=3)
s = WaveSynchronize(None,"c://music/sample2.wav",q)


tc = threading.Thread(name = "ConsumerThread", target=Consume, args=(q,))
#tc.do_run = True
tc.start()

t = threading.Thread(name="ProducerThread", target=s.ExecuteWav)
t.start()
print "esperando...."
q.join()
t.join()
print "finalizado ...."
tc.do_run = False


