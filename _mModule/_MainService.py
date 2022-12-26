__author__ = "wahyudi@multidaya.id"

from _mModule import _CPrepaidDLL as dll
from _mModule import _InterfaceCD as idll
# import json
from flask import Flask, request, jsonify

app = Flask(__name__)
PORT = 5000
LOAD_DLL = False

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
    if LOAD_DLL is True:
        dll.load_dll()
    app.run(host='0.0.0.0', port=PORT)

if __name__ == '__main__':
    if LOAD_DLL is True:
        dll.load_dll()
    app.run(host='0.0.0.0', port=PORT)
