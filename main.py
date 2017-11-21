import config
from logger import clienteLog
from www.AudioSpectrogram import WaveSynchronize
from www.PinManager import PinManager
from www.server import WebServer


class  DuxmanLights(object):
    Logger = None
    Config = None
    ConfigServer = None
    MusicManager =  None
    PinManager =  None
    PinList = [2,3,4,17,27,22,10,9,11,5]

    def pinManager(self):
       self.PinManager = PinManager(self.Logger,self.PinList)

    def musicManager(self):
        fil = "c://music/sample2.wav"  # sys.argv[1]
        self.MusicManager = WaveSynchronize( self.Logger,fil,self.PinManager.EncenderInRange)
        self.MusicManager.ExecuteWav()

    def execute(self):
        self.pinManager()
        self.musicManager()

    def __init__(self):
        cliente = clienteLog()
        self.Logger = cliente.InicializaLog()
        self.Logger.info("--------------------<<  INI  >>--------------------")
        self.Logger.info("Arrancamos la ejecucion")
        self.Config = config.GeneralConfiguration( self.Logger )
        self.Logger.info("Configuracion Cargada")
        #self.ConfigServer = WebServer(8000, self.Logger)
        self.execute()
        # my code here

if __name__ == "__main__":
    mainprogram = DuxmanLights()

