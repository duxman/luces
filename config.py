import json
import os
from Util import logger

class programacion:
    HoraDesde = ""
    HoraHasta = ""
    Estado=""
    Programa=""
    data = ""

    Secuencia = []
    Logger = None

    def __init__(self, Secuencias):
        self.Logger = logger.clienteLog.logger
        self.Logger.info("Cargamos configuracion programacion")

        self.data = json.load(open('./config/programacion.json'))
        self.HoraDesde = self.data["HoraDesde"]
        self.horaHasta = self.data["HoraHasta"]
        self.Estado = self.data["Estado"]
        programas = self.data["Programa"]
        self.repeticiones = self.data["repeticiones"]
        vprogramas = programas.split(",")

        for p in vprogramas:
            for s in Secuencias.items:
                if s.Nombre == p:
                    self.Secuencia.append( s )
                    break

class Secuencias:
    items = []

    def __init__(self):
        self.Logger = logger.clienteLog.logger
        self.Logger.info("Cargamos configuracion secuencias leds.json")

        dataTotal = json.load(open("./config/leds.json"))

        for d in dataTotal:
            sec = secuencia(d["pines"],d["musica"],d["secuencia"],d["intervalo"],d["Nombre"] )
            self.items.append( sec)

class secuencia:
    pines = ""
    musica = ""
    secuencia=""
    intervalo=""
    Nombre =  ""

    def __init__(self, pines,musica,secuencia,intervalo,nombre):
        self.Logger = logger.clienteLog.logger
        self.Logger.info("Cargamos configuracion secuencia ")
        self.Nombre = nombre
        self.pines = pines
        self.musica = musica
        self.secuencia = secuencia
        self.intervalo = intervalo


class GeneralConfiguration():
    RutaFFMPEG = None
    RutaMusica = None
    WebServerPort = 8000
    Pines=""
    Secuencias=""
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

        self.Secuencias = Secuencias()
        self.Programacion = programacion( self.Secuencias )


