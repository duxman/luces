import cgi
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import ThreadingMixIn


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
        if filename:
            file = open('./config/' + filename, 'wb')
            file.write(contenido)
            file.close()
        return self.do_GET()


class WebServer(ThreadingMixIn):
    PORT = 8000
    Handler = None
    HttpdServer = None
    Logger = None

    def __init__(self, port, logger):
        self.PORT = 8000
        self.Logger = logger
        self.Handler = MiHTTPRequestHandler
        self.HttpdServer = HTTPServer(("", self.PORT), self.Handler)
        self.Logger.info( "serving at port" + str(self.PORT))
        self.HttpdServer.serve_forever()