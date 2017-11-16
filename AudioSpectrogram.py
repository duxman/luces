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
import sys


from sklearn.preprocessing import scale, minmax_scale
from pylab import *
import wave
import numpy as np
import pyaudio

chunk = 1024


def playsound(speech,tiempo,vector):
    with contextlib.closing(wave.open(speech, 'rb')) as f:
        filedata = wave.open(speech, 'r')
        frames = filedata.getnframes()
        rate = filedata.getframerate()
        every = (rate / tiempo)/2

        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                        channels=f.getnchannels(),
                        rate=f.getframerate(),
                        output=True)

        data = f.readframes(every+1)
        sound_info = filedata.readframes(every+1)
        arraya=[]
        i = 0
        while data and i < vector.__len__():

            """
            sound_info = np.absolute(np.fromstring(sound_info, 'Int16'))
            sound_infosample = [round(x) for x in np.absolute(minmax_scale(sound_info, (1, 10), axis=0, copy=True))]
            #print 'Normal [%s]' % ', '.join(map(str, sound_infosample))
            valor = int(round( np.average(sound_infosample) ))
            """
            valor = int(vector[i])
            arraya.append(valor)
            i = i +1

            print ''.ljust(valor,'#')
            stream.write(data)
            data = f.readframes(every+1)
            #sound_info = filedata.readframes(every + 1)
            # stop stream

        subplot(212)
        plot(arraya)
        show()
        filedata.close()
        stream.stop_stream()
        stream.close()
        p.terminate()


def show_wave_n_spec(speech, tiempo):
    with contextlib.closing(wave.open(speech, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        every = ( rate / tiempo )

        sound_info = f.readframes(-1)
        sound_info = np.absolute( np.fromstring(sound_info[::1], 'Int16'))[::every]
        sound_infosample = [round(x) for x in np.absolute( minmax_scale(sound_info,(1,10), axis=0,  copy=True) ) ]
        print 'Normal [%s]' % ', '.join(map(str, sound_infosample))




        subplot(211)
        plot(sound_info)

        subplot(212)
        plot(sound_infosample)
        show()

        return sound_infosample

fil = "music/sample2.wav"#sys.argv[1]
sound_infosample = show_wave_n_spec(fil,250)
playsound(fil, 250, sound_infosample)