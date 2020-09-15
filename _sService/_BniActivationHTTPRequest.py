import requests
import json
import time
import binascii

class BniActivationHTTPRequest(object):

    def __init__(self):
        self.url = "http://192.168.9.44:5000/"
        self.reff_no = -1
        self.sequence = 0

    def send_data(self, card_no, data):
        while self.reff_no == -1:
            self.reff_no = self.get_reference_no()
            if self.reff_no == -1: time.sleep(10)
        self.sequence = self.sequence+1 
        if type(data) is bytes or type(data) is bytearray:
            code, re_apdu = self.send_apdu(card_no,self.reff_no,binascii.b2a_hex(data).decode("utf-8"),self.sequence)
        else:
            code, re_apdu = self.send_apdu(card_no,self.reff_no, data,self.sequence)

        if code == 0:
            return re_apdu
        else:
            return "FF"

    # send apdu
    def send_apdu(self, card_no, reff_no, apdu, apdu_no):
        response = requests.post(self.url+'activation/sendapdu',
                                 json={'card_no': card_no,
                                       'reff_no': reff_no, 'apdu': apdu, 'apdu_no': apdu_no})
        code = 1
        data = -1
        if response.status_code == 200:
            data = json.loads(response.text)
            code = data['code']
            if code == 0:
                data = data['result']['re_apdu']
        return code, data

    # close session
    def close_session(self, card_no):
        response = requests.post(self.url+'activation/closesession',
                                 json={'card_no': card_no,
                                       'reff_no': self.reff_no})
        if response.status_code != 200:
            data = -1
        else:
            data = json.loads(response.text)
            data = data['code']
            self.reff_no = -1
        return data

    def get_reference_no(self):
        response = requests.get(url=self.url+'activation/getreferenceno')

        print("Reference number result : " + response.text)

        if response.status_code != 200:
            data = -1
        else:
            data = json.loads(response.text)
            data = data['reff_no']
        return data
