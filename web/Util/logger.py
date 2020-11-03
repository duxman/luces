#
# Copyright (c) 2020-2037 duxman.
#
# This file is part of Duxman Luces 
# (see https://github.com/duxman/luces).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
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

