import logging
import distutils.dir_util
from logging.handlers import RotatingFileHandler

class clienteLog:
    logger = None
    def log(self):
        return clienteLog.logger

    def InicializaLog(self, filename="./log/application.log"):
        clienteLog.logger = logging.getLogger('Application')
        clienteLog.logger.setLevel(logging.INFO)
        distutils.dir_util.mkpath("./log/")
        fh = RotatingFileHandler(filename, maxBytes=10000000, backupCount=2)

        ch = logging.StreamHandler()

        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        clienteLog.logger.addHandler(fh)
        clienteLog.logger.addHandler(ch)

        return clienteLog.logger

    def InicializaLogConsole(self):
        clienteLog.logger = logging.getLogger('Application')
        clienteLog.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        ch.setFormatter(formatter)
        clienteLog.logger.addHandler(ch)

        return clienteLog.logger

