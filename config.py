import json
import os
from Util import logger


class programacion:
    HoraDesde = ""
    HoraHasta = ""
    Estado = ""
    Programa = ""
    Repeticiones = -1
    WaitTime = 10
    data = ""

    Secuencia = []
    Logger = None

    def __init__(self):
        self.Logger = logger.clienteLog.logger
        self.Logger.info("Cargamos configuracion programacion")

        self.data = json.load(open('./config/programacion.json'))
        self.HoraDesde = self.data["StartTime"]
        self.HoraHasta = self.data["EndTime"]
        self.Estado = self.data["State"]
        self.Repeticiones =  self.data["Repeats"]
        self.WaitTime = int(self.data["WaitTime"])


class Zone():
    ZoneName = ""
    ZonePins = []

    def __init__(self,Name, Pins):
        self.ZoneName = Name
        self.ZonePins = Pins.split(",")

class Zones():
    Logger = None
    ZoneType = ""
    DefinedZones = []

    def __init__(self):
        self.Logger = logger.clienteLog.logger
        self.Logger.info("Cargamos configuracion Zones.json ")

        self.data = json.load(open('./config/Zones.json'))

        self.ZoneType = self.data["ZoneType"]
        for definedzone in self.data["Zones"]:
            ZoneTemp = Zone( definedzone["ZoneName"],definedzone["ZonePins"] )
            self.DefinedZones.append( ZoneTemp )


class ProgramConfiguration():
    Logger = None
    ProgramName = ""
    ProgramType = ""
    ProgramInterval = 0.0
    MusicFiles = []
    Sequences = []

    def __init__(self):
        self.Logger = logger.clienteLog.logger
        self.Logger.info("Cargamos configuracion ProgramConfiguration.json ")

        self.data = json.load(open('./config/ProgramConfiguration.json'))

        self.ProgramName = self.data["ProgramName"]
        self.ProgramType = self.data["ProgramType"]
        self.ProgramInterval = float( self.data["ProgramInterval"] )
        for fichero in self.data["MusicFiles"]:
            self.MusicFiles.append(fichero["File"])

        for sequence in self.data["Sequences"]:
            self.Sequences.append(sequence["Activate Zone"])

class GeneralConfiguration():
    RutaFFMPEG = None
    RutaMusica = None
    WebServerPort = 8000
    Pines = ""
    Secuencias = ""
    Programacion = ""
    ProgramConfiguration = ""
    Zones = ""
    Logger = None

    def __init__(self):
        self.Logger = logger.clienteLog.logger
        self.Logger.info("Cargamos configuracion general ")

        self.data = json.load(open('./config/configuracion.json'))

        pinesString = self.data["GeneralPins"]
        self.RutaMusica = self.data["MusicPath"]
        self.RutaFFMPEG = self.data["FfmpegPath"]
        self.WebServerPort = self.data["WebServerPort"]

        self.Pines = pinesString.split(",")
        self.Programacion = programacion()
        self.ProgramConfiguration = ProgramConfiguration()
        self.Zones = Zones()
