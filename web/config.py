import json


class GeneralConfiguration():
    RutaFFMPEG = None
    RutaMusica = None
    WebServerPort = 8000

    def __init__(self):
        #self.Logger = logger.clienteLog.logger
        #self.Logger.debug("Cargamos configuracion general ")

        self.data = json.load(open('static/config/configuracion.json'))

        self.RutaMusica = self.data["MusicPath"]
        self.RutaFFMPEG = self.data["FfmpegPath"]
        self.WebServerPort = self.data["WebServerPort"]