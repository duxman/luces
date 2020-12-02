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
import sys
import getopt
import threading
import queue
import os

from paho import mqtt

from Util.ledStripMessage import ledLevel
from config import Zones, GeneralConfiguration
from Util import Mp3ToWav, PinManager
#from Util import PinManager
from Util.AudioProcessing import AudioProcessing
#from Util.StopableThreadConsumer import StopableConsumerThread
from Util.logger import clienteLog


class PlayMusic(object):
    Filename = ""
    ZonesConfig: Zones = None
    GeneralConfig: GeneralConfiguration = None
    Logger = None
    ConsumerThread = None
    MusicManager = None
    WorkingQueue = None
    Tokens = []

    pinManager =[]

    def __init__(self, filename, zones):
        cliente = clienteLog()
        self.Logger = cliente.InicializaLog(filename="./log/PlayMusic.log")
        self.Filename = self.CheckFileType(filename)
        self.ZonesConfig = Zones()
        self.GeneralConfig = GeneralConfiguration()
        self.Logger.debug("Create Process Queue")
        self.WorkingQueue = queue.Queue()
        self.pinManager  = PinManager.PinControl( cliente, self.ZonesConfig ,self.GeneralConfig.MQTT_HOST,self.GeneralConfig.MQTT_PORT )

    # def pinManagerProcess(self):
    #     if self.ZonesConfig.ZonePinType == "REMOTE":
    #         pinmanager = PinManager.PinControl(self.Logger, self.ZonesConfig, self.GeneralConfig.MQTT_HOST,
    #                                            self.GeneralConfig.MQTT_PORT, self.ZonesConfig.MQTT_TOKEN)
    #         self.ConsumerThread = StopableConsumerThread(queue=self.WorkingQueue, target=pinmanager.publish,
    #                                                      name="PinManagerConsumerThread", sleep=0)
    #     else:
    #         pinmanager = PinManager.PinControl(self.Logger, self.ZonesConfig)
    #         self.ConsumerThread = StopableConsumerThread(queue=self.WorkingQueue, target=pinmanager.EncenderInRangeZone,
    #                                                      name="PinManagerConsumerThread", sleep=0)
    #     self.ConsumerThread.start()

    def PlayFile(self):
        self.Logger.info("Iniciamos reproduccion de fichero " + self.Filename)

        # producer = threading.Thread(
        #     target=self.MusicManager.PlayWavFile(queue=self.WorkingQueue, FileName=self.Filename,
        #                                          NumeroPines=len(self.ZonesConfig.SpectrumPins)),
        #     name="MusicManagerThread")

        #######################################################
        # El productor gestionara los mensajes a MQTT
        #######################################################
        # Pasamos los parametros de host y port de MQTT al productor


        self.MusicManager = AudioProcessing(FileName=self.Filename, Host=self.GeneralConfig.MQTT_HOST,
                                            Port=self.GeneralConfig.MQTT_PORT,
                                            Tokens=self.ZonesConfig.Tokens)
        producer = threading.Thread(target=self.MusicManager.PlayWavFile(FileName=self.Filename, NumeroPines=len(self.ZonesConfig.SpectrumPins)), name="MusicManagerThread")
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
        if (file_extension == ".MP3"):
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
