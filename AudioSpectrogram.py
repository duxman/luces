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
import wave
import audioop
import uuid

import os
from pydub import AudioSegment
from sklearn.preprocessing import scale, minmax_scale
from pylab import *

import numpy as np
import pyaudio


chunk = 1024
AudioSegment.converter = "d://dev/ffmpeg/bin/ffmpeg.exe"
class parameters(object):
    pass

class wavesincronize(object):
    def PlayWavFile(self,speech,**attrs):
        e = parameters()
        for k, v in attrs.iteritems():
            setattr(e, k, v)
        ValorVector = getattr(e,"vector", [])
        ValorTiempo = getattr(e,"tiempo", 250)

        if ValorVector.__len__() >=0:
            with contextlib.closing(wave.open(speech, 'rb')) as f:
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
                    print ''.ljust(valor*2,"#")
                    stream.write(data)
                    data = f.readframes(rate+1)

                stream.stop_stream()
                stream.close()
                p.terminate()


    def AnalizeWavFile(self,speech, **attrs):
        e = parameters()
        for k, v in attrs.iteritems():
            setattr(e,k,v)

        ValorMinimo =   getattr(e,"min",0)
        ValorMaximo =   getattr(e,"max",10)
        ValorTiempo =   getattr(e,"tiempo", 250)
        extension   =   getattr(e,"format","WAV")
        if extension == ".MP3":
            sound = AudioSegment.from_mp3(speech)
            fdestino = "music/temp/"+str( uuid.uuid4())+".wav"
            sound.export(fdestino , format="wav")
            speech = fdestino

        with contextlib.closing(wave.open(speech, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            every = ( rate / ValorTiempo )

            sound_info = f.readframes(-1)
            sound_info = np.absolute( np.fromstring(sound_info[::1], 'Int16'))[::every]
            sound_infosample = [round(x) for x in np.absolute( minmax_scale(sound_info,(ValorMinimo,ValorMaximo), axis=0,  copy=True) ) ]
            print 'Normal [%s]' % ', '.join(map(str, sound_infosample))
            return sound_infosample, speech


fil = "music/SoundHelix.mp3"#sys.argv[1]
o = wavesincronize()
extension = os.path.splitext(fil)[1].upper()

sound_infosample, fdestino = o.AnalizeWavFile(fil,tiempo=250,max=20, format=extension)

o.PlayWavFile(fdestino, tiempo=250, vector=sound_infosample)