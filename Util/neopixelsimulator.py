RGB = "RGB"
"""Red Green Blue"""
GRB = "GRB"
"""Green Red Blue"""
RGBW = "RGBW"
"""Red Green Blue White"""
GRBW = "GRBW"

class NeoPixel(object):
    def __init__( self, pin, n, *, bpp=3, brightness=1.0, auto_write=True, pixel_order=None):
        print("initialize")

    def fill(self, color):
        print("fill")

    def __setitem__(self, index, val):
        print("set [" + str(index) + "]=" + str(val))

    def show(self):
        print("Show")
    def begin(self):
        print("Begin")




