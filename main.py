import Queue
import threading
import os
from multiprocessing import Process

import thread

from Util import PinManager
from Util.AudioProcessing import AudioProcessing
from Util.PinManager import PinManager
from Util.StopableThreadConsumer import StopableConsumerThread
from Util.logger import clienteLog
from server import WebServer
import config



class  DuxmanLights(object):
    Logger = None
    Config = None
    ConfigServer = None
    MusicManager =  None
    PinManager =  None
    PinList = [2,3,4,17,27,22,10,9,11,5]
    Queue = None


    def pinManager(self, PinList = [] ):
       self.PinManager = PinManager(self.Logger, PinList)
       self.ConsumerThread = StopableConsumerThread( queue=self.WorkingQueue, target= self.PinManager.EncenderInRange,name="PinManagerConsumerThread", sleep= 0.1)
       self.ConsumerThread.start()

    def musicManager(self, filename = "" ):
        #filename = "c://music/sample2.wav"  # sys.argv[1]
        self.MusicManager = AudioProcessing(FileName = filename)

        if os.name != 'poxis':
            self.MusicManager.setFfmpegPath(self.Config.RutaFFMPEG)

        filename = self.MusicManager.ConvertWavFile(filename)

        producer = threading.Thread( target=self.MusicManager.PlayWavFile(queue=self.WorkingQueue,FileName=filename, NumeroPines=len( self.PinList )), name="MusicManagerThread" )
        producer.start()
        self.WorkingQueue.join()
        self.ConsumerThread.stop(timeout=0.3)
        self.Logger.info("Fin Del Proceso")

    def CreateServer(self):
        self.ConfigServer = WebServer(self.Config.WebServerPort)
        self.ConfigServer.StartServer()


    def execute(self):
        i = 0

        for p in self.Config.Programacion.Secuencia:
            self.Logger.info("ejecutamos programa : " + p.Nombre)
            self.pinManager( PinList = p.pines )
            self.musicManager(filename = p.musica )
            threading._sleep( p.intervalo )
            self.Logger.info("fin ejecutamos programa : " + p.Nombre)

        self.Logger.info("Fin de ejecucion")


    def __init__(self):
        cliente = clienteLog()
        self.Logger = cliente.InicializaLog()
        self.Logger.info("--------------------<<  INI  >>--------------------")
        self.Logger.info("Arrancamos la ejecucion")

        """Leemos la configuracion general"""
        self.Config = config.GeneralConfiguration()
        """ Asignamos los pines configurados """
        self.PinList = self.Config.Pines
        self.Logger.info("Configuracion Cargada")

        self.Logger.info("Creamos Cola de procesamiento")
        self.WorkingQueue = Queue.Queue()

        self.CreateServer()


        self.execute()
        self.ConfigServer.StopServer()


if __name__ == "__main__":
    mainprogram = DuxmanLights()
    mainprogram.Logger.info("Fin Programa")

