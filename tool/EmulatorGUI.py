BCM = "BCM"
BOARD = "BOARD"
OUT = "OUT"
IN = "IN"
LOW = 0
HIGH = 1

def setmode(a):
   print a
def setup(a, b):
    print str(a) + "=" + str(b)
def output(a, b):
    print str(a) + "=" + str(b)
def cleanup():
   print "Clean UP"
def setmode(a):
   print a
def setwarnings(flag):
   print 'False'