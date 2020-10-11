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