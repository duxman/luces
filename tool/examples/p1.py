from appJar.appjar import gui

class  DuxmanGpioEmulator():
  app = None
  GND_PINS    = ["PIN06","PIN14","PIN20","PIN30","PIN34","PIN09","PIN25","PIN39"]
  DC_PINS     = ["PIN01","PIN02","PIN04","PIN17"]
  GPIO_PINS   = ["PIN03","PIN05","PIN07","PIN08","PIN10","PIN11","PIN12","PIN13","PIN15","PIN16","PIN18","PIN19","PIN21","PIN22","PIN23","PIN24","PIN26","PIN27","PIN28","PIN29","PIN31","PIN32","PIN33","PIN35","PIN36","PIN37","PIN38","PIN40"]
  PIN_LINE1   = ["PIN01","PIN02","PIN03","PIN04","PIN05","PIN06","PIN07","PIN08","PIN09","PIN10","PIN11","PIN12","PIN13","PIN14","PIN15","PIN16","PIN17","PIN18","PIN19","PIN20"]
  PIN_LINE2   = ["PIN21","PIN22","PIN23","PIN24","PIN25","PIN26","PIN27","PIN28","PIN29","PIN30","PIN31","PIN32","PIN33","PIN34","PIN35","PIN36","PIN37","PIN38","PIN39","PIN40"]
  PIN_NAME    = [["PIN01","3v3   "],["PIN02","5v    "],["PIN03","GPIO 2"],["PIN04","5v    "],["PIN05","GPIO 3"],["PIN06","GND   "],["PIN07","GPIO 4"],["PIN08","GPIO14"],["PIN09","GND   "],["PIN10","GPIO15"],["PIN11","GPIO17"],["PIN12","GPIO18"],["PIN13","GPIO27"],["PIN14","GND   "],["PIN15","GPIO22"],["PIN16","GPIO23"],["PIN17","3v3   "],["PIN18","GPIO24"],["PIN19","GPIO10"],["PIN20","GND   "],["PIN21","GPIO9 "],["PIN22","GPIO25"],["PIN23","GPIO11"],["PIN24","GPIO 8"],["PIN25","GND   "],["PIN26","GPIO 7"],["PIN27","ID SD "],["PIN28","ID SC "],["PIN29","GPIO 5"],["PIN30","   GND"],["PIN31","GPIO 6"],["PIN32","GPIO12"],["PIN33","GPIO13"],["PIN34","   GND"],["PIN35","GPIO19"],["PIN36","GPIO16"],["PIN37","GPIO26"],["PIN38","GPIO20"],["PIN39","   GND"],["PIN40","GPIO21"]]

  BCM         = "BCM"
  BOARD       = "BOARD"
  OUT         = "OUT"
  IN          = "IN"
  MODE        = "BCM"

  def setmode(self,mode):
    self.MODE = mode
    print "Selected mode = " + mode

  def setup(self ,pin , mode):
    pin_name = self.PIN_NAME[pin][0]
    if pin_name  not in self.GPIO_PINS:
      print "Error pin " +self.PIN_NAME[pin][1]+" " + str(pin) + " Not Valid"
      assert "Error pin " + str(pin) + "Not Valid"

    else:
      print "Selected pin " + str(pin) + " mode = " + mode
      if mode == self.IN:
        btn = self.app.configureWidget(gui.BUTTON, pin_name, "background", "green")
        btn = self.app.configureWidget(gui.BUTTON, pin_name, "foreground", "black")
      else:
        btn = self.app.configureWidget(gui.BUTTON, pin_name, "background", "paleturquoise")
        btn = self.app.configureWidget(gui.BUTTON, pin_name, "foreground", "black")
        btn = self.app.configureWidget(gui.BUTTON, pin_name, "state", "disabled")

  def output(self, pin, value):
    pin_name = self.PIN_NAME[pin][0]
    print "change " + self.PIN_NAME[pin][1] + " pin " + str(pin) + " value = " + str(value)
    if value == True :
      btn = self.app.configureWidget(gui.BUTTON, pin_name, "background", "deepskyblue")
    else:
      btn = self.app.configureWidget(gui.BUTTON, pin_name, "background", "paleturquoise")

  def cleanup(self):
    print "Clean UP GPIO"
    self.inititialize()


  def setwarnings(selft, flag):
    print "Set Warning " + str(False)

  def press(self,button):
    print button + " Push"

  def run(self):
    self.app.go()

  def __init__(self):
    self.inititialize()

  def inititialize(self):
      self.app = gui("Duxman RPI GPIO EMULATOR")
      font = ("Courier New")
      self.app.setFont(8, font)
      self.app.addButtons(self.PIN_LINE1, self.press)
      self.app.addButtons(self.PIN_LINE2, self.press)

      for o in self.PIN_NAME:
        self.app.setButton(o[0],o[1])


      btn = self.app.configureWidgets(gui.BUTTON,self.GPIO_PINS,"background","palegreen")
      btn = self.app.configureWidgets(gui.BUTTON, self.GPIO_PINS, "foreground", "black")

      btn = self.app.configureWidgets(gui.BUTTON, self.DC_PINS, "background", "darksalmon")
      btn = self.app.configureWidgets(gui.BUTTON, self.DC_PINS, "foreground", "white")
      btn = self.app.configureWidgets(gui.BUTTON, self.DC_PINS, "state", "disabled")

      btn = self.app.configureWidgets(gui.BUTTON, self.GND_PINS, "background", "black")
      btn = self.app.configureWidgets(gui.BUTTON, self.GND_PINS, "foreground", "white")
      btn = self.app.configureWidgets(gui.BUTTON, self.GND_PINS, "state","disabled")


GPIO = DuxmanGpioEmulator()

GPIO.setmode( GPIO.BCM)
GPIO.setup(2,GPIO.OUT)
GPIO.setup(6,GPIO.OUT)
GPIO.setup(4,GPIO.IN)
GPIO.setup(7,GPIO.IN)

GPIO.run()




  
