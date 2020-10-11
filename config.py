import json
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

    def __init__(self, path="./web/static/config"):
        self.Logger = logger.clienteLog.logger
        self.Logger.debug("Cargamos configuracion programacion")

        self.data = json.load(open(path + '/programacion.json'))
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
    ZonePosition = "LOCAL"

    def __cmp__(self, other):
        return cmp(self.ZoneId, other.ZoneId)

    def __eq__(self, other):
        return self.ZoneId==other.ZoneId

    def __lt__(self, other):
        return self.ZoneId < other.ZoneId

    def __gt__(self, other):
        return self.ZoneId > other.ZoneId

    def __init__(self, name, pins, id, type,position):
        self.ZoneName = name
        self.ZonePins = pins.split(",")
        self.ZoneId = id
        self.ZoneType = type
        self.ZonePosition = position


class Zones():
    Logger = None
    ZonePinType = ""
    DefinedZones = []
    OrderedPins = []

    def __init__(self , path="./web/static/config"):
        self.Logger = logger.clienteLog.logger
        self.Logger.debug("Cargamos configuracion Zones.json ")

        self.data = json.load(open(path + '/Zones.json'))

        self.ZonePinType = self.data["ZonePinType"]
        definedzonestemp = []
        for definedzone in self.data["Zones"]:
            ZoneTemp = Zone( definedzone["ZoneName"], definedzone["ZonePins"], definedzone["ZoneId"], definedzone["ZoneType"], definedzone["ZonePosition"])
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


class ProgramConfiguration():
    Logger = None
    ProgramName = ""
    ProgramType = ""
    ProgramInterval = 0.0
    MusicFiles = []
    Sequences = []

    def __init__(self, path="./web/static/config"):
        self.Logger = logger.clienteLog.logger
        self.Logger.debug("Cargamos configuracion ProgramConfiguration.json ")

        self.data = json.load(open(path + '/ProgramConfiguration.json'))

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
    Programacion = None
    ProgramConfiguration = None
    Zones = None
    I2CDevicesConf = None
    Logger = None

    def __init__(self, path="./web/static/config"):
        self.Logger = logger.clienteLog.logger
        self.Logger.debug("Cargamos configuracion general ")

        self.data = json.load(open(path+'/configuracion.json'))

        self.RutaMusica = self.data["MusicPath"]
        self.RutaFFMPEG = self.data["FfmpegPath"]
        self.WebServerPort = self.data["WebServerPort"]

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



