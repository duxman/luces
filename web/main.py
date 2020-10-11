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


@app.route('/load', methods=['POST'])
def load():
    return 'OK'


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

