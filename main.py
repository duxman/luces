import Queue
import threading
import os
import config
import time
from Util import PinManager
from Util.AudioProcessing import AudioProcessing
from Util.PinManager import PinManager
from Util.StopableThreadConsumer import StopableConsumerThread
from Util.logger import clienteLog
from server import WebServer





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
        #filename = "c://music/sample2.wav"
        #  sys.argv[1]
        self.MusicManager = AudioProcessing(FileName = filename)

        if os.name != 'poxis':
            self.MusicManager.setFfmpegPath(self.Config.RutaFFMPEG)

        filename = self.MusicManager.ConvertWavFile(filename)

        producer = threading.Thread( target=self.MusicManager.PlayWavFile(queue=self.WorkingQueue,FileName=filename, NumeroPines=len( self.PinList.split(',') )), name="MusicManagerThread" )
        producer.start()
        self.WorkingQueue.join()
        self.ConsumerThread.stop(timeout=0.3)
        self.Logger.info("Fin Del Proceso")
        self.Logger.info("Borramos fichero : " +  filename)

    def secuenceManager(self, StringSecuencia, time):
        vSecuenciatmp = StringSecuencia.split(",")
        producer = threading.Thread( target=self.executeSecuence(queue=self.WorkingQueue, vSecuencia=vSecuenciatmp, tiempo=time ), name="SecuenceManagerThread" )
        producer.start()
        self.WorkingQueue.join()
        self.ConsumerThread.stop(timeout=0.3)

    def reloadConfig(self):
        ## volvemos a cargar la configuracion de la programacion por si se ha cambiado mientras ejecutabamos
        self.Logger.info("Recargamos Programacion por si ha cambiado ")
        self.Config.Programacion = None
        self.Config.Programacion = config.programacion()

    def executeSecuence(self, queue, vSecuencia,tiempo):
        for secval in vSecuencia:
            queue.put(int(secval))
            threading._sleep(float(tiempo))




    def CreateServer(self, DefaultPort):
        self.ConfigServer = WebServer(DefaultPort)
        self.ConfigServer.StartServer()


    def execute(self, Tiempo):
        i = int(self.Config.Programacion.Repeticiones)
        ## ejecutamos siempre en un bucle infinito
        while( True ):
            ##Comprobamos la hora
            desde = self.Config.Programacion.HoraDesde
            hasta = self.Config.Programacion.HoraHasta

            ahora = time.strftime("%H:%M")
            ## representacion de fecha y hora
            self.Logger.info("Fecha y hora " + time.strftime("%c"))
            self.Logger.info("Configuracion de " + desde + " hasta " + hasta)

            ## si tenemos que ejecutar
            if ((ahora >= desde) & (ahora < hasta)):
                ##Comprobamos la repeticiones
                while ( i != 0):
                    ##comprobamos la hora por si tenemos que salir del bucle
                    ##Asumimos que el tiempo siempre va hacia delante
                    if ( (ahora > hasta) ):
                        break

                    if( i > 0):
                        self.Logger.info("Repeticiones que faltan = " + str(i))
                    else:
                        self.Logger.info("Repeticiones infinitas")

                    i = i - 1
                    ##Obtenemos la lista de pines a usar
                    PinListTemp = self.PinList

                    ##Ejecutamos cada uno de los programas
                    for p in self.Config.Programacion.Secuencia:
                        self.Logger.info("ejecutamos programa : " + p.nombre)
                        self.PinList = p.pines
                        self.pinManager( PinList = p.pines )

                        ##Comprobamos is es musica o secuencia
                        if( p.type == "MUSIC" ):
                            self.musicManager(filename = p.musica )
                        if (p.type == "SEC"):
                            self.secuenceManager(p.secuencia,p.intervalo)

                        ## dormimos el tiempo estipulado
                        threading._sleep( float(p.intervalo) )
                        self.Logger.info("fin ejecutamos programa : " + p.nombre)

                        ##  Establecemos los pines generales
                        self.Logger.info("Fin de ejecucion")
                        self.PinList = PinListTemp
                    self.reloadConfig()
            else :
                ##Como no es la hora dormimos 60 seg
                i = int(self.Config.Programacion.Repeticiones)
                self.Logger.info( "No es la hora" )
                self.Logger.info( "Configuracion de " + desde + " hasta " + hasta )

            self.reloadConfig()
            threading._sleep(Tiempo)






    def __init__(self):
        cliente = clienteLog()
        self.Logger = cliente.InicializaLog()
        self.Logger.info("--------------------<<  INI  >>--------------------")
        self.Logger.info("Arrancamos la ejecucion")
        DefaultPort = 8000
        if os.path.isfile('./config/configuracion.json'):
            """Leemos la configuracion general"""
            self.Config = config.GeneralConfiguration()

            """ Asignamos los pines configurados """
            self.PinList = self.Config.Pines
            self.Logger.info("Configuracion Cargada")

            self.Logger.info("Creamos Cola de procesamiento")
            self.WorkingQueue = Queue.Queue()
            DefaultPort = int(self.Config.WebServerPort)

        self.CreateServer(DefaultPort)

        if( self.Config != None ):
            self.execute(10)
            self.ConfigServer.StopServer()


if __name__ == "__main__":
    mainprogram = DuxmanLights()
    mainprogram.Logger.info("Fin Programa")

