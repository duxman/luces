import json

import os

from Util import logger

Logger = None

class programacion:
    HoraDesde = ""
    HoraHasta = ""
    Estado=""
    Programa=""
    data = ""

    Secuencia = []
    Logger = None

    def __init__(self):
        self.Logger = logger.clienteLog.logger
        self.Logger.info("Cargamos configuracion programacion")

        self.data = json.load(open('./config/programacion.json'))
        self.HoraDesde = self.data["HoraDesde"]
        self.horaHasta = self.data["HoraHasta"]
        self.Estado = self.data["Estado"]
        programas = self.data["Programa"]
        vprogramas = programas.split(",")

        for p in vprogramas:
            self.Secuencia.append( secuencia(p) )

class secuencia:
    pines = ""
    musica = ""
    secuencia=""
    intervalo=""
    repeticiones=""
    data = ""
    Logger = None
    Nombre =  ""

    def __init__(self, fichero):
        self.Logger = logger.clienteLog.logger
        self.Logger.info("Cargamos configuracion secuencia " + fichero)

        self.data = json.load(open(fichero))
        self.Nombre =  os.path.splitext(fichero)[0].upper()
        self.pines = self.data["pines"]
        self.musica = self.data["musica"]
        self.secuencia = self.data["secuencia"]
        self.intervalo = self.data["intervalo"]
        self.repeticiones = self.data["repeticiones"]

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


        self.Programacion = programacion()


