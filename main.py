#
# Copyright (c) 2020-2037 duxman.
#
# This file is part of Duxman Luces 
# (see https://github.com/duxman/luces).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import queue
import threading
import os

from paho import mqtt

import config
import time
import subprocess
from Util.logger import clienteLog


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

    def CheckTime(self):
        # Comprobamos la hora
        desde = self.Config.Programacion.HoraDesde
        hasta = self.Config.Programacion.HoraHasta

        ahora = time.strftime("%H:%M")
        # representacion de fecha y hora
        self.Logger.info("Date Time" + time.strftime("%c"))
        self.Logger.info("Configuration from " + desde + " to " + hasta)
        self.Logger.info("Configuration Status " + self.Config.Programacion.Estado)

        return_value = False

        if self.Config.Programacion.Estado == "ON":
            return_value = True
        elif self.Config.Programacion.Estado == "OFF":
            return_value = False
        else:
            if ((ahora >= desde) & (ahora < hasta)):
                return_value = True

        return return_value


    def MainLoop(self, repeatNumber):
        while (repeatNumber != 0):
            # comprobamos la hora por si tenemos que salir del bucle
            # Asumimos que el tiempo siempre va hacia delante
            if self.CheckTime() == False:
                break

            if repeatNumber > 0:
                self.Logger.info("Remaining repeats = " + str(repeatNumber))
            else:
                self.Logger.debug("Infinite loops")

            repeatNumber = repeatNumber - 1

            # Ejecutamos cada uno de los programas

            self.Logger.debug("Execute program: " + self.Config.ProgramConfiguration.ProgramName)

            # Comprobamos is es musica o secuencia
            if self.Config.ProgramConfiguration.ProgramType == "MUSIC":
                for MusicFile in self.Config.ProgramConfiguration.MusicFiles:
                    self.executeCommandMusic(self.Config.RutaMusica+"/"+MusicFile)
                    self.reloadConfig()

            if self.Config.ProgramConfiguration.ProgramType == "SEQ":
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
        while True:

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
            time.sleep(self.Config.Programacion.WaitTime)

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

        if os.path.isdir('./web/static/config'):
            """Leemos la configuracion general"""
            self.Config = config.GeneralConfiguration()

            """ Asignamos los pines configurados """
            self.PinList = self.Config.Zones.OrderedPins
            self.Logger.debug("Configuracion Cargada")

            self.Logger.debug("Create Process Queue")
            self.WorkingQueue = queue.Queue()

        if (self.Config != None):
            self.MainProcess()
            # probamos comando externo


if __name__ == "__main__":
    mainprogram = DuxmanLights()
    mainprogram.Logger.info("--------------------<<  END  >>--------------------")
