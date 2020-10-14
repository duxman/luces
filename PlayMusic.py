import sys
import getopt
import threading
import queue
import os
from config import Zones
from Util import Mp3ToWav
from Util import PinManager
from Util.AudioProcessing import AudioProcessing
from Util.StopableThreadConsumer import StopableConsumerThread
from Util.logger import clienteLog

class PlayMusic(object):

    Filename = ""
    Zones = None
    Logger = None

    ConsumerThread = None
    MusicManager = None
    WorkingQueue = None

    def __init__(self, filename, zones):
        cliente = clienteLog()
        self.Logger = cliente.InicializaLog(filename="./log/PlayMusic.log")
        self.Filename = self.CheckFileType( filename)
        self.Zones = Zones()
        self.Logger.debug("Create Process Queue")
        self.WorkingQueue = queue.Queue()

    def pinManagerProcess(self):
        pinmanager = PinManager.PinControl(self.Logger, self.Zones)
        self.ConsumerThread = StopableConsumerThread(queue=self.WorkingQueue, target=pinmanager.EncenderInRangeZone, name="PinManagerConsumerThread", sleep=0)
        self.ConsumerThread.start()

    def PlayFile(self):
        self.Logger.info("Iniciamos reproduccion de fichero " + self.Filename)


        self.pinManagerProcess()
        self.MusicManager = AudioProcessing(FileName=self.Filename)
        producer = threading.Thread(target=self.MusicManager.PlayWavFile(queue=self.WorkingQueue, FileName=self.Filename, NumeroPines=len(self.Zones.SpectrumPins)), name="MusicManagerThread")

        producer.start()
        self.WorkingQueue.join()
        self.ConsumerThread.stop(timeout=0.3)
        self.Logger.info("End of the process")

    def CallMp3ToWav(self, filename):
        self.Logger.info("--------------------<<  INI PROCESO  CONVERSION>>--------------------")
        conv = Mp3ToWav.conversor(filename)
        return conv.Convertir()
        self.Logger.info("--------------------<<  FIN PROCESO  CONVERSION>>--------------------")

    def CheckFileType(self, inputfile):
        filename, file_extension = os.path.splitext(inputfile)
        file_extension = file_extension.upper()
        if( file_extension == ".MP3"):
            outputfile = inputfile + ".wav"
            exists = os.path.isfile(outputfile)
            if exists:
                # retornamos el nuemro nombre
                self.Filename = outputfile
                return outputfile
            else:
                # Convertimos el fichero
                outputfile = self.CallMp3ToWav(inputfile)
                self.Filename = outputfile
                return outputfile
        else:
            self.Filename = inputfile
            return inputfile
        # End of file Extension



def main(argv):
    inputfile = ""
    zones = []

    try:
        opts, args = getopt.getopt(argv, "hi:z:", ["ifile=", "zones="])
    except getopt.GetoptError:
        print('PlayMusic.py -i <inputfile> -z <ZonesArray>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('PlayMusic.py -i <inputfile> -z <ZonesArray>')
            sys.exit()

        elif opt in ("-i", "--ifile"):
            inputfile = arg


    playfile = PlayMusic(inputfile, zones)
    playfile.Logger.info("--------------------<<  INI PLAY SCRIPT >>--------------------")
    playfile.PlayFile()
    playfile.Logger.info("--------------------<<  END PLAY SCRIPT >>--------------------")



if __name__ == "__main__":
    main(sys.argv[1:])
