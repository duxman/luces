False  # Credits to Andrew Oakley www.aoakley.com
# Thanks a lot for the inspiration of this program
# By parameter takes resolution and image and create animation
import getopt
import json
import time, sys, os
import board
# if os == 'poxis':
import neopixel  # See https://learn.adafruit.com/neopixels-on-raspberry-pi/software
# else:
# from Util.neopixelsimulator import NeoPixel, RGB

from PIL import Image  # Use apt-get install python-imaging to install this


def calculateMatrix(MatrixHeight, MatrixWidth):
    bInc = True
    myMatrix = []
    for i in range(MatrixHeight, 0, -1):
        # Calculate Max and min led
        maxled = (i * MatrixWidth)
        minled = (maxled - MatrixWidth)
        # For calculate go and return
        if bInc == False:
            rangeMatrixLine = range(maxled - 1, minled - 1, -1)
            bInc = True
        else:
            rangeMatrixLine = range(minled, maxled, 1)
            bInc = False;
        myMatrix.extend(rangeMatrixLine)
    return myMatrix


class configurationLedMatrix(object):
    # Array of images
    Animations = []
    # Configuration of ledMatrix
    ################################################################
    #                 In configuration File
    ################################################################

    # Size of your matrix
    MatrixWidth = 32
    MatrixHeight = 16
    LedPin = 18  # GPIO pin connected to the pixels (must support PWM!).
    ################################################################
    #                 In configuration File
    ################################################################

    ################################################################
    #               Probably not configurable
    ################################################################

    LedFreqHz = 800000  # LED signal frequency in hertz (usually 800khz)
    LedDma = 5  # DMA channel to use for generating signal (try 5)
    LedBrigh = 255  # Set to 0 for darkest and 255 for brightest
    LedInvert = False  # True to invert the signal (when using NPN transistor level shift)
    ################################################################
    #               Probably not configurable
    ################################################################

    ################################################################
    #           Auto calculate
    ################################################################
    myMatrix = []
    LedCount = 0

    ################################################################
    #           Auto calculate
    ################################################################

    ################################################################
    #               Example
    ################################################################
    # [95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 85, 84,
    # 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83,
    # 71, 70, 69, 68, 67, 66, 65, 64, 63, 62, 61, 60,
    # 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
    # 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36,
    # 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
    # 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12,
    # 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

    def __init__(self, path):
        self.data = json.load(open(path + '/config/configurationLedMatrix.json'))
        self.MatrixWidth = self.data["MatrixWidth"]
        self.MatrixHeight = self.data["MatrixHeight"]
        self.LedCount = self.MatrixWidth * self.MAtrixHeight
        self.LedPin = self.data["LedPin"]

        for anim in self.data["Animations"]:
            anim["width"] = self.MatrixWidth
            anim["height"] = self.MatrixHeight
            json.dump(anim)
            animtemp = animation(json.dump(anim))

            self.Animations.append(animtemp)

        # self.LedFreqHz = self.data["LedFreqHz"]
        # self.LedDma = self.data["LedDma"]
        # self.LedBrigh = self.data["LedBrigh"]
        # self.LedInvert = self.data["LedInvert"]
        self.myMatrix = calculateMatrix(self.MatrixHeight, self.MatrixWidth)


class commandLine(object):
    IniFrame = 0
    EndFrame = 0
    Instruction = ""
    Value = 0.0

    def __init__(self, ini, end, ins, val):
        self.IniFrame = ini
        self.EndFrame = end
        self.Instruction = ins
        self.Value = val


class animation(object):
    ImageFile = ""
    CommandFile = ""
    image = None
    width = 0
    heigt = 0
    # instructions: commandLine = []
    instructions = []
    Repetitions = -1
    # Speed of movement, in seconds (recommend 0.1-0.3)
    Speed = 0.075

    # Example
    # "{'ImageFile': 'file', 'CommandFile': '', 'width': 128, 'heigt': 8, 'Repetitions': 5, 'Speed': 0.1}"
    def __init__(self, TxtData):
        data = json.loads(TxtData)

        self.ImageFile = data["ImageFile"]
        self.command = data["CommandFile"]
        self.width = data["width"]
        self.height = data["height"]
        self.Repetitions = data["Repetitions"]
        self.Speed = data["Speed"]
        # Procesamos
        self.loadImage()
        self.loadAnimationCommand()

    def loadImage(self):
        # Open the image file given as the command line parameter
        try:
            loadIm = Image.open(self.ImageFile)
        except:
            raise Exception("Image file %s could not be loaded" % self.ImageFile)

        if loadIm.size[1] != self.heigt:
            origIm = loadIm.resize(
                (loadIm.size[0] / (loadIm.size[1] // self.height), self.height),
                Image.BICUBIC)
        else:
            origIm = loadIm.copy()
        # If the input is a very small portrait image, then no amount of resizing will save us
        if origIm.size[0] < self.width:
            raise Exception("Picture is too narrow. Must be at least %s pixels wide" % self.width)

        # Add a copy of the start of the image, to the end of the image,
        # so that it loops smoothly at the end of the image
        self.image = Image.new('RGB', (origIm.size[0] + self.width, self.height))
        self.image.paste(origIm, (0, 0, origIm.size[0], self.height))
        self.image.paste(origIm.crop((0, 0, self.width, self.height)),
                         (origIm.size[0], 0, origIm.size[0] + self.width, self.height))

    def loadAnimationCommand(self):
        if self.CommandFile != "":
            data = json.load(open(self.CommandFile))
            for inst in data["Commands"]:
                cLine = commandLine(inst["IniFrame"], inst["EndFrame"], inst["Instruction"], inst["Value"])
                self.instructions.append(cLine)


class matrixAnimation(object):
    Logger = None
    ImageFile = ""
    Config = None
    loadIm = None
    origIm = None
    im = None
    txtlines = []
    LedStrip: neopixel.NeoPixel = None
    myMatrix = []

    def __init__(self, test=False):
        if test == False:
            self.Config = configurationLedMatrix()
            self.initializeNeoPixel(self.Config.LedPin, self.Config.LedCount)

    def initializeNeoPixel(self, ledPin, LedCount):
        # Create NeoPixel object with appropriate configuration.
        self.LedStrip = neopixel.NeoPixel(ledPin,
                                          LedCount,
                                          brightness=1.0,
                                          auto_write=False,
                                          pixel_order=neopixel.GRB)

        self.initLeds(self.LedStrip)

    def initializeImages(self):
        del self.loadIm
        del self.origIm
        del self.im
        del self.txtlines
        self.loadIm = None
        self.origIm = None
        self.im = None
        self.txtlines = []

        # Load the animation config
        self.loadAnimationConfig()

    def allonecolour(self, strip, colour):

        # Paint the entire matrix one colour
        strip.fill(colour)
        strip.show()

    def colour(self, r, g, b):
        # Fix for Neopixel RGB->GRB, also British spelling
        return self.colourTuple([g, r, b])

    def colourTuple(self, rgbTuple):
        red = rgbTuple[0]
        green = rgbTuple[1]
        blue = rgbTuple[2]
        RGBint = (red << 16) + (green << 8) + blue
        return RGBint

    def initLeds(self, strip):
        # Intialize the library (must be called once before other functions).
        # strip.begin()
        # Wake up the LEDs by briefly setting them all to white
        self.allonecolour(strip, self.colour(255, 255, 255))
        time.sleep(0.01)

    def startAnimation(self, Anim: animation, myMatrix):
        # And here we go.
        try:
            rep = Anim.Repetitions
            if Anim.Repetitions < 0:
                rep = sys.maxsize
            for i in range(rep):
                # Loop through the image widthways
                # Can't use a for loop because Python is dumb
                # and won't jump values for FLIP command
                x = 0
                # Initialise a pointer for the current line in the text file
                tx = 0

                while x < Anim.image.size[0] - Anim.width:

                    # Set the sleep period for this frame
                    # This might get changed by a textfile command
                    thissleep = Anim.Speed

                    # Set the increment for this frame
                    # Typically advance 1 pixel at a time but
                    # the FLIP command can change this
                    thisincrement = 1

                    rg = Anim.image.crop((x, 0, x + Anim.width, Anim.height))
                    dots = list(rg.getdata())

                    for i in range(len(dots)):
                        id = myMatrix[i]
                        self.LedStrip[id] = self.colourTuple(dots[i])
                        # self.strip.setPixelColor(self.Config.myMatrix[i], self.colourTuple(dots[i]))

                    self.LedStrip.show()

                    # by the moment without instructions

                    x = x + thisincrement
                    time.sleep(thissleep)

        except (KeyboardInterrupt, SystemExit):
            print("Stopped")
            self.allonecolour(self.LedStrip, self.colour(0, 0, 0))


def main(argv):
    inputfile = ""

    try:
        opts, args = getopt.getopt(argv, "a:", ["AnimationData="])
    except getopt.GetoptError:
        print('LedMatrixAnimation.py -a <json animation data>')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-a", "--AnimationData"):
            inputfile = arg

    ani = animation(inputfile)
    myMatrix = calculateMatrix(ani.height, ani.width)

    ma = matrixAnimation(True)
    

    ma.initializeNeoPixel(board.D18, len(myMatrix))
    ma.startAnimation(ani, myMatrix)


if __name__ == "__main__":
    main(sys.argv[1:])
