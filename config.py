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
        self.Repeticiones = self.data["Repeats"]
        self.WaitTime = int(self.data["WaitTime"])


class Zone():
    ZoneName = ""
    ZonePins = []
    ZoneId = 0
    ZoneType = ""
    ZonePosition = "LOCAL"
    VumeterNumber = 0
    VumeterSection = 0
    VumeterType = ""
    VumeterData = None

    def __cmp__(self, other):
        return cmp(self.ZoneId, other.ZoneId)

    def __eq__(self, other):
        return self.ZoneId == other.ZoneId

    def __lt__(self, other):
        return self.ZoneId < other.ZoneId

    def __gt__(self, other):
        return self.ZoneId > other.ZoneId

    def __init__(self, name, pins, id, type, position,VNumber, VSection,VType):
        self.ZoneName = name
        self.ZonePins = pins.split(",")
        self.ZoneId = id
        self.ZoneType = type
        self.ZonePosition = position
        self.VumeterData = []
        if self.ZoneType == "VUMETER":
            self.VumeterNumber = int(VNumber)
            self.VumeterSection = int(VSection)
            self.VumeterType = VType
            for i in range(self.VumeterSection):
                inicio =int(((self.VumeterNumber / self.VumeterSection) * i) + 1)
                fin = int((self.VumeterNumber / self.VumeterSection) * (i +1))
                if self.VumeterType == "RTOL":
                    self.VumeterData.append([inicio, fin] )
                elif self.VumeterType == "lTOR":
                    self.VumeterData.append([fin, inicio])
                elif self.VumeterType == "STOC":
                    self.VumeterData.append([inicio, int(fin/2)])
                    self.VumeterData.append([fin, int(fin/2)])
                elif self.VumeterType == "CTOS":
                    self.VumeterData.append([int(fin / 2), inicio])
                    self.VumeterData.append([int(fin / 2), fin])




class Zones():
    Logger = None
    ZonePinType = ""
    DefinedZones = []
    SpectrumPins = []
    VumeterPins = []
    AlonePins = []

    def __init__(self, path="./web/static/config"):
        self.Logger = logger.clienteLog.logger
        self.Logger.debug("Cargamos configuracion Zones.json ")

        self.data = json.load(open(path + '/Zones.json'))

        self.ZonePinType = self.data["ZonePinType"]
        definedzonestemp = []
        for definedzone in self.data["Zones"]:
            ZoneTemp = Zone(definedzone["ZoneName"],
                            definedzone["ZonePins"],
                            definedzone["ZoneId"],
                            definedzone["ZoneType"],
                            definedzone["ZonePosition"],
                            definedzone["VumeterNumber"],
                            definedzone["VumeterSection"],
                            definedzone["VumeterType"] )
            definedzonestemp.append(ZoneTemp)

        # Ordenamos la lista
        self.DefinedZones = sorted(definedzonestemp)

        # Montamos la lista para no tener que calcular los pines
        for d in self.DefinedZones:
            if (d.ZoneType == "ALONE"):
                self.AlonePins.extend(d.ZonePins)
            if (d.ZoneType == "VUNETER"):
                self.VumeterPins.extend(d.ZonePins)
            if (d.ZoneType == "SPECTRUM"):
                self.SpectrumPins.extend(d.ZonePins)

        #Eliminamos pins duplicados
        self.AlonePins = list(dict.fromkeys(self.AlonePins))
        self.VumeterPins = list(dict.fromkeys(self.VumeterPins))
        self.SpectrumPins = list(dict.fromkeys(self.SpectrumPins))

        #Ordenamos pins duplicados
        self.AlonePins.sort()
        self.VumeterPins.sort()
        self.SpectrumPins.sort()

        # mostramos el resultado por si acaso
        for d in self.SpectrumPins:
            self.Logger.info(' '.join(d))


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
        self.ProgramInterval = float(self.data["ProgramInterval"])
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

        self.data = json.load(open(path + '/configuracion.json'))

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
