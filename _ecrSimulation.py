__author__ = "wahyudi@multidaya.id"

from time import time
import json
import sys, traceback
from _dDevice import _BCAEDC
from _cConfig import _Common


def welcome():
    print("""
            ECR Simulator
        App Ver: """ + _Common.VERSION + """
    Powered By: PT. MultiDaya Dinamika
                -2023-
    """)
    
    
def simulate_trx(amount=100, trxid=''):
    result = None
    sale_data = None
    edc_ecr = _BCAEDC.BCAEDC()
    trxid = ''.join(['SIM', str(time())])
    try:
        if edc_ecr.connect(_Common.EDC_PORT):
            amount = amount.replace('.00', '')
            result, sale_data = edc_ecr.do_payment(trxid, amount)
            print('Result -> ', result)
            print('Data -> ', json.dumps(sale_data))
        else:
            print('ECR Not Connect', _Common.EDC_PORT)
            exit(1, 'Failed')
    except Exception as e:
        print('ECR Exception', str(e))
        trace = traceback.format_exc()
        exit(1, trace)
        

def simulate_echo():
    result = None
    output = None
    edc_ecr = _BCAEDC.BCAEDC()
    try:
        if edc_ecr.connect(_Common.EDC_PORT):
            result, output = edc_ecr.echo_test()
            print('Result -> ', result)
            print('Data -> ', json.dumps(output))
        else:
            print('ECR Not Connect', _Common.EDC_PORT)
            exit(1, 'Failed')
    except Exception as e:
        print('ECR Exception', str(e))
        trace = traceback.format_exc()
        exit(1, trace)
        

def simulate_info():
    result = None
    output = None
    edc_ecr = _BCAEDC.BCAEDC()
    try:
        if edc_ecr.connect(_Common.EDC_PORT):
            result, output = edc_ecr.card_info()
            print('Result -> ', result)
            print('Data -> ', json.dumps(output))
        else:
            print('ECR Not Connect', _Common.EDC_PORT)
            exit(1, 'Failed')
    except Exception as e:
        print('ECR Exception', str(e))
        trace = traceback.format_exc()
        exit(1, trace)


def exit(code=0, message='Exit Simulator'):
    print(message+'\n')
    sys.exit(code)


if __name__ == '__main__':
    welcome()
    mode = ''
    while True:
        mode = input('Pilih Mode ECR Berikut (Pilih Nomor)?\n1 - Simulate Transaction\n2 - Echo Test\n3 - Card Information\nX - Exit\n\nInput :')
        if mode in ['1', '2', '3']:
            break
        elif mode in ['x', 'X']:
            break
    if mode in ['1', '2', '3']:
        if mode == '1':
            while True:
                amount = input('Input Amount To Test?\n')
                if int(amount) > 0:
                    amount = str(amount)
                    break
            simulate_trx(amount)
        elif mode == '2':
            simulate_echo()
        elif mode == '3':
            simulate_info()
    exit(code=0)
    