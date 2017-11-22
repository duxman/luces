import logging

class clienteLog:
    logger = None
    def log(self):
        return self.logger

    def InicializaLog(self):
        self.logger = logging.getLogger('Application')

        fh = logging.FileHandler('./log/application.log')
        ch = logging.StreamHandler()

        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        self.logger.level = logging.INFO
        return self.logger


