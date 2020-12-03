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
import json
from Util import logger
from PIL import Image  # Use apt-get install python-imaging to install this


class programacion(object):
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


class Zone(object):
    ZonePinType = ""
    MQTT_TOKEN = "PinManager"
    ZoneName = ""
    ZonePins: dict = {}
    ZoneId = 0
    ZoneType = ""

    def __cmp__(self, other):
        return __cmp__(self.ZoneId, other.ZoneId)

    def __eq__(self, other):
        return self.ZoneId == other.ZoneId

    def __lt__(self, other):
        return self.ZoneId < other.ZoneId

    def __gt__(self, other):
        return self.ZoneId > other.ZoneId

    def __init__(self, name, PinsArray, id, type, PinType, MQTT_TOKEN):
        self.ZoneName = name
        self.ZonePins = dict()
        for zp in PinsArray:
            pins = zp["ZonePinId"].split(",")
            self.ZonePins[zp["ZonePinValue"]] = pins
        self.ZoneId = id
        self.ZoneType = type
        self.ZonePinType = PinType
        self.MQTT_TOKEN = MQTT_TOKEN


class Zones(object):
    Logger = None
    DefinedZones = []
    SpectrumPins = []
    AlonePins = []
    Tokens = []
    MaxPinValue = 0

    def __init__(self, path="./web/static/config"):
        self.Logger = logger.clienteLog.logger
        self.Logger.debug("Cargamos configuracion Zones.json ")

        self.data = json.load(open(path + '/Zones.json'))
        self.Tokens = []
        definedzonestemp = []
        for definedzone in self.data["Zones"]:
            definedzonestemp.append( Zone(definedzone["ZoneName"],
                            definedzone["ZonePinsArray"],
                            definedzone["ZoneId"],
                            definedzone["ZoneType"],
                            definedzone["ZonePinType"],
                            definedzone["MQTT_TOKEN"]) )

        # Ordenamos la lista
        self.DefinedZones = sorted(definedzonestemp)
        max = 0
        for z in self.DefinedZones:
            for k in z.ZonePins.keys():
                if k > max:
                    max=k

        self.MaxPinValue = max

        # Montamos la lista para no tener que calcular los pines
        for d in self.DefinedZones:
            if d.ZoneType == "ALONE":
                self.AlonePins.extend(d.ZonePins)
            if d.ZoneType == "SPECTRUM":
                for zp in d.ZonePins:
                    self.SpectrumPins.extend(d.ZonePins[zp])
            if d.ZonePinType == "REMOTE":
                self.Tokens.append(d.MQTT_TOKEN)

        # Eliminamos pins duplicados
        self.AlonePins = list(dict.fromkeys(self.AlonePins))
        self.SpectrumPins = list(dict.fromkeys(self.SpectrumPins))
        # Eliminamos Tokens duplicados
        self.Tokens = list(dict.fromkeys(self.Tokens))

        # Ordenamos pins duplicados
        self.AlonePins.sort()
        self.SpectrumPins.sort()

        # mostramos el resultado por si acaso
        for d in self.SpectrumPins:
            self.Logger.info(' '.join(d))


class ProgramConfiguration(object):
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


class GeneralConfiguration(object):
    RutaFFMPEG = None
    RutaMusica = None
    WebServerPort = 8000
    Programacion = None
    MQTT_HOST = "localhost"
    MQTT_PORT = 1883
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
        self.MQTT_HOST = self.data["MQTT_HOST"]
        self.MQTT_PORT = self.data["MQTT_PORT"]

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


def calculateMatrix(MatrixHeight, MatrixWidth, Side="LEFT", PanelsV=1, PanelsH=1):
    if Side == "LEFT":
        bInc = False
    else:
        bInc = True

    CountLeds = MatrixHeight * MatrixWidth
    VerticalHeight = MatrixHeight * PanelsV

    myMatrix = []
    for i in range(VerticalHeight, 0, -1):
        rangeMatrixLine = []
        linetemp = [];
        # Calculate Max and min led
        maxled = (i * MatrixWidth)
        minled = (maxled - int(MatrixWidth))
        # For calculate go and return
        if bInc == False:
            rangeMatrixLine.extend(range(maxled - 1, minled - 1, -1))
            bInc = True
        else:
            rangeMatrixLine.extend(range(minled, maxled, 1))
            bInc = False;
        print("range line " + str(i))
        print(rangeMatrixLine)

        for p in range(PanelsH):
            valorSuma = p * CountLeds
            line = list(map(lambda x: x + valorSuma, rangeMatrixLine))
            print("line " + str(i))
            print(line)
            myMatrix.extend(line)
    return myMatrix


class LedMatrix(object):
    ################################################################
    #                 In configuration File
    ################################################################
    # Size of your matrix
    MatrixWidth = 32
    MatrixHeight = 16
    LedPin = 18  # GPIO pin connected to the pixels (must support PWM!).
    MQTT_HOST = "127.0.0.1"
    MQTT_PORT = 8080
    MQTT_TOKEN = "DATA"
    MatrixStartLed = "RIGHT"
    MatrixType = "NONE"
    Animations = []
    VerticalPanels = 1
    HorizontalPanels = 1
    ################################################################
    #                 In configuration File
    ################################################################

    ################################################################
    #               Probably not configurable
    ################################################################

    LedFreqHz = 800000  # LED signal frequency in hertz (usually 800khz)
    LedDma = 5  # DMA channel to use for generating signal (try 5)
    LedBrigh = 255  # Set to 0 for darkest and 255 for brightest
    LedInvert = False  # True to invert the signal (when using NPN transistor level shift)
    ################################################################
    #               Probably not configurable
    ################################################################

    ################################################################
    #           Auto calculate
    ################################################################
    myMatrix = []
    LedCount = 0

    ################################################################
    #           Auto calculate
    ################################################################
    def __init__(self, MatrixWidth, MatrixHeight, LedPin, MQTT_HOST, MQTT_PORT, MQTT_TOKEN, MatrixStartLed, MatrixType,
                 PanelsV, PanelsH, AnimationsData):
        self.MatrixWidth = MatrixWidth
        self.MatrixHeight = MatrixHeight
        self.LedPin = LedPin  # GPIO pin connected to the pixels (must support PWM!).
        self.MQTT_HOST = MQTT_HOST
        self.MQTT_PORT = MQTT_PORT
        self.MQTT_TOKEN = MQTT_TOKEN
        self.VerticalPanels = PanelsV
        self.HorizontalPanels = PanelsH
        self.MatrixStartLed = MatrixStartLed
        self.MatrixType = MatrixType
        data = json.loads(AnimationsData)
        for anim in data:
            anim["width"] = self.MatrixWidth
            anim["height"] = self.MatrixHeight
            animtemp = animation(json.dumps(anim))
            self.Animations.append(animtemp)
        self.myMatrix = calculateMatrix(self.MatrixHeight, self.MatrixWidth, self.MatrixStartLed, self.VerticalPanels,
                                        self.HorizontalPanels)


class configurationLedMatrix(object):
    # Array of images
    Matrix: LedMatrix = []

    def __init__(self, path="./web/static/config"):
        self.data = json.load(open(path + '/LedMatrix.json'))
        for mtx in self.data["Matrix"]:
            lm = LedMatrix(mtx["MatrixWidth"],
                           mtx["MatrixHeight"],
                           mtx["LedPin"],
                           mtx["MQTT_HOST"],
                           mtx["MQTT_PORT"],
                           mtx["MQTT_TOKEN"],
                           mtx["MatrixStartLed"],
                           mtx["MatrixType"],
                           mtx["VerticalPanels"],
                           mtx["HorizontalPanels"],
                           json.dumps(mtx["Animations"]))
        self.Matrix.append(lm)


class commandLine(object):
    IniFrame = 0
    EndFrame = 0
    Instruction = ""
    Value = 0.0

    def __init__(self, ini, end, ins, val):
        self.IniFrame = ini
        self.EndFrame = end
        self.Instruction = ins
        self.Value = val


class animation(object):
    ImageFile = ""
    CommandFile = ""
    image = None
    width = 0
    heigth = 0
    type = ""

    # instructions: commandLine = []
    instructions = []
    Repetitions = -1
    # Speed of movement, in seconds (recommend 0.1-0.3)
    Speed = 0.075

    # Example
    # "{'ImageFile': 'file', 'CommandFile': '', 'width': 128, 'heigth': 8, 'Repetitions': 5, 'Speed': 0.1 }"
    def __init__(self, TxtData):
        data = json.loads(TxtData)

        self.ImageFile = data["ImageFile"]
        self.command = data["CommandFile"]
        self.width = data["width"]
        self.height = data["height"]
        self.Repetitions = data["Repetitions"]
        self.Speed = data["Speed"]
        # Procesamos
        self.loadImage()
        self.loadAnimationCommand()

    def loadImage(self):
        # Open the image file given as the command line parameter
        try:
            loadIm = Image.open(self.ImageFile)
        except:
            raise Exception("Image file %s could not be loaded" % self.ImageFile)

        if loadIm.size[1] != self.height:
            origIm = loadIm.resize(
                (loadIm.size[0] / (loadIm.size[1] // self.height), self.height),
                Image.BICUBIC)
        else:
            origIm = loadIm.copy()
        # If the input is a very small portrait image, then no amount of resizing will save us
        if origIm.size[0] < self.width:
            raise Exception("Picture is too narrow. Must be at least %s pixels wide" % self.width)

        # Add a copy of the start of the image, to the end of the image,
        # so that it loops smoothly at the end of the image
        self.image = Image.new('RGB', (origIm.size[0] + self.width, self.height))
        self.image.paste(origIm, (0, 0, origIm.size[0], self.height))
        self.image.paste(origIm.crop((0, 0, self.width, self.height)),
                         (origIm.size[0], 0, origIm.size[0] + self.width, self.height))

    def loadAnimationCommand(self):
        if self.CommandFile != "":
            data = json.load(open(self.CommandFile))
            for inst in data["Commands"]:
                cLine = commandLine(inst["IniFrame"], inst["EndFrame"], inst["Instruction"], inst["Value"])
                self.instructions.append(cLine)
