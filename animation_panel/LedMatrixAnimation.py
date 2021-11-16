# This is a sample Python script.

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sys

from Animation import Animation
from AnimationServer import AnimationServer
from Config import Config
from Panel import Panel
import glob



class MainClass():

   panel  : Panel = None
   panel_matriz = None
   animation_server: AnimationServer = None
   ficheros = []
   config : Config

   def __init__(self, config: Config):
       self.config = config
       self.panel = Panel(config.ancho, config.alto, config.primer_led, config.panel_ver, config.panel_hor)
       self.animation_server = AnimationServer(self.panel, self.config.velocidad)
       self.panel_matriz = self.panel.calculateMatrix()
       self.buscarFicheros()

   def buscarFicheros(self):
       self.ficheros = glob.glob(self.config.directorio + "/*.png")

   def start(self):
       for imagen in self.ficheros:
           print("preparamos imagen {0}".format(imagen))
           animation = Animation(imagen, self.config.alto*self.config.panel_ver,  self.config.ancho*self.config.panel_hor)
           for i in range(self.config.repeticiones):
               self.animation_server.startAnimation(animation, self.panel)

def main():
    config = Config("configuracion.json")
    main = MainClass(config)
    main.start()

if __name__ == '__main__':
    main()





