import json


class Config:
    directorio: str
    repeticiones: int
    ancho: int
    alto: int
    panel_hor: int
    panel_ver: int
    primer_led: str
    velocidad: float
    data: str

    def __init__(self, jsonfile: str):
        self.data =  self.data = json.load(open('./'+jsonfile))
        self.directorio = self.data["directorio"]
        self.repeticiones = self.data["repeticiones"]
        self.ancho = self.data["ancho"]
        self.alto = self.data["alto"]
        self.panel_hor = self.data["panel_hor"]
        self.panel_ver = self.data["panel_ver"]
        self.primer_led = self.data["primer_led"]
        self.velocidad = self.data["velocidad"]