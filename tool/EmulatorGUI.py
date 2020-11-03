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

    def analogread(self,a):
        return 500

    def analogwrite(self,a,b):
        self.Logger.debug(str(a) + "=" + str(b))

    def cleanup(self):
        self.Logger.debug("Clean UP")

    def setmode(self,a):
        self.Logger.debug(a)

    def setwarnings(self,flag):
        self.Logger.debug('False')