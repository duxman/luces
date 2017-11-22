import contextlib
import uuid
import wave
import audioop
import os
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
    def __int__(self,FileName=None):
        self.SongName = FileName
        self.ConvertWavFile(FileName)
        self.GetMaxRate(self.WaveFile)
        if os.name == 'posix':
            self.Device = alsaaudio.PCM()
        else:
            self.Device = pyaudio.PyAudio()

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
        else:
            AudioDevice.open(format=AudioDevice.get_format_from_width(WaveAudio.getsampwidth()),
                             channels=WaveAudio.getnchannels(),
                             rate=WaveAudio.getframerate(),
                             output=True)

    def ConvertWavFile(self,FileName):
        extension   =  os.path.splitext(FileName)[1].upper()
        self.WaveFile = FileName
        if extension == ".MP3":
            sound = AudioSegment.from_mp3( FileName )
            self.WaveFile = "music/temp/"+str( uuid.uuid4())+".wav"
            sound.export(self.WaveFile , format="wav")
        return self.WaveFile

    def GetMaxRate(self, FileName):
        with contextlib.closing(wave.open(FileName, 'rb')) as f:
            self.PeriodSize = f.getframerate() / 8
            array = []
            data = f.readframes(self.PeriodSize)
            while data:
                valor = int( audioop.rms )
                array.push( valor )
                data = f.readframes(self.PeriodSize)
            self.MaxRate = audioop.max(array, 2)
        return self.MaxRate, self.PeriodSize


    def PlayWavFile(self, queue, FileName = None):
        self.QueueProcess = queue

        if FileName == None:
            FileName = self.WaveFile

        with contextlib.closing(wave.open(FileName, 'rb')) as WaveAudio:
            self.prepareDevice(self.Device, WaveAudio)
            data = WaveAudio.readframes(self.PeriodSize)
            while data:
                valor = int(round( audioop.rms(data, 2) * 5 / self.MaxRate ))
                self.QueueProcess.put( valor )
                self.Device.write(data)
                data = WaveAudio.readframes(self.PeriodSize)
            self.QueueProcess.join()