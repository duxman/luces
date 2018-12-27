import logging
from logging.handlers import RotatingFileHandler

class clienteLog:
    logger = None
    def log(self):
        return clienteLog.logger

    def InicializaLog(self):
        clienteLog.logger = logging.getLogger('Application')
        clienteLog.logger.setLevel(logging.INFO)
        fh = RotatingFileHandler('./log/application.log', maxBytes=10000000, backupCount=2)

        ch = logging.StreamHandler()

        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        clienteLog.logger.addHandler(fh)
        clienteLog.logger.addHandler(ch)

        return clienteLog.logger


