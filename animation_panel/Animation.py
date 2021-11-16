from PIL import Image  # Use apt-get install python-imaging to install this pip install Pillow


class Animation():

    imagen_file : str
    imagen : Image = None
    imagen_final = None
    width:int=0
    height:int=0

    def loadFile(self):
        try:
            self.imagen = Image.open(self.imagen_file)
            print("Imagen : {0} w = {1} h = {2}".format(self.imagen_file, self.imagen.size[0], self.imagen.size[1]))
        except:
            raise Exception("Image file %s could not be loaded" % self.imagen_file)

    def resizeImagen(self):

        if self.imagen.size[1] != self.height:
            imagen_original = self.imagen.resize((self.imagen.size[0] / (self.imagen.size[1] // self.height), self.height), Image.BICUBIC)
        else:
            imagen_original = self.imagen.copy()

        if imagen_original.size[0] < self.width:
            raise Exception("Picture is too narrow. Must be at least %s pixels wide" % self.width)

        self.imagen_final = Image.new('RGB', (imagen_original.size[0] + self.width, self.height))
        self.imagen_final.paste(imagen_original, (0, 0, imagen_original.size[0], self.height))
        self.imagen_final.paste(imagen_original.crop((0, 0, self.width, self.height)), (imagen_original.size[0], 0, imagen_original.size[0] + self.width, self.height))

        return self.imagen_final

    def __init__(self, fichero, alto, ancho):
        self.imagen_file = fichero
        self.width = ancho
        self.height = alto
        print("Imagen : {0} wp = {1} hp = {2}".format(self.imagen_file, self.width, self.height))

        self.loadFile()
        self.resizeImagen()

