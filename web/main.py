#
# Copyright (c) 2020-2037 duxman.
#
# This file is part of Duxman Luces 
# (see https://github.com/duxman/luces).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import json
import flask
from io import StringIO
from flask import request, render_template
from config import GeneralConfiguration

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.static_folder = 'static'


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/save', methods=['POST'])
def save():
    error = ''
    try:
        Data = request.form['contenido']
        Filename = request.form['filename']
        saveConfigurationJsonFile(Filename, Data)
        return 'OK'
    except Exception as e:
        # flash(e)
        return 'KO'
        
@app.route('/testMusic/<MusicFile>')
def testMusic(MusicFile):
    error = ''
    try:       
        print ("prueba musica")
        executeCommandMusic(MusicFile)
        return 'OK'
    except Exception as e:
        # flash(e)
        return 'KO'


@app.route('/load', methods=['POST'])
def load():
    return 'OK'

def executeCommandMusic(filename):
    self.Logger.info("--------------------<<  INI SUBPROCESO  >>--------------------")
    wd = os.getcwd()
    os.chdir("../")
    p = subprocess.Popen("python PlayMusic.py -i " + filename)    
    os.chdir(wd)   
    self.Logger.info("--------------------<<  FIN SUBPROCESO  >>--------------------")

def saveConfigurationJsonFile(filename, contenido):
    file = open('.' + filename, 'w')
    io = StringIO(contenido)
    data = json.load(io)
    indentstr = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    file.write(indentstr)
    file.close()


if __name__ == '__main__':

    config = GeneralConfiguration()
    #ConfigServer = WebServer()
    #ConfigServer.StartServer()
    app.run(host='0.0.0.0', port=int(config.WebServerPort))

