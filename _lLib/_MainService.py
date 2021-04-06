__author__ = "fitrah.wahyudi.imam@gmail.com"

from . import _CPrepaidDLL as dll
from . import _InterfacePrepaidDLL as idll
import json
from flask import Flask, request, jsonify

app = Flask(__name__)
dll.load_dll()
PORT = 5000

@app.route('/')
def hello_world():
    return jsonify({
        'code': 200,
        'message': 'VM Kiosk Topup Service'
    })


@app.route('/ping', methods=['GET'])
def ping_me():
    return 'pong'


@app.route('/send_command', methods=['GET'])
def send_command():
    cmd = request.args.get('cmd')
    param = request.args.get('param')
    response = idll.send_command(cmd, param)
    return jsonify(response)


def start():
    app.run(host='0.0.0.0', port=PORT)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
