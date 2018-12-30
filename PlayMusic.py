import sys
import getopt
import threading
import Queue
from config import Zones
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
        self.Filename = filename
        self.Zones = Zones()
        self.Logger.debug("Create Process Queue")
        self.WorkingQueue = Queue.Queue()

    def pinManagerProcess(self):
        pinmanager = PinManager.PinControl(self.Logger, self.Zones)
        self.ConsumerThread = StopableConsumerThread(queue=self.WorkingQueue, target=pinmanager.EncenderInRangeZone, name="PinManagerConsumerThread", sleep=0)
        self.ConsumerThread.start()

    def PlayFile(self):
        self.Logger.info("Iniciamos reproduccion de fichero " + self.Filename)

        self.pinManagerProcess()

        self.MusicManager = AudioProcessing(FileName=self.Filename)

        producer = threading.Thread(target=self.MusicManager.PlayWavFile(queue=self.WorkingQueue, FileName=self.Filename, NumeroPines=len(self.Zones.DefinedZones)), name="MusicManagerThread")
        producer.start()
        self.WorkingQueue.join()
        self.ConsumerThread.stop(timeout=0.3)
        self.Logger.info("End of the process")


def main(argv):
    inputfile = ""
    zones = []

    try:
        opts, args = getopt.getopt(argv, "hi:z:", ["ifile=", "zones="])
    except getopt.GetoptError:
        print 'PlayMusic.py -i <inputfile> -z <ZonesArray>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'PlayMusic.py -i <inputfile> -z <ZonesArray>'
            sys.exit()

        elif opt in ("-i", "--ifile"):
            inputfile = arg

    playfile = PlayMusic(inputfile, zones)
    playfile.Logger.info("--------------------<<  INI PLAY SCRIPT >>--------------------")
    playfile.PlayFile()
    playfile.Logger.info("--------------------<<  END PLAY SCRIPT >>--------------------")


if __name__ == "__main__":
    main(sys.argv[1:])
