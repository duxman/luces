from Util.logger import clienteLog

class emulatorGPIO(object):
    BCM = "BCM"
    BOARD = "BOARD"
    OUT = "OUT"
    IN = "IN"
    LOW = 0
    HIGH = 1
    Loggger = None

    def __init__(self):
        cliente = clienteLog()
        self.Logger = cliente.InicializaLogConsole()

    def setmode(self,a):
        self.Logger.debug(a)

    def setup(self,a, b):
        self.Logger.debug(str(a) + "=" + str(b))

    def output(self,a, b):
        self.Logger.debug(str(a) + "=" + str(b))

    def cleanup(self):
        self.Logger.debug("Clean UP")

    def setmode(self,a):
        self.Logger.debug(a)

    def setwarnings(self,flag):
        self.Logger.debug('False')