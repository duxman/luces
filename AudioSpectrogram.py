"""Generate a Spectrogram image for a given WAV audio sample.

A spectrogram, or sonogram, is a visual representation of the spectrum
of frequencies in a sound.  Horizontal axis represents time, Vertical axis
represents frequency, and color represents amplitude.
"""

#from pydub import AudioSegment
#sound = AudioSegment.from_file("sample.wav", format="wav")
#peak_amplitude = sound.max

# !/usr/bin/env python
import contextlib
import uuid

import os
from pydub import AudioSegment
from sklearn.preprocessing import scale, minmax_scale
from pylab import *
import wave
import numpy as np
import pyaudio
import Queue
import audioop


chunk = 1024
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

    def __init__(self, Logger, Song, callback):
        self.Logger = Logger
        self.subscribe( callback )
        self.SongFile = Song

    def subscribe(self, callback):
        self.Logger.info( " Callback added")
        self.callbacks = callback

    def Fire(self, valor):
        self.Logger.info(" execute callback")
        self.callbacks(valor)

    def ExecuteWav(self):
        self.AnalizeWavFile(tiempo=250, min=0,max=10)
        self.PlayWavFile(tiempo=250)


    def PlayWavFileWithQueue(self, FileName, Queue,**attrs):
        self.Logger.info(" Play File")
        e = parameters()
        for k, v in attrs.iteritems():
            setattr(e, k, v)
        ValorTiempo = getattr(e,"tiempo", 250)

        if Queue is None:
            return

        with contextlib.closing(wave.open(self.WaveFile, 'rb')) as f:
            rate = (f.getframerate() / ValorTiempo)/2
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                            channels=f.getnchannels(),
                            rate=f.getframerate(),
                            output=True)

            data = f.readframes(rate+1)

            i = 0
            while data:
                Queue.put()
                ##print ''.ljust(valor*2,"#")
                stream.write(data)
                data = f.readframes(rate+1)

            stream.stop_stream()
            stream.close()
            p.terminate()

    def PlayWavFile(self,**attrs):
        self.Logger.info(" Play File")
        e = parameters()
        for k, v in attrs.iteritems():
            setattr(e, k, v)
        ValorVector = getattr(e,"vector", [])
        ValorTiempo = getattr(e,"tiempo", 250)

        if ValorVector.__len__() >=0:
            with contextlib.closing(wave.open(self.WaveFile, 'rb')) as f:
                rate = (f.getframerate() / ValorTiempo)/2
                p = pyaudio.PyAudio()
                stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                                channels=f.getnchannels(),
                                rate=f.getframerate(),
                                output=True)

                data = f.readframes(rate+1)

                i = 0
                while data and i < ValorVector.__len__():
                    valor = int(ValorVector[i])
                    i = i +1
                    self.Fire( valor )
                    ##print ''.ljust(valor*2,"#")
                    stream.write(data)
                    data = f.readframes(rate+1)

                stream.stop_stream()
                stream.close()
                p.terminate()


    def AnalizeWavFile(self, **attrs):
        e = parameters()
        for k, v in attrs.iteritems():
            setattr(e,k,v)

        ValorMinimo =   getattr(e,"min",0)
        ValorMaximo =   getattr(e,"max",10)
        ValorTiempo =   getattr(e,"tiempo", 250)

        extension   =  os.path.splitext(self.SongFile)[1].upper()

        if extension == ".MP3":
            sound = AudioSegment.from_mp3( self.SongFile )
            self.WaveFile = "music/temp/"+str( uuid.uuid4())+".wav"
            sound.export(self.WaveFile , format="wav")
        else:
            self.WaveFile = self.SongFile

        with contextlib.closing(wave.open(self.WaveFile, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            every = ( rate / ValorTiempo )

            sound_info = f.readframes(-1)
            sound_info = np.absolute( np.fromstring(sound_info[::1], 'Int16'))[::every]
            self.SoundInfoSample = [round(x) for x in np.absolute( minmax_scale(sound_info,(ValorMinimo,ValorMaximo), axis=0,  copy=True) ) ]
            print 'Normal [%s]' % ', '.join(map(str, self.SoundInfoSample))

            return self.SoundInfoSample