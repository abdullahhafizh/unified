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
        self.set_font('Arial', '', HEADER_FONT_SIZE)
        # Logo
        self.image(LOGO_PATH, 25, 5, 30)
        self.ln(SPACING)
        self.cell(MARGIN_LEFT, HEADER_FONT_SIZE, 'ACQUIRED BY BCA', 0, 0, 'C')
        self.ln(SPACING)
        self.cell(MARGIN_LEFT, HEADER_FONT_SIZE, _Common.KIOSK_NAME, 0, 0, 'C')
        self.ln(SPACING)
        self.cell(MARGIN_LEFT, HEADER_FONT_SIZE, 'KIOSK ID : '+KIOSK_ID, 0, 0, 'C')
        self.ln(SPACING)
        self.cell(MARGIN_LEFT, HEADER_FONT_SIZE, 'JAKARTA', 0, 0, 'C')
        self.ln(SPACING*2)

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


def generate_qr_receipt(data):
    if _Helper.empty(data):
        LOGGER.warning(('EMPTY_RECEIPT_DATA'))
        return
    if 'detail' not in data.keys():
        LOGGER.warning(('EMPTY_QR_DETAIL_DATA'))
        return
    pdf = None
    pdf_file = None
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
        file_name = date_now+'_'+data['trx_reff_no']+'_bca-qris'

        pdf = PDF('P', 'mm', (80, 140))
        # LOGGER.info(('Registering New Font', font_path('UnispaceBold.ttf')))
        # pdf.add_font('Arial', '', font_path('UnispaceBold.ttf'), uni=True)
        pdf.add_page()

        # Layouting
        # pdf.ln(tiny_space)
        # pdf.set_font('Arial', '', default_size)
        # pdf.cell(padding_left, 0, justifying('TID: '+trx['tid'], 'MID: '+trx['mid']), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Arial', '', extra_size)
        pdf.cell(padding_left, 0, 'Issuer: '+trx['transaction_detail']['issuer_name'], 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Arial', '', extra_size)
        pdf.cell(padding_left, 0, 'Acquirer: '+trx['transaction_detail']['acquirer_name'], 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.cell(padding_left, 0, 'Trx ID: '+trx['trx_reff_no'], 0, 0, 'C')
        pdf.ln(large_space)
        pdf.set_font('Arial', '', default_size)
        pdf.cell(padding_left, 0, 'Trx Time: '+data['host_trx_date'], 0, 0, 'L')
        pdf.ln(large_space)
        pdf.set_font('Arial', '', default_size)
        pdf.cell(padding_left, 0, 'Cust. Name: '+trx['transaction_detail']['payer_name'], 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Arial', '', default_size)
        pdf.cell(padding_left, 0, 'Cust. PAN: '+trx['transaction_detail']['customer_pan'], 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Arial', '', default_size)
        pdf.cell(padding_left, 0, 'Cust. Phone: '+trx['transaction_detail']['payer_phone_number'], 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Arial', '', default_size)
        pdf.cell(padding_left, 0, 'Merc. ID: '+trx['transaction_detail']['merchant_info']['merchant_id'], 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Arial', '', default_size)
        pdf.cell(padding_left, 0, 'Merc. PAN: '+trx['transaction_detail']['merchant_info']['merchant_pan'], 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Arial', '', default_size)
        pdf.cell(padding_left, 0, 'Merc. Name: '+trx['transaction_detail']['merchant_info']['name'], 0, 0, 'L')
        pdf.ln(large_space)
        pdf.set_font('Arial', '', default_size)
        _batch = trx['transaction_detail']['batch_number']
        _trace = trx['transaction_detail']['issuer_reference_number']
        pdf.cell(padding_left, 0, justifying('BATCH: '+_batch, 'TRACE: '+_trace), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Arial', '', default_size)
        _reff_no = data['detail']['data']['reference_number']
        _app_code = trx['transaction_detail']['approval_code']
        pdf.cell(padding_left, 0, justifying('REF.NO: '+_reff_no, 'APPR: '+_app_code), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Arial', '', extra_size+2)
        _amount_fee = str(trx['transaction_detail']['convenience_fee'])
        pdf.cell(0, 0, 'FEE   Rp.'+re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', _amount_fee)+'.0', 0, 0, 'C')
        pdf.ln(large_space)
        pdf.set_font('Arial', '', default_size)
        _amount = str(trx['transaction_detail']['amount'])
        pdf.cell(0, 0, 'TOTAL   Rp.'+re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', _amount)+'.0', 0, 0, 'C')
        pdf.ln(large_space)
        pdf.set_font('Arial', '', footer_size)
        pdf.cell(padding_left, 0, '--CUSTOMER COPY--', 0, 0, 'C')
        pdf.ln(tiny_space)
        pdf.set_font('Arial', '', footer_size-1)
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