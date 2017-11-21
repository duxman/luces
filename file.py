import audioop
import contextlib
import sys
import wave
import getopt
import pyalsaaudio


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
  
def PlayWavFile2(speech, tiempo):   
  with contextlib.closing(wave.open(speech, 'rb')) as a: 
    data = a.readframes(-1)
    maxvalue = audioop.rms(data,2)             
  minmax =  " RMXMAX : " + str( maxvalue )

  print minmax

  with contextlib.closing(wave.open(speech, 'rb')) as f:  
      
      device = alsaaudio.PCM(device=0)
      prepareDevice (device, f)       
      periodsize = f.getframerate() / 8
            

      data = f.readframes( periodsize )
     
      while data:                                
          device.write(data)
          rms = audioop.rms(data,2)
          valor= int( round( rms*10/maxvalue )  )
          print ''.ljust(valor,"#") + " Valor : " + str ( valor  )+ " rms : " + str ( rms ) + minmax     
          data = f.readframes(periodsize) 

fil = "music/sample2.wav"#sys.argv[1]
PlayWavFile2( il,1024)


                