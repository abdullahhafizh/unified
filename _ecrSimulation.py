__author__ = "wahyudi@multidaya.id"

from time import time
import json
import sys
from _dDevice import _BCAEDC
from _cConfig import _Common


def welcome():
    print("""
            ECR Simulator
        App Ver: """ + _Common.VERSION + """
    Powered By: PT. MultiDaya Dinamika
                -2023-
    """)
    
    
def simulate(amount=100, trxid=''):
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
        exit(1, 'Exception')


def exit(code=0, message='Exit Simulator'):
    print(message+'\n')
    sys.exit(code)


if __name__ == '__main__':
    welcome()
    while True:
        amount = input('Input Amount To Test?\n')
        if int(amount) > 0:
            amount = str(amount)
            break
    simulate(amount)
    exit(code=0)
    