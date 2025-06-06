__author__ = 'wahyudi@multidaya.id'

import logging
from fpdf import FPDF
import sys
import os
from datetime import datetime
from _dDevice import _Printer
from _sService import _KioskService
from _cConfig import _ConfigParser, _Common
import re

LOGGER = logging.getLogger()
PDF_PATH = os.path.join(sys.path[0], '_pPDF')
LOGO_PATH = os.path.join(sys.path[0], '_rReceipts', 'bni_logo.gif')
VERSION = _Common.VERSION
KIOSK_ID = _Common.TID
FONT_PATH = os.path.join(os.getcwd(), '_fFonts')

CARD_TYPE = {
    '5484': 'CREDIT CARD',
    '5246': 'CREDIT CARD',
    '5230': 'CREDIT CARD',
    '5240': 'CREDIT CARD',
    '5489': 'CREDIT CARD',
    '5426': 'CREDIT CARD',
    '5241': 'CREDIT CARD',
    '5220': 'CREDIT CARD',
    '5318': 'CREDIT CARD',
    '5184': 'CREDIT CARD',
    '5100': 'CREDIT CARD',
    '5176': 'CREDIT CARD',
    '5226': 'CREDIT CARD',
    '2221': 'CREDIT CARD',
    '4105': 'CREDIT CARD',
    '4512': 'CREDIT CARD',
    '4712': 'CREDIT CARD',
    '4665': 'CREDIT CARD',
    '4575': 'CREDIT CARD',
    '4365': 'CREDIT CARD',
    '4390': 'CREDIT CARD',
    '4260': 'CREDIT CARD',
    '4035': 'CREDIT CARD',
    '4506': 'CREDIT CARD',
    '4507': 'CREDIT CARD',
    '3565': 'CREDIT CARD',
    '3563': 'CREDIT CARD',
    '3500': 'CREDIT CARD',
    '1946': 'DEBIT CARD',
    '5264': 'DEBIT CARD',
    '5371': 'DEBIT CARD',
    '5198': 'DEBIT CARD',
    '5326': 'DEBIT CARD',
    '5178': 'DEBIT CARD',
    '5269': 'DEBIT CARD',
    '5287': 'DEBIT CARD',
    '5327': 'DEBIT CARD',
    '5210': 'DEBIT CARD',
    '5054': 'DEBIT CARD',
    '6010': 'DEBIT CARD',
    '4893': 'DEBIT CARD',
    '4626': 'DEBIT CARD',
    '4640': 'DEBIT CARD',
    '5893': 'DEBIT CARD',
    '4712*': 'DEBIT CARD',
    '5898': 'DEBIT CARD',
    '4760': 'DEBIT CARD',
    '4214': 'DEBIT CARD',
    '5576': 'DEBIT CARD',
    '5211': 'DEBIT CARD',
    '5327*': 'DEBIT CARD',
    '6666': 'DEBIT CARD',
    '5366': 'DEBIT CARD',
    '5376': 'DEBIT CARD',
    '5174': 'DEBIT CARD',
    '5472': 'DEBIT CARD',
    '5304': 'DEBIT CARD',
    '5221': 'DEBIT CARD',
    '5326*': 'DEBIT CARD',
    '6013': 'DEBIT CARD',
    '4616': 'DEBIT CARD',
    '4097': 'DEBIT CARD',
    '4617': 'DEBIT CARD',
    '6032': 'DEBIT CARD',
    '4837': 'DEBIT CARD',
    '6019': 'DEBIT CARD',
    '6276': 'DEBIT CARD',
    '6271': 'DEBIT CARD',
    '6277': 'DEBIT CARD',
    '3571': 'DEBIT CARD',
    '5047': 'DEBIT CARD',
    '4158': 'DEBIT CARD',
    '5297': 'DEBIT CARD',
    '5049': 'DEBIT CARD',
    '5069': 'DEBIT CARD',
    '5058': 'DEBIT CARD',
    '4215': 'DEBIT CARD',
    '6221': 'DEBIT CARD',
    '4854': 'DEBIT CARD',
    '4693': 'DEBIT CARD',
    '6220': 'DEBIT CARD',
    '4620': 'DEBIT CARD',
    '6013*': 'DEBIT CARD',
    '5376*': 'DEBIT CARD',
    '4617*': 'DEBIT CARD',
    '5104': 'DEBIT CARD',
    '5318*': 'DEBIT CARD',
    '5597': 'DEBIT CARD',
    '4214*': 'DEBIT CARD',
    '5058*': 'DEBIT CARD',
    '4847': 'DEBIT CARD',
    '6214': 'DEBIT CARD',
    '5577': 'DEBIT CARD',
    '4135': 'DEBIT CARD',
    '4706': 'DEBIT CARD',
    '6274': 'DEBIT CARD',
    '4416': 'CREDIT CARD',
    '5336': 'CREDIT CARD',
}


def get_type(card_no):
    card_type = 'CREDIT CARD'
    try:
        card_type = CARD_TYPE[card_no[:4]]
        # LOGGER.info(('Card Type Found!', card_no, card_type))
    except (KeyError, ValueError, IndexError):
        LOGGER.warning(('Card Type Not Found!', card_no))
    finally:
        return card_type


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
        self.cell(MARGIN_LEFT, HEADER_FONT_SIZE, 'ACQUIRED BY BNI', 0, 0, 'C')
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


def generate_edc_receipt_old(trx):
    pdf = None

    # Init Variables
    large_space = 9
    tiny_space = 4.5
    default_size = 9
    extra_size = 15
    line_size = 10
    padding_left = -10

    try:
        time_text = datetime.strptime(trx['trans_date'], '%Y%m%d%H%M%S').strftime('%H:%M:%S')
        date_text = datetime.strptime(trx['trans_date'], '%Y%m%d%H%M%S').strftime('%d %b %Y')
        date_now = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
        file_name = date_now+'_'+trx['card_no'].replace('*', 'X')+'_'+trx['app_code']+'_'+trx['inv_no']

        pdf = PDF('P', 'mm', (80, 140))
        pdf.add_page()

        # Layouting
        pdf.ln(tiny_space)
        pdf.set_font('Courier', 'B', default_size)
        pdf.cell(padding_left, 0, 'MID   : '+trx['mid'], 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.cell(padding_left, 0, 'TID   : '+trx['tid'], 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.cell(padding_left, 0, 'TRXID : '+trx['struck_id'], 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Courier', 'B', line_size)
        pdf.cell(padding_left, 0, '==============================', 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Courier', '', default_size)
        pdf.cell(padding_left, 0, 'APP VERSION '+VERSION.replace('VER:', ''), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Courier', '', default_size)
        pdf.cell(padding_left, 0, 'EMV OTHER', 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Courier', 'B', extra_size)
        pdf.cell(padding_left, 0, 'SALE', 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Courier', 'B', default_size)
        pdf.cell(padding_left, 0, trx['card_type']+' BNI46', 0, 0, 'L')
        pdf.ln(large_space)
        pdf.set_font('Courier', 'B', extra_size)
        pdf.cell(padding_left, 0, trx['card_no'], 0, 0, 'L')
        pdf.ln(large_space)
        pdf.set_font('Courier', 'B', default_size)
        pdf.cell(padding_left, 0, 'TRACE    : '+trx['inv_no'], 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.cell(padding_left, 0, 'BATCH    : '+trx['batch_no'], 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Courier', 'B', default_size)
        pdf.cell(padding_left, 0, 'DATE     : '+date_text, 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.cell(padding_left, 0, 'TIME     : '+time_text, 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Courier', 'B', default_size)
        pdf.cell(padding_left, 0, 'REF. NO  : '+trx['ref_no'], 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.cell(padding_left, 0, 'APROVAL  : '+trx['app_code'], 0, 0, 'L')
        pdf.ln(large_space)
        pdf.set_font('Courier', 'B', extra_size)
        pdf.cell(0, 0, 'TOTAL   Rp.'+re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', trx['amount']), 0, 0, 'C')
        pdf.ln(tiny_space)

        # Rendering
        pdf_file = get_path(file_name+'.pdf')
        pdf.output(pdf_file, 'F')
        _Common.LAST_EDC_TRX_RECEIPT = pdf_file
        LOGGER.debug((file_name))
    except Exception as e:
        LOGGER.warning(str(e))
    finally:
        if not _Common.EDC_PRINT_ON_LAST:
            print_ = _Printer.do_printout(_Common.LAST_EDC_TRX_RECEIPT)
            print("pyt : sending edc_receipt to printer : {}".format(str(print_)))
        del pdf


def generate_edc_receipt(trx):
    pdf = None

    # Init Variables
    large_space = 8
    tiny_space = 3.5

    default_size = 8
    extra_size = 10
    footer_size = 6

    padding_left = 0

    try:
        # trans_date must have format = 20161003125804
        time_text = datetime.strptime(trx['trans_date'], '%Y%m%d%H%M%S').strftime('%H:%M:%S')
        date_text = datetime.strptime(trx['trans_date'], '%Y%m%d%H%M%S').strftime('%d %b %Y')
        date_now = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
        file_name = date_now+'_'+trx['card_no'].replace('*', 'X')+'_'+trx['app_code']+'_'+trx['inv_no']

        pdf = PDF('P', 'mm', (80, 140))
        # LOGGER.info(('Registering New Font', font_path('UnispaceBold.ttf')))
        # pdf.add_font('Arial', '', font_path('UnispaceBold.ttf'), uni=True)
        pdf.add_page()

        # Layouting
        pdf.ln(tiny_space)
        pdf.set_font('Arial', '', default_size)
        pdf.cell(padding_left, 0, justifying('TID: '+trx['tid'], 'MID: '+trx['mid']), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.cell(padding_left, 0, 'TRXID: '+trx['struck_id'], 0, 0, 'C')
        pdf.ln(large_space)
        pdf.set_font('Arial', '', default_size)
        pdf.cell(padding_left, 0, justifying('DATE: '+date_text, 'TIME: '+time_text), 0, 0, 'L')
        pdf.ln(large_space)
        pdf.set_font('Arial', '', default_size)
        pdf.cell(padding_left, 0, 'EMV OTHER', 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Arial', '', extra_size)
        pdf.cell(padding_left, 0, 'SALE', 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Arial', '', default_size)
        pdf.cell(padding_left, 0, trx['card_type'], 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Arial', 'B', extra_size+2)
        pdf.cell(padding_left, 0, trx['card_no'], 0, 0, 'L')
        pdf.ln(large_space)
        pdf.set_font('Arial', '', default_size)
        _batch = trx['batch_no'].replace(' ', '')
        pdf.cell(padding_left, 0, justifying('BATCH: '+_batch, 'TRACE: '+trx['trace_no']), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font('Arial', '', default_size)
        pdf.cell(padding_left, 0, justifying('REF.NO: '+trx['bank_reff_no'].zfill(12), 'APPR: '+trx['app_code']), 0, 0, 'L')
        pdf.ln(large_space)
        pdf.set_font('Arial', 'B', extra_size+2)
        pdf.cell(0, 0, 'TOTAL   Rp.'+re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', trx['amount']), 0, 0, 'C')
        pdf.ln(large_space)
        pdf.set_font('Arial', '', footer_size)
        pdf.cell(padding_left, 0, 'I AGREE TO PAY ABOVE TOTAL AMOUNT', 0, 0, 'C')
        pdf.ln(tiny_space)
        pdf.set_font('Arial', '', footer_size)
        pdf.cell(padding_left, 0, 'ACCORDING TO CARD ISSUER AGREEMENT', 0, 0, 'C')
        pdf.ln(tiny_space)
        pdf.set_font('Arial', '', footer_size)
        pdf.cell(padding_left, 0, '***PIN VERIFICATION SUCCESS***', 0, 0, 'C')
        pdf.ln(tiny_space)
        pdf.set_font('Arial', '', footer_size)
        pdf.cell(padding_left, 0, '***NO SIGNATURE REQUIRED***', 0, 0, 'C')
        pdf.ln(tiny_space)
        pdf.set_font('Arial', '', footer_size)
        pdf.cell(padding_left, 0, '--CUSTOMER COPY--', 0, 0, 'C')
        pdf.ln(tiny_space)
        pdf.set_font('Arial', '', footer_size-1)
        pdf.cell(padding_left, 0, 'APP VER: '+VERSION.replace('VER:', ''), 0, 0, 'L')

        # Rendering
        pdf_file = get_path(file_name+'.pdf')
        pdf.output(pdf_file, 'F')
        _Common.LAST_EDC_TRX_RECEIPT = pdf_file
        LOGGER.debug((file_name))
    except Exception as e:
        LOGGER.warning(str(e))
    finally:
        if not _Common.EDC_PRINT_ON_LAST:
            print_ = _Printer.do_printout(_Common.LAST_EDC_TRX_RECEIPT)
            print("pyt : sending edc_receipt to printer : {}".format(str(print_)))
        del pdf
