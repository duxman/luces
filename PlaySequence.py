import sys
import getopt
import threading
import queue
from config import Zones, GeneralConfiguration
from Util import PinManager
from Util.StopableThreadConsumer import StopableConsumerThread
from Util.logger import clienteLog


class PlaySequence(object):
    Filename = ""
    WaitTime = 0
    ZonesConfig: Zones = None
    GeneralConfig: GeneralConfiguration = None
    Logger = None

    ConsumerThread = None
    WorkingQueue = None

    def __init__(self, filename, waittime):
        cliente = clienteLog()
        self.Logger = cliente.InicializaLog(filename="./log/PlaySequence.log")
        self.Filename = filename
        self.WaitTime = waittime
        self.ZonesConfig = Zones()
        self.GeneralConfig = GeneralConfiguration()
        self.Logger.debug("Create Process Queue")
        self.WorkingQueue = queue.Queue()

    def pinManagerProcess(self):
        if self.ZonesConfig.ZonePinType == "REMOTE":
            pinmanager = PinManager.PinControl(self.Logger, self.ZonesConfig, self.GeneralConfig.MQTT_HOST,
                                               self.GeneralConfig.MQTT_PORT, self.ZonesConfig.MQTT_TOKEN)
            self.ConsumerThread = StopableConsumerThread(queue=self.WorkingQueue, target=pinmanager.publish,
                                                         name="PinManagerConsumerThread", sleep=0)
        else:
            pinmanager = PinManager.PinControl(self.Logger, self.ZonesConfig)
            self.ConsumerThread = StopableConsumerThread(queue=self.WorkingQueue, target=pinmanager.EncenderInRangeZone,
                                                         name="PinManagerConsumerThread", sleep=0)
        self.ConsumerThread.start()

    def executeSecuence(self, queue, vSecuencia, waittime):
        for secval in vSecuencia:
            queue.put(int(secval))
            threading._sleep(float(waittime))

    def PlayFile(self):
        self.Logger.info("Iniciamos reproduccion de secuencia " + self.Filename)
        vSecuenciatmp = self.Filename.split(",")

        self.pinManagerProcess()

        producer = threading.Thread(
            target=self.executeSecuence(queue=self.WorkingQueue, vSecuencia=vSecuenciatmp, waittime=self.WaitTime),
            name="SequenceManagerThread")
        producer.start()
        self.WorkingQueue.join()
        self.ConsumerThread.stop(timeout=0.3)

        self.Logger.info("End of the process")


def main(argv):
    inputfile = ""
    waittime = 0

    try:
        opts, args = getopt.getopt(argv, "hi:w:", ["ifile=", "waittime="])
    except getopt.GetoptError:
        print('PlayMusic.py -i <inputfile> -z <ZonesArray>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('PlayMusic.py -i <inputfile> -z <ZonesArray>')
            sys.exit()

        elif opt in ("-i", "--ifile"):
            inputfile = arg

        elif opt in ("-w", "--waittime"):
            waittime = float(arg)

    playfile = PlaySequence(inputfile, waittime)
    playfile.Logger.info("--------------------<<  INI PLAY SCRIPT >>--------------------")
    playfile.PlayFile()
    playfile.Logger.info("--------------------<<  END PLAY SCRIPT >>--------------------")


if __name__ == "__main__":
    main(sys.argv[1:])
