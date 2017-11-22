import json

from Util.logger import clienteLog

Logger = None

class programacion:
    HoraDesde = ""
    HoraHasta = ""
    Estado=""
    Programa=""
    data = ""

    Secuencia = ""
    Logger = None

    def __init__(self,log):
        self.Logger = log
        self.Logger.info("Cargamos configuracion programacion")

        self.data = json.load(open('./config/programacion.json'))
        self.HoraDesde = self.data["HoraDesde"]
        self.horaHasta = self.data["HoraHasta"]
        self.Estado = self.data["Estado"]
        self.Programa = self.data["Programa"]
        self.Secuencia = secuencia(self.Programa,log)

class secuencia:
    pines = ""
    musica = ""
    secuencia=""
    intervalo=""
    repeticiones=""
    data = ""
    Logger = None

    def __init__(self, fichero, log):
        self.Logger = log
        self.Logger.info("Cargamos configuracion secuencia " + fichero)

        self.data = json.load(open(fichero))
        self.pines = self.data["pines"]
        self.musica = self.data["musica"]
        self.secuencia = self.data["secuencia"]
        self.intervalo = self.data["intervalo"]
        self.repeticiones = self.data["repeticiones"]


class GeneralConfiguration(clienteLog):
    Pines=""
    Secuencias=""
    Programacion = ""
    Logger = None


    def __init__(self, log):
        self.Logger = log
        self.Logger.info("Cargamos configuracion general ")

        self.data = json.load(open('./config/configuration.json'))

        pinesString = self.data["Pines"]

        self.Pines = pinesString.split(",")

        for pin in self.Pines:
            self.Pines = pin

        self.Programacion = programacion(self.Logger)


