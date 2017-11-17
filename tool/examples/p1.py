import sys
import time
from appJar.appjar import gui

pinLinea1 = ["GPIO01","GPIO02","GPIO03","GPIO04","GPIO05","GPIO06","GPIO07","GPIO08","GPIO09","GPIO10","GPIO11","GPIO12","GPIO13","GPIO14","GPIO15","GPIO16","GPIO17","GPIO18","GPIO19","GPIO20"]
pinLinea2 = ["GPIO21","GPIO22","GPIO23","GPIO24","GPIO25","GPIO26","GPIO27","GPIO28","GPIO29","GPIO30","GPIO31","GPIO32","GPIO33","GPIO34","GPIO35","GPIO36","GPIO37","GPIO38","GPIO39","GPIO40"]
def press(button):
  print button

with gui("PRUEBA") as app:
  font = ("Courier New")
  app.setFont(8, font)
  app.addButtons(pinLinea1, press)
  app.addButtons(pinLinea2, press)
  app.go()
  
  
