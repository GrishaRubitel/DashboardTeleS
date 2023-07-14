import flask

app = flask.Flask(__name__)


@app.route('/<path:path>')
def send_report(path):
    return flask.send_from_directory('venv', path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
