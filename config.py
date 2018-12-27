import json
import os
from Util import logger


class programacion:
    HoraDesde = ""
    HoraHasta = ""
    Estado = ""
    Programa = ""
    data = ""

    Secuencia = []
    Logger = None

    def __init__(self):
        self.Logger = logger.clienteLog.logger
        self.Logger.info("Cargamos configuracion programacion")

        self.data = json.load(open('./config/programacion.json'))
        self.HoraDesde = self.data["HoraDesde"]
        self.HoraHasta = self.data["HoraHasta"]
        self.Estado = self.data["Estado"]
        programas = self.data["Programa"]
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
    Data = ""
    def __init__(self, file):
        self.Logger = logger.clienteLog.logger
        self.Logger.info("Cargamos configuracion secuencias" + file)

        self.Data = json.load(open(file))

        self.pines = self.Data["pines"]
        self.musica = self.Data["musica"]
        self.secuencia = self.Data["secuencia"]
        self.intervalo = self.Data["intervalo"]
        self.repeticiones = self.Data["repeticiones"]
        self.nombre = file

    def initialize (self, pines, musica, secuencia, intervalo, repeticiones, nombre):
        self.Logger = logger.clienteLog.logger
        self.Logger.info("Cargamos configuracion secuencia ")
        self.nombre = nombre
        self.pines = pines
        self.musica = musica
        self.secuencia = secuencia
        self.intervalo = intervalo
        self.repeticiones = repeticiones


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

        self.data = json.load(open('./config/configuration.json'))

        pinesString = self.data["Pines"]
        self.RutaMusica = self.data["RutaMusica"]
        self.RutaFFMPEG = self.data["Rutaffmpeg"]
        self.WebServerPort = self.data["WebServerPort"]

        self.Pines = pinesString.split(",")

        # self.Secuencias = Secuencias()
        self.Programacion = programacion()
