import Queue
import threading
import os
import config
import time
import subprocess
from Util.logger import clienteLog
from server import WebServer


class DuxmanLights(object):
    Logger = None
    Config = None
    ConfigServer = None
    MusicManager = None
    PinManager = None
    PinList = []
    Queue = None

    def reloadConfig(self):
        # volvemos a cargar la configuracion de la programacion por si se ha cambiado mientras ejecutabamos
        self.Logger.debug("Reloads configuration files ")
        self.Config.Programacion = None
        self.Config.Programacion = config.programacion()

    def CreateServer(self, default_port=8000,internal_server=True,external_command="" ):
        self.Logger.info("--------------------<<  INI SUBPROCESO WEBSERVER  >>--------------------")
        if( internal_server == True):
            self.ConfigServer = WebServer(default_port)
            self.ConfigServer.StartServer()
        else:
            p = subprocess.Popen(external_command)

    def CheckTime(self):
        # Comprobamos la hora
        desde = self.Config.Programacion.HoraDesde
        hasta = self.Config.Programacion.HoraHasta

        ahora = time.strftime("%H:%M")
        # representacion de fecha y hora
        self.Logger.info("Date Time" + time.strftime("%c"))
        self.Logger.info("Configuration from " + desde + " to " + hasta)
        return_value = False
        if ((ahora >= desde) & (ahora < hasta)):
            return_value = True
        return return_value


    def MainLoop(self, repeatNumber):
        while (repeatNumber != 0):
            # comprobamos la hora por si tenemos que salir del bucle
            # Asumimos que el tiempo siempre va hacia delante
            if (self.CheckTime() == False):
                break

            if (repeatNumber > 0):
                self.Logger.info("Remaining repeats = " + str(repeatNumber))
            else:
                self.Logger.debug("Infinite loops")

            repeatNumber = repeatNumber - 1

            # Ejecutamos cada uno de los programas

            self.Logger.debug("Execute program: " + self.Config.ProgramConfiguration.ProgramName)

            # Comprobamos is es musica o secuencia
            if (self.Config.ProgramConfiguration.ProgramType == "MUSIC"):
                for MusicFile in self.Config.ProgramConfiguration.MusicFiles:
                    self.executeCommandMusic(self.Config.RutaMusica+"/"+MusicFile)
                    self.reloadConfig()

            if (self.Config.ProgramConfiguration.ProgramType == "SEQ"):
                for Seq in self.Config.ProgramConfiguration.Sequences:
                    self.executeCommandSequence(Seq.replace(" ", ""), self.Config.ProgramConfiguration.ProgramInterval)
                    self.reloadConfig()

            # dormimos el tiempo estipulado
            threading._sleep(float(self.Config.ProgramConfiguration.ProgramInterval))
            self.Logger.debug("End Execution of : " + self.Config.ProgramConfiguration.ProgramName)
        else:
            self.Logger.debug("End of repeats")
        # End While
        self.Logger.debug("End of MainLoop")

    def MainProcess(self):
        repeatNumber = int(self.Config.Programacion.Repeticiones)
        # ejecutamos siempre en un bucle infinito
        while (True):

            # Comprobamos la hora
            if (self.CheckTime() == True):
                self.MainLoop(repeatNumber)
            else:
                # Como no es la hora dormimos 60 seg
                repeatNumber = int(self.Config.Programacion.Repeticiones)
                self.Logger.debug("it is not the Time")
            # END if( self.CheckTime()== True ):
            self.reloadConfig()
            self.Logger.debug("Wait " + str(self.Config.Programacion.WaitTime) + "sec")
            threading._sleep(self.Config.Programacion.WaitTime)

        # END while (True):
        self.Logger.debug("End MainProcess")

    def executeCommandMusic(self, filename):
        self.Logger.info("--------------------<<  INI SUBPROCESO  >>--------------------")
        p = subprocess.Popen("python PlayMusic.py -i " + filename)
        p.wait()
        self.Logger.info("--------------------<<  FIN SUBPROCESO  >>--------------------")

    def executeCommandSequence(self, filename,waittime):
        self.Logger.info("--------------------<<  INI SUBPROCESO  >>--------------------")
        p = subprocess.Popen("python PlaySequence.py -i " + filename + " -w " + str(waittime))
        p.wait()
        self.Logger.info("--------------------<<  FIN SUBPROCESO  >>--------------------")

    def __init__(self):
        cliente = clienteLog()
        self.Logger = cliente.InicializaLog()
        self.Logger.info("--------------------<<  INI  >>--------------------")
        self.Logger.debug("Start of Program")
        DefaultPort = 8000

        if os.path.isfile('./config/configuracion.json'):
            """Leemos la configuracion general"""
            self.Config = config.GeneralConfiguration()

            """ Asignamos los pines configurados """
            self.PinList = self.Config.Pines
            self.Logger.debug("Configuracion Cargada")

            self.Logger.debug("Create Process Queue")
            self.WorkingQueue = Queue.Queue()
            DefaultPort = int(self.Config.WebServerPort)

            self.CreateServer( default_port=DefaultPort,internal_server=self.Config.UseInternalWebServer,external_command=self.Config.ExternalWebServerCommand )
        else:
            self.CreateServer(default_port=DefaultPort)

        if (self.Config != None):
            self.MainProcess()
            # probamos comando externo
            #self.executeCommandMusic()
            self.ConfigServer.StopServer()


if __name__ == "__main__":
    mainprogram = DuxmanLights()
    mainprogram.Logger.info("--------------------<<  END  >>--------------------")
