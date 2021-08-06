__author__ = 'fitrah.wahyudi.imam@gmail.com'

import logging
from fpdf import FPDF
import sys
import os
from datetime import datetime
from _dDevice import _Printer
from _sService import _KioskService
from _cConfig import _ConfigParser, _Common
import re
from _tTools import _Helper

LOGGER = logging.getLogger()
PDF_PATH = os.path.join(sys.path[0], '_pPDF')
LOGO_PATH = os.path.join(sys.path[0], '_tTools', 'qris_logo.gif')
VERSION = _Common.VERSION
KIOSK_ID = _Common.TID
FONT_PATH = os.path.join(os.getcwd(), '_fFonts')


def get_path(file):
    return os.path.join(PDF_PATH, file)


def font_path(font):
    return os.path.join(FONT_PATH, font)


MAX_LENGTH = 36


def justifying(left, right):
    return left + (" " * (MAX_LENGTH-len(left)-len(right))) + right


MARGIN_LEFT = 0
HEADER_FONT_SIZE = 8
SPACING = 2.5
DEFAULT_FONT_SIZE = 6


class PDF(FPDF):
    def header(self):
        self.set_font('Courier', '', HEADER_FONT_SIZE)
        # Logo
        if os.path.isfile(LOGO_PATH):
            # self.image(name=LOGO_PATH, x=None, y=None, w=100, h=60, type='GIF')
            self.image(LOGO_PATH, 25, 20, 30)
            self.ln(SPACING*5)
        self.cell(MARGIN_LEFT, HEADER_FONT_SIZE, ' - ', 0, 0, 'C')
        self.ln(SPACING)
        self.cell(MARGIN_LEFT, HEADER_FONT_SIZE, _Common.KIOSK_NAME + ' - ' + KIOSK_ID, 0, 0, 'C')
        self.ln(SPACING)

    # def footer(self):
    #     self.set_font('Courier', '', DEFAULT_FONT_SIZE)
    #     self.set_y(-25)
    #     self.cell(MARGIN_LEFT, DEFAULT_FONT_SIZE, '***PIN VERIFICATION SUCCESS***', 0, 0, 'C')
    #     self.ln(SPACING)
    #     self.cell(MARGIN_LEFT, DEFAULT_FONT_SIZE, 'NO SIGNATURE REQUIRED', 0, 0, 'C')
    #     self.ln(SPACING)
    #     self.cell(MARGIN_LEFT, DEFAULT_FONT_SIZE, 'I AGREE TO PAY ABOVE TOTAL AMOUNT', 0, 0, 'C')
    #     self.ln(SPACING)
    #     self.cell(MARGIN_LEFT, DEFAULT_FONT_SIZE, 'ACCORDING TO CARD ISSUER AGREEMENT', 0, 0, 'C')
    #     self.ln(SPACING)
    #     self.cell(MARGIN_LEFT, HEADER_FONT_SIZE, '--CUSTOMER COPY--', 0, 0, 'C')


DUMMY_QR_DATA = {
        "provider": "QRIS BCA",
        "tid": "17092001",
        "mid": "000972721511382bf739669cce165808",
        "trx_id": "VVD000202102231214208633",
        "amount": 500,
        "status": "SUCCESS",
        "host_trx_date": "11-Aug-2020 11:25:34",
        "detail": {
            "status": "success",
            "reason": "Transaction success",
            "data": {
                "reference_number": "022411000106",
                "transaction_date": "11-Aug-2020 11:25:34",
                "transaction_status": "success",
                "transaction_id": "2dd1ee0c-0255-3bd8-a4b4276a17ab7cf"
            },
            "transaction_detail": {
                "amount": 15000,
                "currency_code": "IDR",
                "approval_code": "ATTRT0",
                "batch_number": "000004",
                "convenience_fee": 0,
                "issuer_reference_number": "000013101",
                "customer_pan": "9360001430000131018",
                "issuer_name": "BCA",
                "acquirer_name": "BCA",
                "merchant_info": {
                    "city": "JAKARTA PUSAT",
                    "country": "ID",
                    "email": "null",
                    "merchant_id": "00088500033345",
                    "merchant_pan": "9360001430003334569",
                    "name": "FDM DUMMY MAGENTA TOKO",
                    "payment_channel_name": "Sakuku",
                    "postal_code": "10310",
                    "terminal_id": "DTESTDRA"
                },
                "payer_name": "DEV Apos",
                "payer_phone_number": "08174964450"
            }
        }
    }

DUMMY_QR_DATA_BNI = {
   "host_trx_date":"2021-08-06T15:50:45",
   "detail":{
      "customer_name":"Fadlian",
      "merchant_id":"008800223497",
      "merchant_name":"Sukses Makmur Bendungan Hilir",
      "merchant_city":"Jakarta Pusat",
      "currency_code":"360",
      "bill_number":"12345678901234567890",
      "code":"00",
      "merchant_pan":"9360001316000000032",
      "transaction_datetime":"2021-02-25T13:36:13",
      "payment_description":"Payment Success",
      "mcc":"5814",
      "amount":10000,
      "issuer_code":"93600013",
      "message":"success",
      "customer_pan":" 9360001110000000019",
      "terminal_id":"00005771",
      "payment_status":"00",
      "stan":"210226",
      "amount_fee":1000,
      "request_id":"XwVjF5zfuHhrDZuw",
      "approval_code":"00",
      "merchant_country":"ID",
      "rrn":"123456789012"
   },
   "reff_no":"shop1628239813483124",
   "amount":10000,
   "status":"PAID",
   "trx_reff_no":"shop1628239813483124-17092001",
   "provider":"QRIS BNI",
   "trx_id":"MVM000202108061550131348",
   "mid":"000972721511382bf739669cce165808",
   "tid":"17092001"
}


def normalize_details_data(data, source='bni-qris'):
    # Issue Index Found Here
    if source == 'bni-qris':
        data['trx_reff_no'] = data['reff_no']
        data['detail']['data'] = []
        data['detail']['transaction_detail'] = []
        data['detail']['data']['reference_number'] = data['detail']['bill_number']
        data['detail']['transaction_detail']['payer_name'] = data['detail']['customer_name']
        data['detail']['transaction_detail']['customer_pan'] = data['detail']['customer_pan']
        data['detail']['transaction_detail']['payer_phone_number'] = 'N/A'
        data['detail']['transaction_detail']['merchant_info']['merchant_id'] = data['detail']['merchant_id']
        data['detail']['transaction_detail']['merchant_info']['merchant_pan'] = data['detail']['merchant_pan']
        data['detail']['transaction_detail']['merchant_info']['name'] = data['detail']['merchant_name']
        data['detail']['transaction_detail']['batch_number'] = data['detail']['stan']
        data['detail']['transaction_detail']['issuer_reference_number'] = data['detail']['rrn']
        data['detail']['transaction_detail']['approval_code'] = data['detail']['approval_code']
        data['detail']['transaction_detail']['issuer_name'] = data['detail']['issuer_code']
        data['detail']['transaction_detail']['acquirer_name'] = data['detail']['merchant_pan'][:9]
        data['detail']['transaction_detail']['convenience_fee'] = data['detail']['amount_fee']
        data['detail']['transaction_detail']['amount'] = data['detail']['amount']
        return data        
    else:
        return data


def generate_qr_receipt(data, mode='bca-qris'):
    if _Helper.empty(data):
        LOGGER.warning(('EMPTY_RECEIPT_DATA', str(data)))
        return
    if 'detail' not in data.keys():
        LOGGER.warning(('EMPTY_QR_DETAIL_DATA', str(data)))
        return
    pdf = None
    pdf_file = None
    data = normalize_details_data(data, mode)
    trx = data['detail']

    # Init Variables
    large_space = 8
    tiny_space = 3.5
    default_size = 8
    extra_size = 10
    footer_size = 6
    padding_left = 0

    try:
        # trans_date must have format = 20161003125804
        date_now = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
        file_name = date_now+'_'+data['trx_reff_no']+'_'+mode

        pdf = PDF('P', 'mm', (80, 140))
        # LOGGER.info(('Registering New Font', font_path('UnispaceBold.ttf')))
        # pdf.add_font('Courier', '', font_path('UnispaceBold.ttf'), uni=True)
        pdf.add_page()
        # Layouting
        # pdf.ln(tiny_space)
        # pdf.set_font('Courier', '', default_size)
        # pdf.cell(padding_left, 0, justifying('TID: '+trx['tid'], 'MID: '+trx['mid']), 0, 0, 'L')
        pdf.ln(large_space)
        pdf.set_font('Courier', '', default_size)
        _trx_id = data['trx_reff_no'].split('-')[0]
        pdf.cell(padding_left, 0, 'Trx ID: '+_trx_id, 0, 0, 'l')
        pdf.ln(tiny_space)
        pdf.set_font('Courier', '', default_size)
        pdf.cell(padding_left, 0, 'Trx Time: '+data['host_trx_date'], 0, 0, 'L')
        pdf.ln(5)
        pdf.set_font('Courier', '', default_size)
        pdf.cell(padding_left, 0, 'Cust. Name: '+trx['transaction_detail']['payer_name'], 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Courier', '', default_size)
        pdf.cell(padding_left, 0, 'Cust. PAN: '+trx['transaction_detail']['customer_pan'], 0, 0, 'L')
        pdf.ln(tiny_space)
        if mode == 'bca-qris':
            pdf.set_font('Courier', '', default_size)
            pdf.cell(padding_left, 0, 'Cust. Phone: '+trx['transaction_detail']['payer_phone_number'], 0, 0, 'L')
            pdf.ln(tiny_space)
        pdf.set_font('Courier', '', default_size)
        pdf.cell(padding_left, 0, 'Merc. ID: '+trx['transaction_detail']['merchant_info']['merchant_id'], 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Courier', '', default_size)
        pdf.cell(padding_left, 0, 'Merc. PAN: '+trx['transaction_detail']['merchant_info']['merchant_pan'], 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Courier', '', default_size)
        pdf.cell(padding_left, 0, 'Merc. Name: '+trx['transaction_detail']['merchant_info']['name'], 0, 0, 'L')
        pdf.ln(5)
        pdf.set_font('Courier', '', default_size)
        _batch = trx['transaction_detail']['batch_number']
        _rrn = trx['transaction_detail']['issuer_reference_number']
        pdf.cell(padding_left, 0, justifying('BATCH: '+_batch, 'RRN QRIS: '+_rrn), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Courier', '', default_size)
        _reff_no = data['detail']['data']['reference_number']
        _app_code = trx['transaction_detail']['approval_code']
        pdf.cell(padding_left, 0, justifying('REF.NO: '+_reff_no, 'APPR: '+_app_code), 0, 0, 'L')
        pdf.ln(tiny_space)
        _issuer = trx['transaction_detail']['issuer_name']
        _acquirer = trx['transaction_detail']['acquirer_name']
        pdf.cell(padding_left, 0, justifying('ISSUER: '+_issuer, 'ACQUIRER: '+_acquirer), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Courier', '', default_size)
        _amount_fee = str(trx['transaction_detail']['convenience_fee'])
        pdf.cell(0, 0, 'FEE   Rp.'+re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', _amount_fee)+'.0', 0, 0, 'C')
        pdf.ln(tiny_space)
        pdf.set_font('Courier', '', extra_size+2)
        _amount = str(trx['transaction_detail']['amount'])
        pdf.cell(0, 0, 'TOTAL   Rp.'+re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', _amount)+'.0', 0, 0, 'C')
        pdf.ln(tiny_space)
        pdf.set_font('Courier', '', footer_size-1)
        pdf.cell(padding_left, 0, 'APP VER: '+VERSION.replace('VER:', ''), 0, 0, 'L')
        # Rendering
        pdf_file = get_path(file_name+'.pdf')
        pdf.output(pdf_file, 'F')
        LOGGER.debug((file_name))
    except Exception as e:
        LOGGER.warning(str(e))
    finally:
        if pdf_file is not None:
            print_ = _Printer.do_printout(pdf_file)
            print("pyt : sending qr_receipt to printer : {}".format(str(print_)))
        del pdf
        del trx
        del data