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
import sys
import getopt
from pydub import AudioSegment


class conversor(object):
    DestinoPath = ""
    OrigenPath = ""

    def __init__(self, filename=""):
        self.OrigenPath = filename
        self.DestinoPath = filename+".wav"



    def Convertir(self):
        sound = AudioSegment.from_mp3(self.OrigenPath)
        sound.export(self.DestinoPath, format="wav")
        return self.DestinoPath

def main(argv):
    inputfile = ""

    try:
        opts, args = getopt.getopt(argv, "hi:p:", ["ifile=", "path="])
    except getopt.GetoptError:
        print('Mp3ToWav.py -i <inputfile> -p <Path>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('Mp3ToWav.py -i <inputfile> -p <Path>')
            sys.exit()

        elif opt in ("-i", "--ifile"):
            inputfile = arg

    conv = conversor(inputfile)
    conv.Convertir()


if __name__ == "__main__":
    main(sys.argv[1:])