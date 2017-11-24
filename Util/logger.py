import logging

class clienteLog:
    logger = None
    def log(self):
        return clienteLog.logger

    def InicializaLog(self):
        clienteLog.logger = logging.getLogger('Application')

        fh = logging.FileHandler('./log/application.log')
        ch = logging.StreamHandler()

        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        clienteLog.logger.addHandler(fh)
        clienteLog.logger.addHandler(ch)
        clienteLog.logger.level = logging.INFO
        return clienteLog.logger


