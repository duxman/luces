import json
import os
from Util import logger


class programacion:
    HoraDesde = ""
    HoraHasta = ""
    Estado = ""
    Programa = ""
    Repeticiones = -1
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
        programas = self.data["Programs"]
        self.Repeticiones =  self.data["Repeats"]
        vprogramas = programas.split(",")

        for p in vprogramas:
            confledn = Secuencia(p)
            self.Secuencia.append(confledn)


class Secuencia:
    pines = ""
    musica = ""
    secuencia = ""
    intervalo = ""
    nombre = ""
    repeticiones = ""
    type = ""
    Data = ""
    def __init__(self, file):
        self.Logger = logger.clienteLog.logger
        self.Logger.info("Cargamos configuracion secuencias" + file)

        self.Data = json.load(open("./config/"+file))

        self.pines = self.Data["Pins"]
        self.musica = self.Data["Music"]
        self.secuencia = self.Data["Secuence"]
        self.intervalo = self.Data["Interval"]
        self.repeticiones = self.Data["Repeat"]
        self.type = self.Data["Type"]
        self.nombre = self.Data["Name"]


class GeneralConfiguration():
    RutaFFMPEG = None
    RutaMusica = None
    WebServerPort = 8000
    Pines = ""
    Secuencias = ""
    Programacion = ""
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

        # self.Secuencias = Secuencias()
        self.Programacion = programacion()
