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
        self.Logger.debug("Cargamos configuracion programacion")

        self.data = json.load(open('./config/programacion.json'))
        self.HoraDesde = self.data["StartTime"]
        self.HoraHasta = self.data["EndTime"]
        self.Estado = self.data["State"]
        self.Repeticiones =  self.data["Repeats"]
        self.WaitTime = int(self.data["WaitTime"])


class Zone():
    ZoneName = ""
    ZonePins = []
    ZoneId = 0
    ZoneType = ""

    def __cmp__(self, other):
        return cmp(self.ZoneId, other.ZoneId)

    def __eq__(self, other):
        return self.ZoneId==other.ZoneId

    def __lt__(self, other):
        return self.ZoneId < other.ZoneId

    def __gt__(self, other):
        return self.ZoneId > other.ZoneId

    def __init__(self, name, pins, id, type):
        self.ZoneName = name
        self.ZonePins = pins.split(",")
        self.ZoneId = id
        self.ZoneType = type

class I2CDevice():
    I2CAddress = 0x20
    BasePin = 65

    def __init__(self,address, base):
        self.I2CAddress = int(address,16)
        self.BasePin = int(base)

class Zones():
    Logger = None
    ZonePinType = ""
    DefinedZones = []
    OrderedPins = []

    def __init__(self):
        self.Logger = logger.clienteLog.logger
        self.Logger.debug("Cargamos configuracion Zones.json ")

        self.data = json.load(open('./config/Zones.json'))

        self.ZonePinType = self.data["ZonePinType"]
        definedzonestemp = []
        for definedzone in self.data["Zones"]:
            ZoneTemp = Zone( definedzone["ZoneName"], definedzone["ZonePins"], definedzone["ZoneId"], definedzone["ZoneType"])
            definedzonestemp.append( ZoneTemp )

        # Ordenamos la lista
        self.DefinedZones = sorted(definedzonestemp)

        # Montamos la lista para no tener que calcular los pines
        acttualpins = []
        for d in self.DefinedZones:
            acttualpins.extend(d.ZonePins)
            self.OrderedPins.append(list(acttualpins))

        # sustituimos los valores alone puesto que estos van solos
        for idx,val  in enumerate(self.DefinedZones):
            if val.ZoneType == "ALONE":
                self.OrderedPins[idx] = val.ZonePins

        # mostramos el resultado por si acaso
        for d in self.OrderedPins:
            self.Logger.info( ' '.join(d) )




class I2CDevices():
    Logger = None
    DefinedDevices = []

    def __init__(self):
        self.Logger = logger.clienteLog.logger
        self.Logger.debug("Cargamos configuracion I2CConfig.json ")

        self.data = json.load(open('./config/I2CConfig.json'))

        for device in self.data["Devices"]:
            devicetemp = I2CDevice(device["I2CAddress"], device["BasePin"])
            self.DefinedDevices.append(devicetemp)


class ProgramConfiguration():
    Logger = None
    ProgramName = ""
    ProgramType = ""
    ProgramInterval = 0.0
    MusicFiles = []
    Sequences = []

    def __init__(self):
        self.Logger = logger.clienteLog.logger
        self.Logger.debug("Cargamos configuracion ProgramConfiguration.json ")

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
    Pines = []
    Programacion = None
    ProgramConfiguration = None
    Zones = None
    I2CDevicesConf = None
    Logger = None

    def __init__(self):
        self.Logger = logger.clienteLog.logger
        self.Logger.debug("Cargamos configuracion general ")

        self.data = json.load(open('./config/configuracion.json'))

        pinesString = self.data["GeneralPins"]
        self.RutaMusica = self.data["MusicPath"]
        self.RutaFFMPEG = self.data["FfmpegPath"]
        self.WebServerPort = self.data["WebServerPort"]

        self.Pines = pinesString.split(",")

        try:
            self.ProgramConfiguration = ProgramConfiguration()
        except IOError:
            self.Logger.debug("No hay ProgramConfiguration")

        try:
            self.Programacion = programacion()
        except IOError:
            self.Logger.debug("No hay Programacion")

        try:
            self.Zones = Zones()

        except IOError:
            self.Logger.debug("No hay Zonas definidas")

        try:
            I2CDevicesConf = I2CDevices()
        except IOError:
            self.Logger.debug("No hay configuracion I2C")


