import cgi
import json
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from json import JSONEncoder
from multiprocessing import Pool

import thread
from threading import Thread

from Util import logger


class MiHTTPRequestHandler(SimpleHTTPRequestHandler):

    def do_POST(self):
        # CITATION: http://stackoverflow.com/questions/4233218/python-basehttprequesthandler-post-variables
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}

        filename = postvars['filename'][0]
        contenido = postvars['contenido'][0]
        type = postvars["type"][0]
        if type == 'PROGRAMACION':
            self.saveProgramacion(filename, contenido)
        elif type == "GENERAL":
            self.saveConfiguracion(self, filename, contenido)
        elif type == "SECUENCIA":
            self.saveSecuencia( contenido)

        return self.do_GET()

    def saveSecuencia(self,contenido):
        data = json.loads(contenido)
        dataout = []
        i = 0
        for secuencia in data:
            i = i +1
            secuencia["Nombre"] = "led"+str(i)
            dataout.append(secuencia)

        dataencoded = JSONEncoder().encode(dataout)

        file = open('./config/leds.json', 'wb')
        file.write(dataencoded)
        file.close()

    def saveProgramacion(self, filename,contenido):
        file = open('./config/' + filename, 'wb')
        file.write(contenido)
        file.close()
    def saveConfiguracion(self, filename,contenido):
        file = open('./config/' + filename, 'wb')
        file.write(contenido)
        file.close()


class WebServer():
    PORT = 8000
    Handler = None
    HttpdServer = None
    Logger = None

    def StopServer(self):
        try:
            self.HttpdServer.shutdown()
            self.HttpdServer.socket.close()
            self.HttpdServer.join()
            self.HttpdServer, self.HttpdServer = None, None
        except Exception as error:
            pass  # catch and raise which ever errors you desire here

    def StartServer(self):
        self.server_thread = Thread(target=self.HttpdServer.serve_forever)
        self.server_thread.start()

    def __init__(self, port):
        self.PORT = port
        self.Logger = logger.clienteLog.logger

        self.Handler = MiHTTPRequestHandler
        self.HttpdServer = HTTPServer(("", self.PORT), self.Handler)
        self.Logger.info( "serving at port" + str(self.PORT))

