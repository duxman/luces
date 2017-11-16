import cgi
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

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



PORT = 8000



Handler = MiHTTPRequestHandler

httpd = HTTPServer(("", PORT), Handler)

print "serving at port", PORT
httpd.serve_forever()