__author__ = 'fitrah.wahyudi.imam@gmail.com'

import logging
from fpdf import FPDF
import sys
import os
import json
from datetime import datetime
from _tTools import _Helper
from PyQt5.QtCore import QObject, pyqtSignal
from _dDevice import _Printer, _BILL
from _sService import _KioskService
from _nNetwork import _NetworkAccess
from _cConfig import _Common
from _sService import _UserService
from _sService import _ProductService
from _dDAO import _DAO
from time import sleep
import re

LOGGER = logging.getLogger()


class SPrintToolSignalHandler(QObject):
    __qualname__ = 'SPrintToolSignalHandler'
    SIGNAL_SALE_START_GENERATE = pyqtSignal(str)
    SIGNAL_SALE_PRINT_GLOBAL = pyqtSignal(str)
    SIGNAL_SALE_REPRINT_GLOBAL = pyqtSignal(str)
    SIGNAL_ADMIN_PRINT_GLOBAL = pyqtSignal(str)


SPRINTTOOL_SIGNDLER = SPrintToolSignalHandler()
PATH = os.path.join(sys.path[0], '_pPDF')
if not os.path.exists(PATH):
    os.makedirs(PATH)
FONT_PATH = os.path.join(sys.path[0], '_fFonts')
if not os.path.exists(FONT_PATH):
    os.makedirs(FONT_PATH)
LOGO_PATH = os.path.join(sys.path[0], '_rReceipts', _Common.RECEIPT_LOGO)
ERECEIPT_PATH = os.path.join(sys.path[0], '_rReceipts', '_jJson')
if not os.path.exists(ERECEIPT_PATH):
    os.makedirs(ERECEIPT_PATH)


def get_paper_size(ls=None):
    p = {'WIDTH': 80, 'HEIGHT': 80}
    if ls is not None:
        ls = ls.split('\r\n')
        p['HEIGHT'] = p['WIDTH'] + (3.5 * len(ls))
    return p


MARGIN_LEFT = 0
SPACING = 3.5
USED_FONT = 'Courier'
GLOBAL_FONT_SIZE = 7.5
RECEIPT_TITLE = 'SALE GLOBAL PRINT'
HEADER_TEXT1 = 'ISI ULANG'
HEADER_TEXT2 = 'MANDIRI E-MONEY'


class PDF(FPDF):
    def header(self):
        # Logo
        if os.path.isfile(LOGO_PATH):
            # self.image(name=LOGO_PATH, x=None, y=None, w=100, h=60, type='GIF')
            self.image(LOGO_PATH, 25, 20, 30)
            self.ln(SPACING*4)
        self.set_font(USED_FONT, '', GLOBAL_FONT_SIZE)
        self.ln(SPACING*4)
        self.cell(MARGIN_LEFT, GLOBAL_FONT_SIZE, 'TERMINAL : '+_Common.TID, 0, 0, 'C')
        self.ln(SPACING)
        self.cell(MARGIN_LEFT, GLOBAL_FONT_SIZE, 'LOKASI : '+_Common.KIOSK_NAME, 0, 1, 'C')

    def footer(self):
        self.set_font(USED_FONT, '', GLOBAL_FONT_SIZE-1)
        # self.ln(SPACING)
        # self.cell(MARGIN_LEFT, HEADER_FONT_SIZE, 'Layanan Pelanggan Hubungi 0812-XXXX-XXXX', 0, 0, 'C')
        # self.cell(MARGIN_LEFT, FOOTER_FONT_SIZE, '-APP VER: ' + _KioskService.VERSION+'-', 0, 0, 'C')
        self.set_y(-20)
        if len(_Common.CUSTOM_RECEIPT_TEXT) > 5:
            for custom_text in _Common.CUSTOM_RECEIPT_TEXT.split('|'):
                self.ln(SPACING-1)
                self.cell(MARGIN_LEFT, GLOBAL_FONT_SIZE-1, custom_text, 0, 0, 'C')
        self.ln(SPACING-1)
        self.cell(MARGIN_LEFT, GLOBAL_FONT_SIZE-1, 'TERIMA KASIH', 0, 0, 'C')


class NEW_LAYOUT_PDF(FPDF):
    def header(self):
        # Logo
        if os.path.isfile(LOGO_PATH):
            # self.image(name=LOGO_PATH, x=None, y=None, w=100, h=60, type='GIF')
            self.image(LOGO_PATH, 25, 20, 30)
            self.ln(SPACING*5)
        self.set_font(USED_FONT, '', GLOBAL_FONT_SIZE)
        self.ln(SPACING*3)
        self.cell(MARGIN_LEFT, GLOBAL_FONT_SIZE, 'TERMINAL : '+_Common.TID, 0, 0, 'C')
        self.ln(SPACING)
        self.cell(MARGIN_LEFT, GLOBAL_FONT_SIZE, 'LOKASI : '+_Common.KIOSK_NAME, 0, 1, 'C')

    # def footer(self):
        # self.set_font(USED_FONT, '', GLOBAL_FONT_SIZE-1)
        # self.ln(SPACING)
        # self.cell(MARGIN_LEFT, HEADER_FONT_SIZE, 'Layanan Pelanggan Hubungi 0812-XXXX-XXXX', 0, 0, 'C')
        # self.cell(MARGIN_LEFT, FOOTER_FONT_SIZE, '-APP VER: ' + _KioskService.VERSION+'-', 0, 0, 'C')
        # self.set_y(-5)
        # if len(_Common.CUSTOM_RECEIPT_TEXT) > 5:
        #     for custom_text in _Common.CUSTOM_RECEIPT_TEXT.split('|'):
        #         self.ln(SPACING-1)
        #         self.cell(MARGIN_LEFT, GLOBAL_FONT_SIZE-1, custom_text, 0, 0, 'C')
        # self.cell(MARGIN_LEFT, GLOBAL_FONT_SIZE-1, 'TERIMA KASIH', 0, 0, 'C')


GENERAL_TITLE = 'VM COLLECTION REPORT'
USE_FOOTER = False

class GeneralPDF(FPDF):
    def header(self):
        self.set_font(USED_FONT, '', 7)
        self.ln(3*3)
        self.cell(MARGIN_LEFT, 7, GENERAL_TITLE, 0, 0, 'C')
        self.ln(3)
        self.cell(MARGIN_LEFT, 7, 'VM ID : '+_Common.TID, 0, 0, 'C')
        self.ln(3)
        self.cell(MARGIN_LEFT, 7, 'VM Name : '+_Common.KIOSK_NAME, 0, 1, 'C')

    def footer(self):
        if USE_FOOTER is True:
            self.set_font(USED_FONT, '', 7)
            self.set_y(-20)
            self.cell(MARGIN_LEFT, 7, '(TTD Korlap)   (TTD Teknisi MDD)', 0, 0, 'C')
            self.ln(3)
            self.cell(MARGIN_LEFT, 7, '--Internal Use Only--', 0, 0, 'C')


def load_strings(param):
    strings_list = []
    for i in range(len(param)):
        strings_list.append(param[i])
    return '\r\n'.join(strings_list)


def get_path(file):
    return os.path.join(PATH, file)


PARAM = {}
GET_PAYMENT_METHOD = None
GET_CARD_NO = None
GET_PAYMENT_NOTES = None
GET_TOTAL_NOTES = 0
MAX_LENGTH = 36


def chunk_text(text, length=24, delimiter="\r\n"):
    if len(text) <= length:
        return text
    else:
        return text[:length] + delimiter + text[length:]


def font_path(font):
    return os.path.join(sys.path[0], '_fFonts', font)


def justifying(left, right):
    return left + (" " * (MAX_LENGTH-len(left)-len(right))) + right


def start_direct_sale_print_global(payload):
    _KioskService.GLOBAL_TRANSACTION_DATA = json.loads(payload)
    _Helper.get_thread().apply_async(sale_print_global, )


def start_direct_sale_print_ereceipt(payload):
    _KioskService.GLOBAL_TRANSACTION_DATA = json.loads(payload)
    _Helper.get_thread().apply_async(sale_print_global_ereceipt, )


def start_sale_print_global():
    _Helper.get_thread().apply_async(sale_print_global, )


    # '{"date":"Thursday, March 07, 2019","epoch":1551970698740,"payment":"cash","shop_type":"shop","time":"9:58:18 PM",
    # "qty":4,"value":"3000","provider":"Kartu Prabayar","raw":{"init_price":500,"syncFlag":1,"createdAt":1551856851000,
    # "stock":99,"pid":"testprod001","name":"Test Product","status":1,"sell_price":750,"stid":"stid001",
    # "remarks":"TEST STOCK PRODUCT"},"notes":"DEBUG_TEST - 1551970698879"}'

    # '{"date":"Thursday, March 07, 2019","epoch":1551970911009,"payment":"debit","shop_type":"topup","time":"10:01:51 PM",
    # "qty":1,"value":"50000","provider":"e-Money Mandiri","raw":{"provider":"e-Money Mandiri","value":"50000"},
    # "notes":"DEBUG_TEST - 1551970911187"}')


def start_reprint_global():
    _Helper.get_thread().apply_async(sale_reprint_global, )


def validate_refund_fee(channel):
    fee = _Common.check_refund_fee(channel)
    LOGGER.debug(('Refund Fee Check', fee))
    if fee > 0:
        return True, str(fee)
    else:
        return False, str(0)


LAST_TRX = None
SMALL_SPACE = 3.5
REGULAR_SPACE = 8
PADDING_LEFT = 0


def sale_print_global(ext='.pdf', use_last=False):
    global LAST_TRX, HEADER_TEXT1
    if not use_last:
        if _KioskService.GLOBAL_TRANSACTION_DATA is None:
            LOGGER.warning(('Cannot Generate Receipt Data', 'GLOBAL_TRANSACTION_DATA', 'None'))
            SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERROR')
            return
        LAST_TRX = _KioskService.GLOBAL_TRANSACTION_DATA
    # if _Common.PRINTER_TYPE.lower() == 'ereceipt':
    #     sale_print_global_ereceipt()
    #     return
    if _Common.PRINTER_NEW_LAYOUT is True:
        sale_print_global_new_layout()
        return
    p = LAST_TRX
    if p['shop_type'] == 'topup':    
        print_topup_trx(p, 'ISI ULANG PRABAYAR')    
    if p['shop_type'] == 'shop':    
        print_shop_trx(p, 'PEMBELIAN PRABAYAR')
    if p['shop_type'] == 'ppob':    
        print_ppob_trx(p, 'PEMBELIAN/PEMBAYARAN')


def sale_print_global_new_layout():
    p = LAST_TRX
    if p['shop_type'] == 'topup':    
        new_print_topup_trx(p, 'ISI ULANG KARTU')    
    if p['shop_type'] == 'shop':    
        new_print_shop_trx(p, 'PEMBELIAN KARTU')
    if p['shop_type'] == 'ppob':    
        new_print_ppob_trx(p, 'BELI/BAYAR')


def sale_print_global_ereceipt():
    p = LAST_TRX = _KioskService.GLOBAL_TRANSACTION_DATA
    if p['shop_type'] == 'topup':    
        ereceipt_print_topup_trx(p, 'ISI ULANG KARTU')    
    if p['shop_type'] == 'shop':    
        ereceipt_print_shop_trx(p, 'PEMBELIAN KARTU')
    if p['shop_type'] == 'ppob':    
        ereceipt_print_ppob_trx(p, 'BELI/BAYAR')


def merge_text(text=[]):
    if len(text) == 0:
        return ''
    return ' - '.join(text)



def start_finalize_trx_process(trxid, data, cash):
    _Helper.get_thread().apply_async(finalize_trx_process, (trxid, data, cash,))



def finalize_trx_process(trxid='', data={}, cash=0, failure='USER_CANCELLATION'):
    p = data
    if p['payment'].upper() == 'CASH':
        _BILL.log_book_cash(trxid, p['payment_received'], p['shop_type'])
    if 'payment_error' in p.keys() or (p['shop_type'] == 'topup' and 'topup_details' not in p.keys()):
        if p['shop_type'] == 'topup' and 'topup_details' not in p.keys():
            failure = 'TOPUP_FAILURE'
        if 'pending_trx_code' in p.keys():
            failure = 'PENDING_TRANSACTION'
        # Send Failure To Backend
        _Common.store_upload_failed_trx(trxid, p.get('pid', ''), cash, failure, p.get('payment', 'cash'),
                                        json.dumps(p))
    # save_receipt_local(trxid[-6:], json.dumps(p), 'CUSTOMER_TOPUP_TRX')
    if p['payment'].upper() == 'DEBIT' and _Common.LAST_EDC_TRX_RECEIPT is not None:
        print__ = _Printer.do_printout(_Common.LAST_EDC_TRX_RECEIPT)
        print("pyt : sending pdf to default printer : {}".format(str(print__)))
        _Common.LAST_EDC_TRX_RECEIPT = None


# NEW LAYOUT =============
# TODO: Adjust Below Layout

def new_print_topup_trx(p, t, ext='.pdf'):
    global HEADER_TEXT1
    if _Common.empty(p):
        LOGGER.warning(('Cannot Generate Receipt Data', 'GLOBAL_TRANSACTION_DATA', 'None'))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERROR')
        return
    pdf = None
    # Init Variables
    small_space = SMALL_SPACE - 0.3
    regular_space = REGULAR_SPACE
    padding_left = PADDING_LEFT
    trxid = ''
    # failure = 'USER_CANCELLATION'
    cash = 0
    try:
        cash = int(p['payment_received'])
        HEADER_TEXT1 = t
        # paper_ = get_paper_size('\r\n'.join(p.keys()))
        pdf = NEW_LAYOUT_PDF('P', 'mm', (80, 140))
        # LOGGER.info(('Registering New Font', font_path('UnispaceBold.ttf')))
        # pdf.add_font('UniSpace', '', font_path('UnispaceBold.ttf'), uni=True)
        pdf.add_page()
        file_name = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')+'-'+p['shop_type']
        # Layouting
        # pdf.cell(padding_left, 0, '_' * MAX_LENGTH, 0, 0, 'C')
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        pdf.cell(padding_left, 0, 'Tanggal : '+datetime.strftime(datetime.now(), '%d-%m-%Y'), 0, 0, 'L')
        pdf.cell(padding_left, 0, 'Jam : ' + datetime.strftime(datetime.now(), '%H:%M'), 0, 0, 'R')
        pdf.ln(small_space*2)
        if 'receipt_title' in p.keys():
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, p['receipt_title'].upper(), 0, 0, 'C')
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        __title = t
        pdf.cell(padding_left, 0, merge_text([__title, p['raw']['bank_name'], p['payment'].upper(), ]), 0, 0, 'L')
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        trxid = p['shop_type']+str(p['epoch'])
        pdf.cell(padding_left, 0, 'NO TRX    : '+trxid, 0, 0, 'L')
        # pdf.ln(small_space)
        # pdf.set_font(USED_FONT, '', regular_space)
        # pdf.cell(padding_left, 0, p['shop_type'].upper()+' '+p['provider'], 0, 0, 'L')
        if 'payment_error' not in p.keys() and 'process_error' not in p.keys():
            if 'topup_details' in p.keys():
                # pdf.ln(small_space)
                # pdf.set_font(USED_FONT, '', regular_space)
                # if 'Mandiri' in p['provider']:
                #     pdf.cell(padding_left, 0, 'TID : ' + _Common.TID_MAN, 0, 0, 'L')
                # else:
                #     pdf.cell(padding_left, 0, 'TID : ' + _Common.TID_BNI, 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'ISI ULANG  : Rp. ' + clean_number(p['denom']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'BIAYA ADMIN: Rp. ' + clean_number(p['admin_fee']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'TOTAL BAYAR: Rp. ' + clean_number(p['value']), 0, 0, 'L')
                # pdf.ln(small_space)
                # pdf.set_font(USED_FONT, '', regular_space)
                # pdf.cell(padding_left, 0, 'BANK PENERBIT: ' + p['topup_details']['bank_name'], 0, 0, 'L')
                if 'other_channel_topup' in p['topup_details'].keys():
                    if int(p['topup_details']['other_channel_topup']) > 0:
                        pdf.ln(small_space)
                        pdf.set_font(USED_FONT, '', regular_space)
                        pdf.cell(padding_left, 0, 'PENDING SALDO: Rp. ' + clean_number(str(p['topup_details']['other_channel_topup'])), 0, 0, 'L')
                # pdf.ln(small_space)
                # pdf.set_font(USED_FONT, '', regular_space)
                # pdf.cell(padding_left, 0, 'UANG MASUK : Rp. ' + clean_number(str(cash)), 0, 0, 'L')
                # pdf.ln(small_space)
                # pdf.set_font(USED_FONT, '', regular_space)
                # pdf.cell(padding_left, 0, 'UANG KEMBALI: Rp. ' + clean_number('0'), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'NO. KARTU  : ' + p['topup_details']['card_no'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                # saldo_awal = int(p['topup_details']['last_balance']) - (int(p['value']) - int(p['admin_fee']))
                pdf.cell(padding_left, 0, 'SALDO AWAL : Rp. ' + clean_number(p['raw']['prev_balance']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'SALDO AKHIR: Rp. ' + clean_number(str(p['final_balance'])), 0, 0, 'L')
                if 'refund_status' in p.keys():
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'UANG DITERIMA: Rp. ' + clean_number(str(p['payment_received'])), 0, 0, 'L')
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'CARA KEMBALIAN: ' + _Common.serialize_refund(p['refund_channel']), 0, 0, 'L')
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'STATUS KEMBALIAN: ' + p['refund_number'] + ' ' + p['refund_status'], 0, 0, 'L')
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'NILAI KEMBALIAN: Rp. ' + clean_number(str(p['refund_amount'])), 0, 0, 'L')
                    fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                    if fee_refund_exist:
                        pdf.ln(small_space)
                        pdf.set_font(USED_FONT, '', regular_space)
                        pdf.cell(padding_left, 0, 'ADMIN KEMBALIAN: Rp. ' + clean_number(str(fee_refund)), 0, 0, 'L')
                # elif 'pending_trx_code' in p.keys():
                #     pdf.ln(small_space)
                #     pdf.set_font(USED_FONT, '', regular_space)
                #     pdf.cell(padding_left, 0, 'VOUCHER TRX  : ' + p['pending_trx_code'], 0, 0, 'L')
                # pdf.ln(small_space*2)
                # pdf.set_font(USED_FONT, '', regular_space-1)
                # pdf.cell(0, 0, 'DENGAN ISI ULANG INI, PEMEGANG', 0, 0, 'L')
                # pdf.ln(small_space-1)
                # pdf.set_font(USED_FONT, '', regular_space-1)
                # pdf.cell(0, 0, 'KARTU MENYATAKAN TUNDUK DAN', 0, 0, 'L')
                # pdf.ln(small_space-1)
                # pdf.set_font(USED_FONT, '', regular_space-1)
                # pdf.cell(0, 0, 'MENGIKAT DIRI PADA SYARAT DAN', 0, 0, 'L')
                # pdf.ln(small_space-1)
                # pdf.set_font(USED_FONT, '', regular_space-1)
                # pdf.cell(0, 0, 'KETENTUAN BANK PENERBIT KARTU', 0, 0, 'L')
                # pdf.ln(small_space-1)
                # pdf.set_font(USED_FONT, '', regular_space-1)
                # pdf.cell(0, 0, 'PADA WWW.BANKMANDIRI.CO.ID', 0, 0, 'L')
            else:
                # pdf.ln(small_space)
                # pdf.set_font(USED_FONT, '', regular_space)
                # pdf.cell(padding_left, 0, 'BANK PENERBIT: ' + p['raw']['bank_name'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'NO. KARTU   : ' + p['raw']['card_no'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'SISA SALDO  : Rp. ' + clean_number(p['raw']['prev_balance']), 0, 0, 'L')
                # pdf.ln(small_space)
                # pdf.set_font(USED_FONT, '', regular_space)
                # pdf.cell(padding_left, 0, 'STATUS ISI ULANG KARTU GAGAL', 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'UANG DITERIMA: Rp. ' + clean_number(str(p['payment_received'])), 0, 0, 'L')
                if 'refund_status' in p.keys():
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'CARA KEMBALIAN: ' + _Common.serialize_refund(p['refund_channel']), 0, 0, 'L')
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'STATUS KEMBALIAN: ' + p['refund_number'] + ' ' + p['refund_status'], 0, 0, 'L')
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'NILAI KEMBALIAN: Rp. ' + clean_number(str(p['refund_amount'])), 0, 0, 'L')
                    fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                    if fee_refund_exist:
                        pdf.ln(small_space)
                        pdf.set_font(USED_FONT, '', regular_space)
                        pdf.cell(padding_left, 0, 'ADMIN KEMBALIAN: Rp. ' + clean_number(str(fee_refund)), 0, 0, 'L')
                elif 'pending_trx_code' in p.keys():
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'KODE ULANG : ' + p['pending_trx_code'], 0, 0, 'L')
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'DAPAT MELANJUTKAN TRANSAKSI KEMBALI', 0, 0, 'L')
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'PADA MENU CEK/LANJUT TRANSAKSI', 0, 0, 'L')
                # pdf.ln(small_space)
                # pdf.set_font(USED_FONT, '', regular_space-1)
                # pdf.cell(padding_left, 0, 'SILAKAN HUBUNGI LAYANAN PELANGGAN', 0, 0, 'L')
                # pdf.ln(small_space)
                # pdf.set_font(USED_FONT, '', regular_space-1)
                # pdf.cell(padding_left, 0, '(SIMPAN STRUK INI SEBAGAI BUKTI)', 0, 0, 'L')
                    # failure = 'TOPUP_FAILURE'
        else:
            # pdf.ln(small_space*2)
            # pdf.set_font(USED_FONT, '', regular_space)
            # pdf.cell(padding_left, 0, 'BANK PENERBIT: ' + p['raw']['bank_name'], 0, 0, 'L')
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'NO. KARTU   : ' + p['raw']['card_no'], 0, 0, 'L')
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'SISA SALDO  : Rp. ' + clean_number(p['raw']['prev_balance']), 0, 0, 'L')
            # pdf.ln(small_space*2)
            # pdf.set_font(USED_FONT, '', regular_space)
            # pdf.cell(padding_left, 0, 'TERJADI BATAL/GAGAL BAYAR TRANSAKSI', 0, 0, 'L')
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'UANG DITERIMA: Rp. ' + clean_number(str(p['payment_received'])), 0, 0, 'L')
            if 'refund_status' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'CARA KEMBALIAN: ' + _Common.serialize_refund(p['refund_channel']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'STATUS KEMBALIAN: ' + p['refund_number'] + ' ' + p['refund_status'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'NILAI KEMBALIAN: Rp. ' + clean_number(str(p['refund_amount'])), 0, 0, 'L')
                fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                if fee_refund_exist:
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'ADMIN KEMBALIAN: Rp. ' + clean_number(str(fee_refund)), 0, 0, 'L')
            elif 'pending_trx_code' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'KODE ULANG : ' + p['pending_trx_code'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'DAPAT MELANJUTKAN TRANSAKSI KEMBALI', 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'PADA MENU CEK/LANJUT TRANSAKSI', 0, 0, 'L')
            # pdf.ln(small_space*4)
            # pdf.set_font(USED_FONT, '', regular_space)
            # pdf.cell(padding_left, 0, 'SILAKAN HUBUNGI LAYANAN PELANGGAN', 0, 0, 'L')
            # pdf.ln(small_space)
            # pdf.set_font(USED_FONT, '', regular_space)
            # pdf.cell(padding_left, 0, '(SIMPAN STRUK INI SEBAGAI BUKTI)', 0, 0, 'L')
        # Footer Move Here
        pdf.ln(regular_space)
        if len(_Common.CUSTOM_RECEIPT_TEXT) > 5:
            for custom_text in _Common.CUSTOM_RECEIPT_TEXT.split('|'):
                pdf.ln(2.5)
                pdf.cell(MARGIN_LEFT, 6.5, custom_text, 0, 0, 'C')
        # End Layouting
        pdf_file = get_path(file_name+ext)
        pdf.output(pdf_file, 'F')
        LOGGER.debug((file_name))
        # Print-out to printer
        print_ = _Printer.do_printout(pdf_file)
        print("pyt : sending pdf to default printer : {}".format(str(print_)))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|DONE')
        # failure = 'USER_CANCELLATION'
        # if 'payment_error' in p.keys() or (p['shop_type'] == 'topup' and 'topup_details' not in p.keys()):
        #     if p['shop_type'] == 'topup' and 'topup_details' not in p.keys():
        #         failure = 'TOPUP_FAILURE'
        #     # Send Failure To Backend
        #     _Common.store_upload_failed_trx(trxid, p.get('pid', ''), cash, failure, p.get('payment', 'cash'),
        #                                     json.dumps(p))
    except Exception as e:
        LOGGER.warning(str(e))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERROR')
    finally:
        finalize_trx_process(trxid, p, cash)
        del pdf


def new_print_shop_trx(p, t, ext='.pdf'):
    global HEADER_TEXT1
    if _Common.empty(p):
        LOGGER.warning(('Cannot Generate Receipt Data', 'GLOBAL_TRANSACTION_DATA', 'None'))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERROR')
        return
    pdf = None
    # Init Variables
    small_space = SMALL_SPACE - 0.3
    regular_space = REGULAR_SPACE
    padding_left = PADDING_LEFT
    trxid = ''
    # failure = 'USER_CANCELLATION'
    cash = 0
    try:
        cash = int(p['payment_received'])
        HEADER_TEXT1 = t
        # paper_ = get_paper_size('\r\n'.join(p.keys()))
        pdf = NEW_LAYOUT_PDF('P', 'mm', (80, 140))
        # LOGGER.info(('Registering New Font', font_path('UnispaceBold.ttf')))
        # pdf.add_font('UniSpace', '', font_path('UnispaceBold.ttf'), uni=True)
        pdf.add_page()
        file_name = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')+'-'+p['shop_type']
        # Layouting
        # pdf.cell(padding_left, 0, '_' * MAX_LENGTH, 0, 0, 'C')
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        pdf.cell(padding_left, 0, 'Tanggal : '+datetime.strftime(datetime.now(), '%d-%m-%Y'), 0, 0, 'L')
        pdf.cell(padding_left, 0, 'Jam : ' + datetime.strftime(datetime.now(), '%H:%M'), 0, 0, 'R')
        pdf.ln(small_space*2)
        if 'receipt_title' in p.keys():
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, p['receipt_title'].upper(), 0, 0, 'C')
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        __title = t
        pdf.cell(padding_left, 0, merge_text([__title, p['payment'].upper(), ]), 0, 0, 'L')
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        trxid = p['shop_type']+str(p['epoch'])
        pdf.cell(padding_left, 0, 'NO TRX    : '+trxid, 0, 0, 'L')
        # pdf.set_font(USED_FONT, '', regular_space)
        # pdf.cell(padding_left, 0, p['shop_type'].upper()+' '+p['provider'], 0, 0, 'L')
        if 'payment_error' not in p.keys() and 'process_error' not in p.keys():
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'TIPE KARTU  : ' + p['provider'], 0, 0, 'L')
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'QTY KARTU   : ' + str(p['qty']), 0, 0, 'L')
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, str(p['qty']) + ' x ' + clean_number(p['value']), 0, 0, 'R')
            # pdf.ln(small_space)
            # pdf.set_font(USED_FONT, '', regular_space)
            # pdf.cell(padding_left, 0, 'UANG MASUK  : Rp. ' + clean_number(str(cash)), 0, 0, 'L')
            if 'refund_status' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'UANG DITERIMA: Rp. ' + clean_number(str(p['payment_received'])), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'PENGEMBALIAN: ' + _Common.serialize_refund(p['refund_channel']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'STATUS KEMBALIAN: ' + p['refund_number'] + ' ' + p['refund_status'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'NILAI KEMBALIAN: Rp. ' + clean_number(str(p['refund_amount'])), 0, 0, 'L')
                fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                if fee_refund_exist:
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'ADMIN KEMBALIAN: Rp. ' + clean_number(str(fee_refund)), 0, 0, 'L')
            elif 'pending_trx_code' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'KODE ULANG : ' + p['pending_trx_code'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'DAPAT MELANJUTKAN TRANSAKSI KEMBALI', 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'PADA MENU CEK/LANJUT TRANSAKSI', 0, 0, 'L')
                # price_unit = str(int(int(p['value'])/p['qty']))
                # sub_total = p['value']
                # if p['payment'] == 'cash' and p['shop_type'] == 'topup':
                #     sub_total = str(int(p['value']) - int(p['admin_fee']))
                #     price_unit = str(int(int(sub_total) / p['qty']))
            pdf.ln(small_space*2)
            pdf.set_font(USED_FONT, '', regular_space+2)
            total_pay = str(int(int(p['value']) * int(p['qty'])))
            pdf.cell(padding_left, 0, 'TOTAL BAYAR : Rp. ' + clean_number(total_pay), 0, 0, 'L')
            # pdf.ln(small_space*2)
            # pdf.set_font(USED_FONT, '', regular_space-1)
            # pdf.cell(padding_left, 0, 'PEMEGANG KARTU MENYATAKAN TUNDUK DAN', 0, 0, 'L')
            # pdf.ln(small_space-1)
            # pdf.set_font(USED_FONT, '', regular_space-1)
            # pdf.cell(padding_left, 0, 'MENGIKAT DIRI PADA SYARAT DAN', 0, 0, 'L')
            # pdf.ln(small_space-1)
            # pdf.set_font(USED_FONT, '', regular_space-1)
            # pdf.cell(padding_left, 0, 'KETENTUAN BANK PENERBIT KARTU', 0, 0, 'L')
            # pdf.ln(small_space)
            # pdf.set_font(USED_FONT, '', regular_space-1)
            # pdf.cell(padding_left, 0, '(SIMPAN STRUK INI SEBAGAI BUKTI)', 0, 0, 'L')
            # failure = 'TOPUP_FAILURE'
        else:
            # pdf.ln(small_space*2)
            # pdf.set_font(USED_FONT, '', regular_space)
            # pdf.cell(padding_left, 0, 'TERJADI BATAL/GAGAL BAYAR TRANSAKSI', 0, 0, 'L')
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'UANG DITERIMA : Rp. ' + clean_number(str(p['payment_received'])), 0, 0, 'L')
            if 'refund_status' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'CARA KEMBALIAN: ' + _Common.serialize_refund(p['refund_channel']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'STATUS KEMBALIAN: ' + p['refund_number'] + ' ' + p['refund_status'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'NILAI KEMBALIAN: Rp. ' + clean_number(str(p['refund_amount'])), 0, 0, 'L')
                fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                if fee_refund_exist:
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'ADMIN KEMBALIAN: Rp. ' + clean_number(str(fee_refund)), 0, 0, 'L')
            elif 'pending_trx_code' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'KODE ULANG : ' + p['pending_trx_code'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'DAPAT MELANJUTKAN TRANSAKSI KEMBALI', 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'PADA MENU CEK/LANJUT TRANSAKSI', 0, 0, 'L')
            # pdf.ln(small_space*3)
            # pdf.set_font(USED_FONT, '', regular_space)
            # pdf.cell(padding_left, 0, 'SILAKAN HUBUNGI LAYANAN PELANGGAN', 0, 0, 'L')
            # pdf.ln(small_space)
            # pdf.set_font(USED_FONT, '', regular_space)
            # pdf.cell(padding_left, 0, '(SIMPAN STRUK INI SEBAGAI BUKTI)', 0, 0, 'L')
        # Footer Move Here
        pdf.ln(regular_space)
        if len(_Common.CUSTOM_RECEIPT_TEXT) > 5:
            for custom_text in _Common.CUSTOM_RECEIPT_TEXT.split('|'):
                pdf.ln(2.5)
                pdf.cell(MARGIN_LEFT, 6.5, custom_text, 0, 0, 'C')
        # End Layouting
        pdf_file = get_path(file_name+ext)
        pdf.output(pdf_file, 'F')
        LOGGER.debug((file_name))
        # Print-out to printer
        print_ = _Printer.do_printout(pdf_file)
        print("pyt : sending pdf to default printer : {}".format(str(print_)))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|DONE')
        # failure = 'USER_CANCELLATION'
        # if 'payment_error' in p.keys() or (p['shop_type'] == 'topup' and 'topup_details' not in p.keys()):
        #     if p['shop_type'] == 'topup' and 'topup_details' not in p.keys():
        #         failure = 'TOPUP_FAILURE'
        #     # Send Failure To Backend
        #     _Common.store_upload_failed_trx(trxid, p.get('pid', ''), cash, failure, p.get('payment', 'cash'),
        #                                     json.dumps(p))
    except Exception as e:
        LOGGER.warning(str(e))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERROR')
    finally:
        finalize_trx_process(trxid, p, cash)
        del pdf


def new_print_ppob_trx(p, t, ext='.pdf'):
    global HEADER_TEXT1
    if _Common.empty(p):
        LOGGER.warning(('Cannot Generate Receipt Data', 'GLOBAL_TRANSACTION_DATA', 'None'))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERROR')
        return
    pdf = None
    # Init Variables
    small_space = SMALL_SPACE - 0.3
    regular_space = REGULAR_SPACE
    padding_left = PADDING_LEFT
    trxid = ''
    # failure = 'USER_CANCELLATION'
    cash = 0
    try:
        cash = int(p['payment_received'])
        HEADER_TEXT1 = t
        # paper_ = get_paper_size('\r\n'.join(p.keys()))
        pdf = NEW_LAYOUT_PDF('P', 'mm', (80, 140))
        # LOGGER.info(('Registering New Font', font_path('UnispaceBold.ttf')))
        # pdf.add_font('UniSpace', '', font_path('UnispaceBold.ttf'), uni=True)
        pdf.add_page()
        file_name = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')+'-'+p['shop_type']
        # Layouting
        # pdf.cell(padding_left, 0, '_' * MAX_LENGTH, 0, 0, 'C')
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        pdf.cell(padding_left, 0, 'Tanggal : '+datetime.strftime(datetime.now(), '%d-%m-%Y'), 0, 0, 'L')
        pdf.cell(padding_left, 0, 'Jam : ' + datetime.strftime(datetime.now(), '%H:%M'), 0, 0, 'R')
        pdf.ln(small_space*2)
        if 'receipt_title' in p.keys():
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, p['receipt_title'].upper(), 0, 0, 'C')
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        __title = t
        pdf.cell(padding_left, 0, merge_text([__title, p['payment'].upper(), ]), 0, 0, 'L')
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        trxid = p['shop_type']+str(p['epoch'])
        pdf.cell(padding_left, 0, 'NO TRX    : '+trxid, 0, 0, 'L')
        # pdf.ln(small_space)
        # pdf.set_font(USED_FONT, '', regular_space)
        # pdf.cell(padding_left, 0, 'KATEGORI  : ' + str(p['category']), 0, 0, 'L')
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        pdf.cell(padding_left, 0, 'PROVIDER  : ' + str(p['provider']), 0, 0, 'L')
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        pdf.cell(padding_left, 0, 'MSISDN    : ' + str(p['msisdn']), 0, 0, 'L')
        # pdf.set_font(USED_FONT, '', regular_space)
        # pdf.cell(padding_left, 0, p['shop_type'].upper()+' '+p['provider'], 0, 0, 'L')
        if 'ppob_details' in p.keys() and 'payment_error' not in p.keys() and 'process_error' not in p.keys():
            if p['ppob_mode'] == 'tagihan':
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'PELANGGAN  : Rp. ' + str(p['customer']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'TAGIHAN    : Rp. ' + clean_number(str(p['value'])), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'BIAYA ADMIN: Rp. ' + clean_number(str(p['admin_fee'])), 0, 0, 'L')
            else:
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'JUMLAH     : ' + str(p['qty']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'HARGA/UNIT : Rp. ' + clean_number(str(p['value'])), 0, 0, 'L')
                if 'sn' in p['ppob_details'].keys():
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    label_sn = 'S/N '
                    if p['category'].lower() == 'listrik':
                        label_sn = 'TOKEN '
                        if str(p['ppob_details']['sn']) == '[]':
                            pdf.cell(padding_left, 0, 'TOKEN DALAM PROSES, HUBUNGI LAYANAN PELANGGAN', 0, 0, 'L')
                        else:    
                            pdf.cell(padding_left, 0, label_sn + str(p['ppob_details']['sn'][:24]), 0, 0, 'L')
                    else:
                        pdf.cell(padding_left, 0, label_sn + str(p['ppob_details']['sn'][:24]), 0, 0, 'L')
            if 'refund_status' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'UANG DITERIMA: Rp. ' + clean_number(str(p['payment_received'])), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'CARA KEMBALIAN: ' + _Common.serialize_refund(p['refund_channel']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'STATUS KEMBALIAN: ' + p['refund_number'] + ' ' + p['refund_status'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'NILAI KEMBALIAN: Rp. ' + clean_number(str(p['refund_amount'])), 0, 0, 'L')
                fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                if fee_refund_exist:
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'ADMIN KEMBALIAN: Rp. ' + clean_number(str(fee_refund)), 0, 0, 'L')
            elif 'pending_trx_code' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'KODE ULANG : ' + p['pending_trx_code'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'DAPAT MELANJUTKAN TRANSAKSI KEMBALI', 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'PADA MENU CEK/LANJUT TRANSAKSI', 0, 0, 'L')
            pdf.ln(small_space*2)
            pdf.set_font(USED_FONT, '', regular_space+2)
            total_pay = str(int(int(p['value']) * int(p['qty'])))
            pdf.cell(0, 0, 'TOTAL BAYAR : Rp. ' + clean_number(total_pay), 0, 0, 'L')
            # pdf.ln(small_space*2)
            # pdf.set_font(USED_FONT, '', regular_space-1)
            # pdf.cell(padding_left, 0, '(SIMPAN STRUK INI SEBAGAI BUKTI)', 0, 0, 'L')
            # failure = 'TOPUP_FAILURE'
        else:
            # pdf.ln(small_space*2)
            # pdf.set_font(USED_FONT, '', regular_space)
            # pdf.cell(padding_left, 0, 'TERJADI BATAL/GAGAL BAYAR TRANSAKSI', 0, 0, 'L')
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'UANG DITERIMA : Rp. ' + clean_number(str(p['payment_received'])), 0, 0, 'L')
            if 'refund_status' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'CARA KEMBALIAN: ' + _Common.serialize_refund(p['refund_channel']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'STATUS KEMBALIAN: ' + p['refund_number'] + ' ' + p['refund_status'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'NILAI KEMBALIAN: Rp. ' + clean_number(str(p['refund_amount'])), 0, 0, 'L')
                fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                if fee_refund_exist:
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'ADMIN KEMBALIAN: Rp. ' + clean_number(str(fee_refund)), 0, 0, 'L')
            elif 'pending_trx_code' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'KODE ULANG : ' + p['pending_trx_code'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'DAPAT MELANJUTKAN TRANSAKSI KEMBALI', 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'PADA MENU CEK/LANJUT TRANSAKSI', 0, 0, 'L')
            # pdf.ln(small_space*3)
            # pdf.set_font(USED_FONT, '', regular_space)
            # pdf.cell(padding_left, 0, 'SILAKAN HUBUNGI LAYANAN PELANGGAN', 0, 0, 'L')
            # pdf.ln(small_space)
            # pdf.set_font(USED_FONT, '', regular_space)
            # pdf.cell(padding_left, 0, '(SIMPAN STRUK INI SEBAGAI BUKTI)', 0, 0, 'L')
        # Footer Move Here
        pdf.ln(regular_space)
        if len(_Common.CUSTOM_RECEIPT_TEXT) > 5:
            for custom_text in _Common.CUSTOM_RECEIPT_TEXT.split('|'):
                pdf.ln(2.5)
                pdf.cell(MARGIN_LEFT, 6.5, custom_text, 0, 0, 'C')
        # End Layouting
        pdf_file = get_path(file_name+ext)
        pdf.output(pdf_file, 'F')
        LOGGER.debug((file_name))
        # Print-out to printer
        print_ = _Printer.do_printout(pdf_file)
        print("pyt : sending pdf to default printer : {}".format(str(print_)))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|DONE')
    except Exception as e:
        LOGGER.warning(str(e))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERROR')
    finally:
        finalize_trx_process(trxid, p, cash)
        del pdf


# OLD LAYOUT =============

def print_topup_trx(p, t, ext='.pdf'):
    global HEADER_TEXT1
    if _Common.empty(p):
        LOGGER.warning(('Cannot Generate Receipt Data', 'GLOBAL_TRANSACTION_DATA', 'None'))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERROR')
        return
    pdf = None
    # Init Variables
    small_space = SMALL_SPACE
    regular_space = REGULAR_SPACE
    padding_left = PADDING_LEFT
    trxid = ''
    # failure = 'USER_CANCELLATION'
    cash = 0
    try:
        cash = int(p['payment_received'])
        HEADER_TEXT1 = t
        # paper_ = get_paper_size('\r\n'.join(p.keys()))
        pdf = PDF('P', 'mm', (80, 140))
        # LOGGER.info(('Registering New Font', font_path('UnispaceBold.ttf')))
        # pdf.add_font('UniSpace', '', font_path('UnispaceBold.ttf'), uni=True)
        pdf.add_page()
        file_name = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')+'-'+p['shop_type']
        # Layouting
        pdf.cell(padding_left, 0, '_' * MAX_LENGTH, 0, 0, 'C')
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        pdf.cell(padding_left, 0, 'Tanggal : '+datetime.strftime(datetime.now(), '%d-%m-%Y'), 0, 0, 'L')
        pdf.cell(padding_left, 0, 'Jam : ' + datetime.strftime(datetime.now(), '%H:%M'), 0, 0, 'R')
        pdf.ln(small_space*2)
        pdf.set_font(USED_FONT, '', regular_space)
        __title = t
        pdf.cell(padding_left, 0, __title, 0, 0, 'L')
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        trxid = p['shop_type']+str(p['epoch'])
        pdf.cell(padding_left, 0, 'NO TRX    : '+trxid, 0, 0, 'L')
        pdf.ln(small_space)
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        pdf.cell(padding_left, 0, 'PEMBAYARAN: ' + p['payment'].upper(), 0, 0, 'L')
        # pdf.set_font(USED_FONT, '', regular_space)
        # pdf.cell(padding_left, 0, p['shop_type'].upper()+' '+p['provider'], 0, 0, 'L')
        if 'payment_error' not in p.keys() and 'process_error' not in p.keys():
            if 'topup_details' in p.keys():
                # pdf.ln(small_space)
                # pdf.set_font(USED_FONT, '', regular_space)
                # if 'Mandiri' in p['provider']:
                #     pdf.cell(padding_left, 0, 'TID : ' + _Common.TID_MAN, 0, 0, 'L')
                # else:
                #     pdf.cell(padding_left, 0, 'TID : ' + _Common.TID_BNI, 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'ISI ULANG  : Rp. ' + clean_number(p['denom']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'BIAYA ADMIN: Rp. ' + clean_number(p['admin_fee']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'TOTAL BAYAR: Rp. ' + clean_number(p['value']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'BANK PENERBIT: ' + p['topup_details']['bank_name'], 0, 0, 'L')
                if 'other_channel_topup' in p['topup_details'].keys():
                    if int(p['topup_details']['other_channel_topup']) > 0:
                        pdf.ln(small_space)
                        pdf.set_font(USED_FONT, '', regular_space)
                        pdf.cell(padding_left, 0, 'PENDING SALDO: Rp. ' + clean_number(str(p['topup_details']['other_channel_topup'])), 0, 0, 'L')
                # pdf.ln(small_space)
                # pdf.set_font(USED_FONT, '', regular_space)
                # pdf.cell(padding_left, 0, 'UANG MASUK : Rp. ' + clean_number(str(cash)), 0, 0, 'L')
                # pdf.ln(small_space)
                # pdf.set_font(USED_FONT, '', regular_space)
                # pdf.cell(padding_left, 0, 'UANG KEMBALI: Rp. ' + clean_number('0'), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'NO. KARTU  : ' + p['topup_details']['card_no'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                # saldo_awal = int(p['topup_details']['last_balance']) - (int(p['value']) - int(p['admin_fee']))
                pdf.cell(padding_left, 0, 'SALDO AWAL : Rp. ' + clean_number(p['raw']['prev_balance']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'SALDO AKHIR: Rp. ' + clean_number(str(p['final_balance'])), 0, 0, 'L')
                if 'refund_status' in p.keys():
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'UANG DITERIMA: Rp. ' + clean_number(str(p['payment_received'])), 0, 0, 'L')
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'METODE REFUND: ' + _Common.serialize_refund(p['refund_channel']), 0, 0, 'L')
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'STATUS REFUND: ' + p['refund_number'] + ' ' + p['refund_status'], 0, 0, 'L')
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'NILAI REFUND : Rp. ' + clean_number(str(p['refund_amount'])), 0, 0, 'L')
                    fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                    if fee_refund_exist:
                        pdf.ln(small_space)
                        pdf.set_font(USED_FONT, '', regular_space)
                        pdf.cell(padding_left, 0, 'FEE REFUND   : Rp. ' + clean_number(str(fee_refund)), 0, 0, 'L')
                # elif 'pending_trx_code' in p.keys():
                #     pdf.ln(small_space)
                #     pdf.set_font(USED_FONT, '', regular_space)
                #     pdf.cell(padding_left, 0, 'VOUCHER TRX  : ' + p['pending_trx_code'], 0, 0, 'L')
                # pdf.ln(small_space*2)
                # pdf.set_font(USED_FONT, '', regular_space-1)
                # pdf.cell(0, 0, 'DENGAN ISI ULANG INI, PEMEGANG', 0, 0, 'L')
                # pdf.ln(small_space-1)
                # pdf.set_font(USED_FONT, '', regular_space-1)
                # pdf.cell(0, 0, 'KARTU MENYATAKAN TUNDUK DAN', 0, 0, 'L')
                # pdf.ln(small_space-1)
                # pdf.set_font(USED_FONT, '', regular_space-1)
                # pdf.cell(0, 0, 'MENGIKAT DIRI PADA SYARAT DAN', 0, 0, 'L')
                # pdf.ln(small_space-1)
                # pdf.set_font(USED_FONT, '', regular_space-1)
                # pdf.cell(0, 0, 'KETENTUAN BANK PENERBIT KARTU', 0, 0, 'L')
                # pdf.ln(small_space-1)
                # pdf.set_font(USED_FONT, '', regular_space-1)
                # pdf.cell(0, 0, 'PADA WWW.BANKMANDIRI.CO.ID', 0, 0, 'L')
            else:
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'BANK PENERBIT: ' + p['raw']['bank_name'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'NO. KARTU   : ' + p['raw']['card_no'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'SISA SALDO  : Rp. ' + clean_number(p['raw']['prev_balance']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'STATUS ISI ULANG KARTU GAGAL', 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'UANG DITERIMA: Rp. ' + clean_number(str(p['payment_received'])), 0, 0, 'L')
                if 'refund_status' in p.keys():
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'METODE REFUND: ' + _Common.serialize_refund(p['refund_channel']), 0, 0, 'L')
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'STATUS REFUND: ' + p['refund_number'] + ' ' + p['refund_status'], 0, 0, 'L')
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'NILAI REFUND : Rp. ' + clean_number(str(p['refund_amount'])), 0, 0, 'L')
                    fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                    if fee_refund_exist:
                        pdf.ln(small_space)
                        pdf.set_font(USED_FONT, '', regular_space)
                        pdf.cell(padding_left, 0, 'FEE REFUND   : Rp. ' + clean_number(str(fee_refund)), 0, 0, 'L')
                elif 'pending_trx_code' in p.keys():
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'VOUCHER TRX  : ' + p['pending_trx_code'], 0, 0, 'L')
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'DAPAT MELANJUTKAN TRANSAKSI KEMBALI', 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space-1)
                pdf.cell(padding_left, 0, 'SILAKAN HUBUNGI LAYANAN PELANGGAN', 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space-1)
                pdf.cell(padding_left, 0, '(SIMPAN STRUK INI SEBAGAI BUKTI)', 0, 0, 'L')
                    # failure = 'TOPUP_FAILURE'
        else:
            pdf.ln(small_space*2)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'BANK PENERBIT: ' + p['raw']['bank_name'], 0, 0, 'L')
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'NO. KARTU   : ' + p['raw']['card_no'], 0, 0, 'L')
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'SISA SALDO  : Rp. ' + clean_number(p['raw']['prev_balance']), 0, 0, 'L')
            pdf.ln(small_space*2)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'TERJADI BATAL/GAGAL BAYAR TRANSAKSI', 0, 0, 'L')
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'UANG DITERIMA: Rp. ' + clean_number(str(p['payment_received'])), 0, 0, 'L')
            if 'refund_status' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'METODE REFUND: ' + _Common.serialize_refund(p['refund_channel']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'STATUS REFUND: ' + p['refund_number'] + ' ' + p['refund_status'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'NILAI REFUND : Rp. ' + clean_number(str(p['refund_amount'])), 0, 0, 'L')
                fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                if fee_refund_exist:
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'FEE REFUND   : Rp. ' + clean_number(str(fee_refund)), 0, 0, 'L')
            elif 'pending_trx_code' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'VOUCHER TRX  : ' + p['pending_trx_code'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'DAPAT MELANJUTKAN TRANSAKSI KEMBALI', 0, 0, 'L')
            pdf.ln(small_space*4)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'SILAKAN HUBUNGI LAYANAN PELANGGAN', 0, 0, 'L')
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, '(SIMPAN STRUK INI SEBAGAI BUKTI)', 0, 0, 'L')
        pdf.ln(small_space)
        # End Layouting
        pdf_file = get_path(file_name+ext)
        pdf.output(pdf_file, 'F')
        LOGGER.debug((file_name))
        # Print-out to printer
        print_ = _Printer.do_printout(pdf_file)
        print("pyt : sending pdf to default printer : {}".format(str(print_)))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|DONE')
        # failure = 'USER_CANCELLATION'
        # if 'payment_error' in p.keys() or (p['shop_type'] == 'topup' and 'topup_details' not in p.keys()):
        #     if p['shop_type'] == 'topup' and 'topup_details' not in p.keys():
        #         failure = 'TOPUP_FAILURE'
        #     # Send Failure To Backend
        #     _Common.store_upload_failed_trx(trxid, p.get('pid', ''), cash, failure, p.get('payment', 'cash'),
        #                                     json.dumps(p))
    except Exception as e:
        LOGGER.warning(str(e))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERROR')
    finally:
        finalize_trx_process(trxid, p, cash)
        del pdf


def print_shop_trx(p, t, ext='.pdf'):
    global HEADER_TEXT1
    if _Common.empty(p):
        LOGGER.warning(('Cannot Generate Receipt Data', 'GLOBAL_TRANSACTION_DATA', 'None'))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERROR')
        return
    pdf = None
    # Init Variables
    small_space = SMALL_SPACE
    regular_space = REGULAR_SPACE
    padding_left = PADDING_LEFT
    trxid = ''
    # failure = 'USER_CANCELLATION'
    cash = 0
    try:
        cash = int(p['payment_received'])
        HEADER_TEXT1 = t
        # paper_ = get_paper_size('\r\n'.join(p.keys()))
        pdf = PDF('P', 'mm', (80, 140))
        # LOGGER.info(('Registering New Font', font_path('UnispaceBold.ttf')))
        # pdf.add_font('UniSpace', '', font_path('UnispaceBold.ttf'), uni=True)
        pdf.add_page()
        file_name = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')+'-'+p['shop_type']
        # Layouting
        pdf.cell(padding_left, 0, '_' * MAX_LENGTH, 0, 0, 'C')
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        pdf.cell(padding_left, 0, 'Tanggal : '+datetime.strftime(datetime.now(), '%d-%m-%Y'), 0, 0, 'L')
        pdf.cell(padding_left, 0, 'Jam : ' + datetime.strftime(datetime.now(), '%H:%M'), 0, 0, 'R')
        pdf.ln(small_space*2)
        pdf.set_font(USED_FONT, '', regular_space)
        __title = t
        pdf.cell(padding_left, 0, __title, 0, 0, 'L')
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        trxid = p['shop_type']+str(p['epoch'])
        pdf.cell(padding_left, 0, 'NO TRX    : '+trxid, 0, 0, 'L')
        pdf.ln(small_space)
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        pdf.cell(padding_left, 0, 'PEMBAYARAN: ' + p['payment'].upper(), 0, 0, 'L')
        # pdf.set_font(USED_FONT, '', regular_space)
        # pdf.cell(padding_left, 0, p['shop_type'].upper()+' '+p['provider'], 0, 0, 'L')
        if 'payment_error' not in p.keys() and 'process_error' not in p.keys():
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'TIPE KARTU  : ' + p['provider'], 0, 0, 'L')
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'QTY KARTU   : ' + str(p['qty']), 0, 0, 'L')
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, str(p['qty']) + ' x ' + clean_number(p['value']), 0, 0, 'R')
            # pdf.ln(small_space)
            # pdf.set_font(USED_FONT, '', regular_space)
            # pdf.cell(padding_left, 0, 'UANG MASUK  : Rp. ' + clean_number(str(cash)), 0, 0, 'L')
            if 'refund_status' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'UANG DITERIMA: Rp. ' + clean_number(str(p['payment_received'])), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'METODE REFUND: ' + _Common.serialize_refund(p['refund_channel']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'STATUS REFUND: ' + p['refund_number'] + ' ' + p['refund_status'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'NILAI REFUND : Rp. ' + clean_number(str(p['refund_amount'])), 0, 0, 'L')
                fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                if fee_refund_exist:
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'FEE REFUND   : Rp. ' + clean_number(str(fee_refund)), 0, 0, 'L')
            elif 'pending_trx_code' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'VOUCHER TRX  : ' + p['pending_trx_code'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'DAPAT MELANJUTKAN TRANSAKSI KEMBALI', 0, 0, 'L')
                # price_unit = str(int(int(p['value'])/p['qty']))
                # sub_total = p['value']
                # if p['payment'] == 'cash' and p['shop_type'] == 'topup':
                #     sub_total = str(int(p['value']) - int(p['admin_fee']))
                #     price_unit = str(int(int(sub_total) / p['qty']))
            pdf.ln(small_space*2)
            pdf.set_font(USED_FONT, '', regular_space+2)
            total_pay = str(int(int(p['value']) * int(p['qty'])))
            pdf.cell(padding_left, 0, 'TOTAL BAYAR : Rp. ' + clean_number(total_pay), 0, 0, 'L')
            pdf.ln(small_space*2)
            pdf.set_font(USED_FONT, '', regular_space-1)
            pdf.cell(padding_left, 0, 'PEMEGANG KARTU MENYATAKAN TUNDUK DAN', 0, 0, 'L')
            pdf.ln(small_space-1)
            pdf.set_font(USED_FONT, '', regular_space-1)
            pdf.cell(padding_left, 0, 'MENGIKAT DIRI PADA SYARAT DAN', 0, 0, 'L')
            pdf.ln(small_space-1)
            pdf.set_font(USED_FONT, '', regular_space-1)
            pdf.cell(padding_left, 0, 'KETENTUAN BANK PENERBIT KARTU', 0, 0, 'L')
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space-1)
            pdf.cell(padding_left, 0, '(SIMPAN STRUK INI SEBAGAI BUKTI)', 0, 0, 'L')
            # failure = 'TOPUP_FAILURE'
        else:
            pdf.ln(small_space*2)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'TERJADI BATAL/GAGAL BAYAR TRANSAKSI', 0, 0, 'L')
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'UANG DITERIMA : Rp. ' + clean_number(str(p['payment_received'])), 0, 0, 'L')
            if 'refund_status' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'METODE REFUND: ' + _Common.serialize_refund(p['refund_channel']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'STATUS REFUND: ' + p['refund_number'] + ' ' + p['refund_status'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'NILAI REFUND : Rp. ' + clean_number(str(p['refund_amount'])), 0, 0, 'L')
                fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                if fee_refund_exist:
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'FEE REFUND   : Rp. ' + clean_number(str(fee_refund)), 0, 0, 'L')
            elif 'pending_trx_code' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'VOUCHER TRX  : ' + p['pending_trx_code'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'DAPAT MELANJUTKAN TRANSAKSI KEMBALI', 0, 0, 'L')
            pdf.ln(small_space*3)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'SILAKAN HUBUNGI LAYANAN PELANGGAN', 0, 0, 'L')
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, '(SIMPAN STRUK INI SEBAGAI BUKTI)', 0, 0, 'L')
        pdf.ln(small_space)
        # End Layouting
        pdf_file = get_path(file_name+ext)
        pdf.output(pdf_file, 'F')
        LOGGER.debug((file_name))
        # Print-out to printer
        print_ = _Printer.do_printout(pdf_file)
        print("pyt : sending pdf to default printer : {}".format(str(print_)))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|DONE')
        # failure = 'USER_CANCELLATION'
        # if 'payment_error' in p.keys() or (p['shop_type'] == 'topup' and 'topup_details' not in p.keys()):
        #     if p['shop_type'] == 'topup' and 'topup_details' not in p.keys():
        #         failure = 'TOPUP_FAILURE'
        #     # Send Failure To Backend
        #     _Common.store_upload_failed_trx(trxid, p.get('pid', ''), cash, failure, p.get('payment', 'cash'),
        #                                     json.dumps(p))
    except Exception as e:
        LOGGER.warning(str(e))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERROR')
    finally:
        finalize_trx_process(trxid, p, cash)
        del pdf


def print_ppob_trx(p, t, ext='.pdf'):
    global HEADER_TEXT1
    if _Common.empty(p):
        LOGGER.warning(('Cannot Generate Receipt Data', 'GLOBAL_TRANSACTION_DATA', 'None'))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERROR')
        return
    pdf = None
    # Init Variables
    small_space = SMALL_SPACE
    regular_space = REGULAR_SPACE
    padding_left = PADDING_LEFT
    trxid = ''
    # failure = 'USER_CANCELLATION'
    cash = 0
    try:
        cash = int(p['payment_received'])
        HEADER_TEXT1 = t
        # paper_ = get_paper_size('\r\n'.join(p.keys()))
        pdf = PDF('P', 'mm', (80, 140))
        # LOGGER.info(('Registering New Font', font_path('UnispaceBold.ttf')))
        # pdf.add_font('UniSpace', '', font_path('UnispaceBold.ttf'), uni=True)
        pdf.add_page()
        file_name = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')+'-'+p['shop_type']
        # Layouting
        pdf.cell(padding_left, 0, '_' * MAX_LENGTH, 0, 0, 'C')
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        pdf.cell(padding_left, 0, 'Tanggal : '+datetime.strftime(datetime.now(), '%d-%m-%Y'), 0, 0, 'L')
        pdf.cell(padding_left, 0, 'Jam : ' + datetime.strftime(datetime.now(), '%H:%M'), 0, 0, 'R')
        pdf.ln(small_space*2)
        pdf.set_font(USED_FONT, '', regular_space)
        __title = t
        pdf.cell(padding_left, 0, __title, 0, 0, 'L')
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        trxid = p['shop_type']+str(p['epoch'])
        pdf.cell(padding_left, 0, 'NO TRX    : '+trxid, 0, 0, 'L')
        pdf.ln(small_space)
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        pdf.cell(padding_left, 0, 'PEMBAYARAN: ' + p['payment'].upper(), 0, 0, 'L')
        # pdf.ln(small_space)
        # pdf.set_font(USED_FONT, '', regular_space)
        # pdf.cell(padding_left, 0, 'KATEGORI  : ' + str(p['category']), 0, 0, 'L')
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        pdf.cell(padding_left, 0, 'PROVIDER  : ' + str(p['provider']), 0, 0, 'L')
        pdf.ln(small_space)
        pdf.set_font(USED_FONT, '', regular_space)
        pdf.cell(padding_left, 0, 'MSISDN    : ' + str(p['msisdn']), 0, 0, 'L')
        # pdf.set_font(USED_FONT, '', regular_space)
        # pdf.cell(padding_left, 0, p['shop_type'].upper()+' '+p['provider'], 0, 0, 'L')
        if 'ppob_details' in p.keys() and 'payment_error' not in p.keys() and 'process_error' not in p.keys():
            if p['ppob_mode'] == 'tagihan':
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'PELANGGAN  : Rp. ' + str(p['customer']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'TAGIHAN    : Rp. ' + clean_number(str(p['value'])), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'BIAYA ADMIN: Rp. ' + clean_number(str(p['admin_fee'])), 0, 0, 'L')
            else:
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'JUMLAH     : ' + str(p['qty']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'HARGA/UNIT : Rp. ' + clean_number(str(p['value'])), 0, 0, 'L')
                if 'sn' in p['ppob_details'].keys():
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    label_sn = 'S/N '
                    if p['category'].lower() == 'listrik':
                        label_sn = 'TOKEN '
                        if str(p['ppob_details']['sn']) == '[]':
                            pdf.cell(padding_left, 0, 'TOKEN DALAM PROSES, HUBUNGI LAYANAN PELANGGAN', 0, 0, 'L')
                        else:    
                            pdf.cell(padding_left, 0, label_sn + str(p['ppob_details']['sn'][:24]), 0, 0, 'L')
                    else:
                        pdf.cell(padding_left, 0, label_sn + str(p['ppob_details']['sn'][:24]), 0, 0, 'L')
            if 'refund_status' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'UANG DITERIMA: Rp. ' + clean_number(str(p['payment_received'])), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'METODE REFUND: ' + _Common.serialize_refund(p['refund_channel']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'STATUS REFUND: ' + p['refund_number'] + ' ' + p['refund_status'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'NILAI REFUND : Rp. ' + clean_number(str(p['refund_amount'])), 0, 0, 'L')
                fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                if fee_refund_exist:
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'FEE REFUND   : Rp. ' + clean_number(str(fee_refund)), 0, 0, 'L')
            elif 'pending_trx_code' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'VOUCHER TRX  : ' + p['pending_trx_code'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'DAPAT MELANJUTKAN TRANSAKSI KEMBALI', 0, 0, 'L')
            pdf.ln(small_space*2)
            pdf.set_font(USED_FONT, '', regular_space+2)
            total_pay = str(int(int(p['value']) * int(p['qty'])))
            pdf.cell(0, 0, 'TOTAL BAYAR : Rp. ' + clean_number(total_pay), 0, 0, 'L')
            pdf.ln(small_space*2)
            pdf.set_font(USED_FONT, '', regular_space-1)
            pdf.cell(padding_left, 0, '(SIMPAN STRUK INI SEBAGAI BUKTI)', 0, 0, 'L')
            # failure = 'TOPUP_FAILURE'
        else:
            pdf.ln(small_space*2)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'TERJADI BATAL/GAGAL BAYAR TRANSAKSI', 0, 0, 'L')
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'UANG DITERIMA : Rp. ' + clean_number(str(p['payment_received'])), 0, 0, 'L')
            if 'refund_status' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'METODE REFUND: ' + _Common.serialize_refund(p['refund_channel']), 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'STATUS REFUND: ' + p['refund_number'] + ' ' + p['refund_status'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'NILAI REFUND : Rp. ' + clean_number(str(p['refund_amount'])), 0, 0, 'L')
                fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                if fee_refund_exist:
                    pdf.ln(small_space)
                    pdf.set_font(USED_FONT, '', regular_space)
                    pdf.cell(padding_left, 0, 'FEE REFUND   : Rp. ' + clean_number(str(fee_refund)), 0, 0, 'L')
            elif 'pending_trx_code' in p.keys():
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'VOUCHER TRX  : ' + p['pending_trx_code'], 0, 0, 'L')
                pdf.ln(small_space)
                pdf.set_font(USED_FONT, '', regular_space)
                pdf.cell(padding_left, 0, 'DAPAT MELANJUTKAN TRANSAKSI KEMBALI', 0, 0, 'L')
            pdf.ln(small_space*3)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, 'SILAKAN HUBUNGI LAYANAN PELANGGAN', 0, 0, 'L')
            pdf.ln(small_space)
            pdf.set_font(USED_FONT, '', regular_space)
            pdf.cell(padding_left, 0, '(SIMPAN STRUK INI SEBAGAI BUKTI)', 0, 0, 'L')
        pdf.ln(small_space)
        # End Layouting
        pdf_file = get_path(file_name+ext)
        pdf.output(pdf_file, 'F')
        LOGGER.debug((file_name))
        # Print-out to printer
        print_ = _Printer.do_printout(pdf_file)
        print("pyt : sending pdf to default printer : {}".format(str(print_)))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|DONE')
    except Exception as e:
        LOGGER.warning(str(e))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERROR')
    finally:
        finalize_trx_process(trxid, p, cash)
        del pdf


def sale_reprint_global(ext='.pdf'):
    sale_print_global(ext=ext, use_last=True)
    

def clean_number(sn):
    return re.sub(r'(?<!^)(?=(\d{3})+$)', r'.', str(sn))


def pdf_print(pdf_file, rotate=False):
    if pdf_file is None:
        LOGGER.warning('Missing PDF File')
        return None
    try:
        if rotate is True:
            pdf_file = rotate_pdf(pdf_file)
        print_ = _Printer.do_printout(pdf_file)
        print("pyt : sending pdf to default printer : {}".format(str(print_)))
    except Exception as e:
        LOGGER.warning(str(e))


def rotate_pdf(path_file):
    try:
        from PyPDF2 import PdfFileWriter, PdfFileReader
        pdf_writer = PdfFileWriter()
        pdf_reader = PdfFileReader(path_file)
        page = pdf_reader.getPage(0).rotateClockwise(90)
        pdf_writer.addPage(page)
        output_file = path_file.replace('.pdf', '_rotated.pdf')

        with open(output_file, 'wb') as fh:
            pdf_writer.write(fh)
        return output_file
    except Exception as e:
        LOGGER.warning(str(e))
        return None

# -------------------------
CARD_SALE = 0 # Will Count All Card Shop TRX
# -------------------------


def get_admin_data():
    __data = dict()
    try:
        __data = _Common.COLLECTION_DATA
        # LOGGER.info(('get_admin_data', str(__data), str(_ProductService.LAST_UPDATED_STOCK)))
    except Exception as e:
        __data = False
        LOGGER.warning(str(e))
    finally:
        return __data


def save_receipt_local(__id, __data, __type):
    try:
        param_receipt = {
            'rid': _Helper.get_uuid(),
            'bookingCode': __id,
            'tid': _Common.TID,
            'receiptRaw': __type,
            'receiptData': __data,
            'createdAt': _Helper.now()
        }
        _DAO.insert_receipt(param_receipt)
        return True
    except Exception as e:
        LOGGER.warning((e))
        return False


def start_admin_print_global(struct_id):
    _Helper.get_thread().apply_async(admin_print_global, (struct_id,))


def admin_print_global(struct_id, ext='.pdf'):
    global GENERAL_TITLE
    pdf = None
    # Init Variables
    tiny_space = 3
    line_size = 7
    padding_left = 0
    print_copy = 2
    user = 'mdd_operator'
    s = False
    if _UserService.USER is not None:
        user = _UserService.USER['username']
    try:
        # paper_ = get_paper_size('\r\n'.join(p.keys()))
        GENERAL_TITLE = 'VM COLLECTION REPORT'
        pdf = GeneralPDF('P', 'mm', (80, 140))
        s = _Common.COLLECTION_DATA
        # LOGGER.info(('Registering New Font', font_path('UnispaceBold.ttf')))
        # pdf.add_font('UniSpace', '', font_path('UnispaceBold.ttf'), uni=True)
        pdf.add_page()
        file_name = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')+'-'+user
        # Layouting
        pdf.cell(padding_left, 0, '_' * MAX_LENGTH, 0, 0, 'C')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, 'Tanggal : '+datetime.strftime(datetime.now(), '%d-%m-%Y')+'  Jam : ' +
                 datetime.strftime(datetime.now(), '%H:%M:%S'), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, 'Operator : ' + user + ' | ' + struct_id, 0, 0, 'L')
        # pdf.ln(tiny_space)
        # pdf.set_font(USED_FONT, '', line_size)
        # pdf.cell(padding_left, 0, 'TRX ID : '+struct_id, 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, '_' * MAX_LENGTH, 0, 0, 'C')
        pdf.ln(tiny_space*2)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, 'CARD SALE', 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        # qty_card = s['trx_card']
        # total_card = str(int(qty_card) * CARD_SALE)
        for cs in s['card_trx_summary']:
            pdf.cell(padding_left, 0,
                    '- '+cs['pid']+' : '+str(cs['count'])+' x '+clean_number(str(cs['price']))+'  = Rp. '+clean_number(str(cs['amount'])), 0, 0, 'L')
            pdf.ln(tiny_space-1)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, '                 Rp. '+clean_number(str(s['amt_card'])), 0, 0, 'L')
        pdf.ln(tiny_space+1)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, 'TOPUP', 0, 0, 'L')
        pdf.ln(tiny_space)
        # if not _Common.BANKS[0]['STATUS']:
        pdf.set_font(USED_FONT, '', line_size)
        qty_t10k = s['trx_top10k']
        total_t10k = str(int(qty_t10k) * 10000)
        pdf.cell(padding_left, 0, '- 10K : '+str(qty_t10k)+' x 10.000 = Rp. '+clean_number(total_t10k), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        qty_t20k = s['trx_top20k']
        total_t20k = str(int(qty_t20k) * 20000)
        pdf.cell(padding_left, 0,
                 '- 20K : '+str(qty_t20k)+' x 20.000 = Rp. '+clean_number(total_t20k), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        qty_t50k = s['trx_top50k']
        total_t50k = str(int(qty_t50k) * 50000)
        pdf.cell(padding_left, 0,
                 '- 50K : '+str(qty_t50k)+' x 50.000 = Rp. '+clean_number(total_t50k), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        qty_t100k = s['trx_top100k']
        total_t100k = str(int(qty_t100k) * 100000)
        pdf.cell(padding_left, 0,
                 '- 100K : '+str(qty_t100k)+' x 100.000 = Rp. '+clean_number(total_t100k), 0, 0, 'L')
        # if not _Common.BANKS[0]['STATUS']:
        #     pdf.ln(tiny_space)
        #     pdf.set_font(USED_FONT, '', line_size)
        #     qty_t200k = s['trx_top200k']
        #     total_t200k = str(int(qty_t200k) * 200000)
        #     pdf.cell(padding_left, 0,
        #              '- 200K : '+str(qty_t200k)+' x 200.000 = Rp. '+clean_number(total_t200k), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        qty_xdenom = s['trx_xdenom']
        amt_xdenom = s['amt_xdenom']
        pdf.cell(padding_left, 0, '- Other : '+str(qty_xdenom)+' -- Total = Rp. '+clean_number(amt_xdenom), 0, 0, 'L')
        pdf.ln(tiny_space+1)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, 'CARD UPDATE', 0, 0, 'L') 
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        adjust_slot1 = int(s['slot1']) - int(s['init_slot1'])
        pdf.cell(padding_left, 0,
                 '- Slot 1 : ' + str(s['init_slot1']) + ' + ' + str(adjust_slot1) + ' = ' + str(s['slot1']), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        adjust_slot2 = int(s['slot2']) - int(s['init_slot2'])
        pdf.cell(padding_left, 0,
                 '- Slot 2 : ' + str(s['init_slot2']) + ' + ' + str(adjust_slot2) + ' = ' + str(s['slot2']), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        adjust_slot3 = int(s['slot3']) - int(s['init_slot3'])
        pdf.cell(padding_left, 0,
                 '- Slot 3 : ' + str(s['init_slot3']) + ' + ' + str(adjust_slot3) + ' = ' + str(s['slot3']), 0, 0, 'L')
        pdf.ln(line_size+1)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, 'MDR Wallet : Rp. ' + clean_number(str(s['sam_1_balance'])), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, 'BNI Wallet : Rp. ' + clean_number(str(s['sam_2_balance'])), 0, 0, 'L')
        pdf.ln(line_size)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, 'Failed/Exceed TRX: Rp. ' + clean_number(str(s['failed_amount'])), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, 'PPOB Cash TRX: Rp. ' + clean_number(str(s['ppob_cash'])), 0, 0, 'L')
        pdf.set_font(USED_FONT, '', line_size+3)
        pdf.ln(tiny_space)
        # total_amount = str(int(s['all_amount']) + int(s['failed_amount']))
        # if total_amount == '0':
        #     total_amount = str(s['failed_amount'])
        pdf.cell(padding_left, 0, 'TOTAL CASH = Rp. ' + clean_number(str(s['all_cash'])), 0, 0, 'L')
        # End Layouting
        pdf_file = get_path(file_name+ext)
        pdf.output(pdf_file, 'F')
        # Print-out to printer
        for i in range(print_copy):
            print_result = _Printer.do_printout(pdf_file)
            LOGGER.debug((file_name, i+1, print_result))
            sleep(1)
        SPRINTTOOL_SIGNDLER.SIGNAL_ADMIN_PRINT_GLOBAL.emit('ADMIN_PRINT|DONE')
    except Exception as e:
        LOGGER.warning(str(e))
        SPRINTTOOL_SIGNDLER.SIGNAL_ADMIN_PRINT_GLOBAL.emit('ADMIN_PRINT|ERROR')
    finally:
        # Send To Backend
        _Common.upload_admin_access(struct_id, user, str(s.get('all_cash', '')), '0', s.get('card_adjustment', ''), json.dumps(s), s.get('trx_list', ''))
        mark_sync_collected_data(s)
        # save_receipt_local(struct_id, json.dumps(s), 'ACCESS_REPORT')
        del pdf


def start_admin_change_stock_print(struct_id):
    _Helper.get_thread().apply_async(admin_change_stock_print, (struct_id,))


def admin_change_stock_print(struct_id, ext='.pdf'):
    global GENERAL_TITLE
    pdf = None
    # Init Variables
    tiny_space = 3
    line_size = 7
    padding_left = 0
    print_copy = 2
    user = 'mdd_operator'
    s = False
    if _UserService.USER is not None:
        user = _UserService.USER['username']
    try:
        # paper_ = get_paper_size('\r\n'.join(p.keys()))
        GENERAL_TITLE = 'VM CHANGE CARD STOCK REPORT'
        pdf = GeneralPDF('P', 'mm', (80, 140))
        s = _Common.generate_stock_change_data()
        # LOGGER.info(('Registering New Font', font_path('UnispaceBold.ttf')))
        # pdf.add_font('UniSpace', '', font_path('UnispaceBold.ttf'), uni=True)
        pdf.add_page()
        file_name = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')+'-change-stock-'+user
        # Layouting
        pdf.cell(padding_left, 0, '_' * MAX_LENGTH, 0, 0, 'C')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, 'Tanggal : '+datetime.strftime(datetime.now(), '%d-%m-%Y')+'  Jam : ' +
                 datetime.strftime(datetime.now(), '%H:%M:%S'), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, 'Operator : ' + user + ' | ' + struct_id, 0, 0, 'L')
        # pdf.ln(tiny_space)
        # pdf.set_font(USED_FONT, '', line_size)
        # pdf.cell(padding_left, 0, 'TRX ID : '+struct_id, 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, '_' * MAX_LENGTH, 0, 0, 'C')
        pdf.ln(tiny_space+1)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, 'CARD STOCK', 0, 0, 'L') 
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        adjust_slot1 = int(s['slot1']) - int(s['init_slot1'])
        pdf.cell(padding_left, 0,
                 '- Slot 1 : ' + str(s['init_slot1']) + ' + ' + str(adjust_slot1) + ' = ' + str(s['slot1']), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        adjust_slot2 = int(s['slot2']) - int(s['init_slot2'])
        pdf.cell(padding_left, 0,
                 '- Slot 2 : ' + str(s['init_slot2']) + ' + ' + str(adjust_slot2) + ' = ' + str(s['slot2']), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        adjust_slot3 = int(s['slot3']) - int(s['init_slot3'])
        pdf.cell(padding_left, 0,
                 '- Slot 3 : ' + str(s['init_slot3']) + ' + ' + str(adjust_slot3) + ' = ' + str(s['slot3']), 0, 0, 'L')
        pdf.ln(line_size+3)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, 'MDR Wallet : Rp. ' + clean_number(str(s['sam_1_balance'])), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, 'BNI Wallet : Rp. ' + clean_number(str(s['sam_2_balance'])), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf_file = get_path(file_name+ext)
        pdf.output(pdf_file, 'F')
        # Print-out to printer
        for i in range(print_copy):
            print_result = _Printer.do_printout(pdf_file)
            LOGGER.debug((file_name, i+1, print_result))
            sleep(1)
        SPRINTTOOL_SIGNDLER.SIGNAL_ADMIN_PRINT_GLOBAL.emit('ADMIN_PRINT|DONE')
    except Exception as e:
        LOGGER.warning(str(e))
        SPRINTTOOL_SIGNDLER.SIGNAL_ADMIN_PRINT_GLOBAL.emit('ADMIN_PRINT|ERROR')
    finally:
        del pdf


def mark_sync_collected_data(s):
    if not _Common.empty(s):
        _DAO.custom_update(' UPDATE Transactions SET isCollected = 1 WHERE isCollected = 0 ')
        operator = 'OPERATOR'
        if _UserService.USER is not None:
            operator = _UserService.USER['first_name']
        # Reset Cash Log
        __update_cash_str = ' UPDATE Cash SET collectedAt = ' + str(_Helper.now()) + ', collectedUser = "' + str(operator) + \
            '"  WHERE collectedAt = 19900901 '
        # _KioskService.python_dump(str(__update_cash_str))
        __exec_cash_update = _DAO.custom_update(__update_cash_str)
        # _KioskService.python_dump(str(__exec_cash_update))
        # Reset Table Cashbox
        _DAO.truncate_cashbox()
        return True
    else:
        return False


def start_print_card_history(payload):
    _Helper.get_thread().apply_async(print_card_history, (payload,))


def print_card_history(payload):
    global GENERAL_TITLE, USE_FOOTER
    if _Helper.empty(_Common.LAST_CARD_LOG_HISTORY):
        return
    # Payload Must Contain Card Number, Bank Name, Balance
    payload = json.loads(payload)
    pdf = None
    # Init Variables
    tiny_space = 3.5
    line_size = 7
    padding_left = 0
    print_copy = 1
    ext = '.pdf'
    try:
        GENERAL_TITLE = 'PREPAID CARD LOG HISTORY'
        USE_FOOTER = False
        # paper_ = get_paper_size('\r\n'.join(p.keys()))
        pdf = GeneralPDF('P', 'mm', (80, 140))
        pdf.add_page()
        file_name = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')+'-CARDLOG-'+payload['bank_name']+'-'+payload['card_no']
        # Layouting
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, 'Tanggal : '+datetime.strftime(datetime.now(), '%d-%m-%Y')+'  Jam : ' +
                datetime.strftime(datetime.now(), '%H:%M:%S'), 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, 'No Kartu : ' + payload['card_no'], 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, 'Penerbit : Bank ' + payload['bank_name'], 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, '_' * MAX_LENGTH, 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, ' NO | TIME | TRX | AMOUNT | BALANCE', 0, 0, 'L')
        pdf.ln(1.5)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, '_' * MAX_LENGTH, 0, 0, 'L')
        #==================================== 
        # Looping Log Here
        # 'date': datetime.strptime(row[2], '%m%d%y').strftime('%Y-%m-%d'),
        # 'time': ':'.join(_Helper.strtolist(row[3])),
        # 'type': _Common.BRI_LOG_LEGEND.get(row[4], ''),
        # 'amount': row[5],
        # 'prev_balance': row[6],
        # 'last_balance': row[7]
        no = 0
        for log in _Common.LAST_CARD_LOG_HISTORY:
            no += 1
            content_row = ' | '.join([
                str(no).zfill(2),
                log['date'], 
                log['type'],
                clean_number(log['amount']), 
                clean_number(log['last_balance']), 
                ])
            pdf.ln(tiny_space)
            pdf.set_font(USED_FONT, '', line_size-1.5)
            pdf.cell(padding_left, 0, content_row, 0, 0, 'L')
            pdf.ln(2)
            pdf.set_font(USED_FONT, '', line_size-1.5)
            pdf.cell(padding_left, 0, (5*' ')+log['time'], 0, 0, 'L')
        #==================================== 
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, '_' * MAX_LENGTH, 0, 0, 'L')
        pdf.ln(tiny_space)
        pdf.set_font(USED_FONT, '', line_size)
        pdf.cell(padding_left, 0, 'Saldo Akhir : ' + clean_number(payload['last_balance']), 0, 0, 'L')
        pdf_file = get_path(file_name+ext)
        pdf.output(pdf_file, 'F')
        LOGGER.debug((file_name))
        # Print-out to printer
        for i in range(print_copy):
            print_ = _Printer.do_printout(pdf_file)
            # LOGGER.debug(("pyt : ({}) Printing to Default Printer : {}".format(str(i), str(print_))))
            print("pyt : ({}) Printing to Default Printer : {}".format(str(i), str(print_)))
            if '[ERROR]' in print_:
                break
            sleep(1)
    except Exception as e:
        LOGGER.warning(str(e))
    finally:
        _Common.LAST_CARD_LOG_HISTORY = []


class Ereceipt:
    header = []
    lines = []
    footer = [
        {
            'caption': '', #Padding To Body Receipt
            'alignment': 'center',
            'font': 'regular'
        }
    ]
    logo = 'tj-logo'
    filename = ''
    amount = ''
    trxid = ''
    company = ''
    data = None

    def __init__(self, logo, filename, headers_line):             
        self.logo = logo
        self.filename = filename
        if len(headers_line) > 0:
            for h in headers_line:
                self.header.append({
                    'caption': h,
                    'alignment': 'center',
                    'font': 'bold'
                })
        if len(_Common.CUSTOM_RECEIPT_TEXT) > 3:
            for c in _Common.CUSTOM_RECEIPT_TEXT.split('|'):
                self.footer.append({
                    'caption': c,
                    'alignment': 'center',
                    'font': 'regular'
                })
        self.footer.append({
            'caption': 'TERIMA KASIH',
            'alignment': 'center',
            'font': 'regular'
        })

    def set_line(self, text):
        self.lines.append({
            'caption': text,
            'alignment': 'left',
            'font': 'regular'
        })
    
    def set_amount(self, amount):
        self.amount = amount

    def set_company(self, company):
        self.company = company

    def set_trxid(self, trxid):
        self.trxid = trxid

    def generate(self):
        self.data = {
            'company': self.company,
            'logo': self.logo,
            'trxid': self.trxid,
            'amount': self.amount,
            'headers': self.header,
            'footers': self.footer,
            'lines': self.lines,
        }
        _Common.log_to_file(self.data, ERECEIPT_PATH, self.filename, '.json')
        return self.data
    

# ERECEIPT LAYOUT =============

def ereceipt_print_topup_trx(p, t, ext='.pdf'):
    if _Common.empty(p):
        LOGGER.warning(('Cannot Generate Receipt Data', 'GLOBAL_TRANSACTION_DATA', 'None'))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERECEIPT_ERROR')
        return
    pdf = None
    trxid = ''
    # failure = 'USER_CANCELLATION'
    cash = 0
    try:
        cash = int(p['payment_received'])
        file_name = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')+'-'+p['shop_type']
        logo = _Common.logo_theme(_Common.THEME_NAME.lower())
        pdf = Ereceipt(logo=logo, filename=file_name, headers_line=[
            _Common.THEME_NAME, 
            'TERMINAL : '+_Common.TID, 
            'LOKASI : '+_Common.KIOSK_NAME,
        ])
        trxid = p['shop_type']+str(p['epoch'])
        pdf.set_trxid(trxid)
        pdf.set_company(_Common.THEME_NAME.lower())
        pdf.set_amount(p['payment_received'])
        pdf.set_line('')
        pdf.set_line('Tanggal : '+datetime.strftime(datetime.now(), '%d-%m-%Y')+'       Jam : ' + datetime.strftime(datetime.now(), '%H:%M'))
        pdf.set_line('')
        if 'receipt_title' in p.keys():
            pdf.set_line(p['receipt_title'].upper())
        __title = t
        pdf.set_line(merge_text([__title, p['raw']['bank_name'], p['payment'].upper(), ]))
        pdf.set_line('')
        pdf.set_line('NO TRX    : '+trxid)
        if 'payment_error' not in p.keys() and 'process_error' not in p.keys():
            if 'topup_details' in p.keys():
                pdf.set_line('ISI ULANG  : Rp. ' + clean_number(p['denom']))
                pdf.set_line('BIAYA ADMIN: Rp. ' + clean_number(p['admin_fee']))
                pdf.set_line('TOTAL BAYAR: Rp. ' + clean_number(p['value']))
                if 'other_channel_topup' in p['topup_details'].keys():
                    if int(p['topup_details']['other_channel_topup']) > 0:
                        pdf.set_line('PENDING SALDO: Rp. ' + clean_number(str(p['topup_details']['other_channel_topup'])))
                pdf.set_line('NO. KARTU  : ' + p['topup_details']['card_no'])
                pdf.set_line('SALDO AWAL : Rp. ' + clean_number(p['raw']['prev_balance']))
                pdf.set_line('SALDO AKHIR: Rp. ' + clean_number(str(p['final_balance'])))
                if 'refund_status' in p.keys():
                    pdf.set_line('UANG DITERIMA: Rp. ' + clean_number(str(p['payment_received'])))
                    pdf.set_line('CARA KEMBALIAN: ' + _Common.serialize_refund(p['refund_channel']))
                    pdf.set_line('STATUS KEMBALIAN: ' + p['refund_number'] + ' ' + p['refund_status'])
                    pdf.set_line('NILAI KEMBALIAN: Rp. ' + clean_number(str(p['refund_amount'])))
                    fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                    if fee_refund_exist:
                        pdf.set_line('ADMIN KEMBALIAN: Rp. ' + clean_number(str(fee_refund)))
            else:
                pdf.set_line('NO. KARTU   : ' + p['raw']['card_no'])
                pdf.set_line('SISA SALDO  : Rp. ' + clean_number(p['raw']['prev_balance']))
                pdf.set_line('UANG DITERIMA: Rp. ' + clean_number(str(p['payment_received'])))
                if 'refund_status' in p.keys():
                    pdf.set_line('CARA KEMBALIAN: ' + _Common.serialize_refund(p['refund_channel']))
                    pdf.set_line('STATUS KEMBALIAN: ' + p['refund_number'] + ' ' + p['refund_status'])
                    pdf.set_line('NILAI KEMBALIAN: Rp. ' + clean_number(str(p['refund_amount'])))
                    fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                    if fee_refund_exist:
                        pdf.set_line('ADMIN KEMBALIAN: Rp. ' + clean_number(str(fee_refund)))
                elif 'pending_trx_code' in p.keys():
                    pdf.set_line('KODE ULANG : ' + p['pending_trx_code'])
                    pdf.set_line('DAPAT MELANJUTKAN TRANSAKSI KEMBALI')
                    pdf.set_line('PADA MENU CEK/LANJUT TRANSAKSI')
        else:
            pdf.set_line('NO. KARTU   : ' + p['raw']['card_no'])
            pdf.set_line('SISA SALDO  : Rp. ' + clean_number(p['raw']['prev_balance']))
            pdf.set_line('UANG DITERIMA: Rp. ' + clean_number(str(p['payment_received'])))
            if 'refund_status' in p.keys():
                pdf.set_line('CARA KEMBALIAN: ' + _Common.serialize_refund(p['refund_channel']))
                pdf.set_line('STATUS KEMBALIAN: ' + p['refund_number'] + ' ' + p['refund_status'])
                pdf.set_line('NILAI KEMBALIAN: Rp. ' + clean_number(str(p['refund_amount'])))
                fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                if fee_refund_exist:
                    pdf.set_line('ADMIN KEMBALIAN: Rp. ' + clean_number(str(fee_refund)))
            elif 'pending_trx_code' in p.keys():
                pdf.set_line('KODE ULANG : ' + p['pending_trx_code'])
                pdf.set_line('DAPAT MELANJUTKAN TRANSAKSI KEMBALI')
                pdf.set_line('PADA MENU CEK/LANJUT TRANSAKSI')
        # Send Print Data To DIVA Loyalty Service
        ereceipt_data = pdf.generate()
        status, response = _NetworkAccess.post_to_url(_Common.ERECEIPT_URL, ereceipt_data)
        if status == 200:
            output = response['response']
            if output['status'] == 0:
                SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERECEIPT_DONE|'+json.dumps(output))
            else:
                SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERECEIPT_ERROR')
        else:
            _Common.store_request_to_job(name=_Helper.whoami(), url=_Common.ERECEIPT_URL, payload=ereceipt_data)
            SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERECEIPT_ERROR')
    except Exception as e:
        LOGGER.warning(str(e))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERECEIPT_ERROR')
    finally:
        finalize_trx_process(trxid, p, cash)
        del pdf


def ereceipt_print_shop_trx(p, t, ext='.pdf'):
    if _Common.empty(p):
        LOGGER.warning(('Cannot Generate Receipt Data', 'GLOBAL_TRANSACTION_DATA', 'None'))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERECEIPT_ERROR')
        return
    pdf = None
    trxid = ''
    # failure = 'USER_CANCELLATION'
    cash = 0
    try:
        cash = int(p['payment_received'])
        file_name = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')+'-'+p['shop_type']
        logo = _Common.logo_theme(_Common.THEME_NAME.lower())
        pdf = Ereceipt(logo=logo, filename=file_name, headers_line=[
            _Common.THEME_NAME, 
            'TERMINAL : '+_Common.TID, 
            'LOKASI : '+_Common.KIOSK_NAME,
        ])
        trxid = p['shop_type']+str(p['epoch'])
        pdf.set_trxid(trxid)
        pdf.set_company(_Common.THEME_NAME.lower())
        pdf.set_amount(p['payment_received'])
        pdf.set_line('')
        pdf.set_line('Tanggal : '+datetime.strftime(datetime.now(), '%d-%m-%Y')+'       Jam : ' + datetime.strftime(datetime.now(), '%H:%M'))
        pdf.set_line('')
        __title = t
        if 'receipt_title' in p.keys():
            pdf.set_line(p['receipt_title'].upper())
        pdf.set_line(merge_text([__title, p['payment'].upper(), ]))
        pdf.set_line('NO TRX    : '+trxid)
        if 'payment_error' not in p.keys() and 'process_error' not in p.keys():
            pdf.set_line('TIPE KARTU  : ' + p['provider'])
            pdf.set_line('QTY KARTU   : ' + str(p['qty']))
            pdf.set_line(str(p['qty']) + ' x ' + clean_number(p['value']), 0, 0, 'R')
            if 'refund_status' in p.keys():
                pdf.set_line('UANG DITERIMA: Rp. ' + clean_number(str(p['payment_received'])))
                pdf.set_line('PENGEMBALIAN: ' + _Common.serialize_refund(p['refund_channel']))
                pdf.set_line('STATUS KEMBALIAN: ' + p['refund_number'] + ' ' + p['refund_status'])
                pdf.set_line('NILAI KEMBALIAN: Rp. ' + clean_number(str(p['refund_amount'])))
                fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                if fee_refund_exist:
                    pdf.set_line('ADMIN KEMBALIAN: Rp. ' + clean_number(str(fee_refund)))
            elif 'pending_trx_code' in p.keys():
                pdf.set_line('KODE ULANG : ' + p['pending_trx_code'])
                pdf.set_line('DAPAT MELANJUTKAN TRANSAKSI KEMBALI')
                pdf.set_line('PADA MENU CEK/LANJUT TRANSAKSI')
            pdf.set_line('')
            total_pay = str(int(int(p['value']) * int(p['qty'])))
            pdf.set_line('TOTAL BAYAR : Rp. ' + clean_number(total_pay))
        else:
            pdf.set_line('UANG DITERIMA : Rp. ' + clean_number(str(p['payment_received'])))
            if 'refund_status' in p.keys():
                pdf.set_line('CARA KEMBALIAN: ' + _Common.serialize_refund(p['refund_channel']))
                pdf.set_line('STATUS KEMBALIAN: ' + p['refund_number'] + ' ' + p['refund_status'])
                pdf.set_line('NILAI KEMBALIAN: Rp. ' + clean_number(str(p['refund_amount'])))
                fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                if fee_refund_exist:
                    pdf.set_line('ADMIN KEMBALIAN: Rp. ' + clean_number(str(fee_refund)))
            elif 'pending_trx_code' in p.keys():
                pdf.set_line('KODE ULANG : ' + p['pending_trx_code'])
                pdf.set_line('DAPAT MELANJUTKAN TRANSAKSI KEMBALI')
                pdf.set_line('PADA MENU CEK/LANJUT TRANSAKSI')
        # Send Print Data To DIVA Loyalty Service
        ereceipt_data = pdf.generate()
        status, response = _NetworkAccess.post_to_url(_Common.ERECEIPT_URL, ereceipt_data)
        if status == 200:
            output = response['response']
            if output['status'] == 0:
                SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERECEIPT_DONE|'+json.dumps(output))
            else:
                SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERECEIPT_ERROR')
        else:
            _Common.store_request_to_job(name=_Helper.whoami(), url=_Common.ERECEIPT_URL, payload=ereceipt_data)
            SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERECEIPT_ERROR')
    except Exception as e:
        LOGGER.warning(str(e))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERECEIPT_ERROR')
    finally:
        finalize_trx_process(trxid, p, cash)
        del pdf


def ereceipt_print_ppob_trx(p, t, ext='.pdf'):
    if _Common.empty(p):
        LOGGER.warning(('Cannot Generate Receipt Data', 'GLOBAL_TRANSACTION_DATA', 'None'))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERECEIPT_ERROR')
        return
    pdf = None
    trxid = ''
    # failure = 'USER_CANCELLATION'
    cash = 0
    try:
        cash = int(p['payment_received'])
        file_name = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')+'-'+p['shop_type']
        logo = _Common.logo_theme(_Common.THEME_NAME.lower())
        pdf = Ereceipt(logo=logo, filename=file_name, headers_line=[
            _Common.THEME_NAME, 
            'TERMINAL : '+_Common.TID, 
            'LOKASI : '+_Common.KIOSK_NAME,
        ])
        trxid = p['shop_type']+str(p['epoch'])
        pdf.set_trxid(trxid)
        pdf.set_company(_Common.THEME_NAME.lower())
        pdf.set_amount(p['payment_received'])
        pdf.set_line('')
        pdf.set_line('Tanggal : '+datetime.strftime(datetime.now(), '%d-%m-%Y')+'       Jam : ' + datetime.strftime(datetime.now(), '%H:%M'))
        pdf.set_line('')
        if 'receipt_title' in p.keys():
            pdf.set_line(p['receipt_title'].upper())
        __title = t
        pdf.set_line(merge_text([__title, p['payment'].upper(), ]))
        pdf.set_line('NO TRX    : '+trxid)
        pdf.set_line('PROVIDER  : ' + str(p['provider']))
        pdf.set_line('MSISDN    : ' + str(p['msisdn']))
        if 'ppob_details' in p.keys() and 'payment_error' not in p.keys() and 'process_error' not in p.keys():
            if p['ppob_mode'] == 'tagihan':
                pdf.set_line('PELANGGAN  : Rp. ' + str(p['customer']))
                pdf.set_line('TAGIHAN    : Rp. ' + clean_number(str(p['value'])))
                pdf.set_line('BIAYA ADMIN: Rp. ' + clean_number(str(p['admin_fee'])))
            else:
                pdf.set_line('JUMLAH     : ' + str(p['qty']))
                pdf.set_line('HARGA/UNIT : Rp. ' + clean_number(str(p['value'])))
                if 'sn' in p['ppob_details'].keys():
                    label_sn = 'S/N '
                    if p['category'].lower() == 'listrik':
                        label_sn = 'TOKEN '
                        if str(p['ppob_details']['sn']) == '[]':
                            pdf.set_line('TOKEN DALAM PROSES, HUBUNGI LAYANAN PELANGGAN')
                        else:    
                            pdf.set_line(label_sn + str(p['ppob_details']['sn'][:24]))
                    else:
                        pdf.set_line(label_sn + str(p['ppob_details']['sn'][:24]))
            if 'refund_status' in p.keys():
                pdf.set_line('UANG DITERIMA: Rp. ' + clean_number(str(p['payment_received'])))
                pdf.set_line('CARA KEMBALIAN: ' + _Common.serialize_refund(p['refund_channel']))
                pdf.set_line('STATUS KEMBALIAN: ' + p['refund_number'] + ' ' + p['refund_status'])
                pdf.set_line('NILAI KEMBALIAN: Rp. ' + clean_number(str(p['refund_amount'])))
                fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                if fee_refund_exist:
                    pdf.set_line('ADMIN KEMBALIAN: Rp. ' + clean_number(str(fee_refund)))
            elif 'pending_trx_code' in p.keys():
                pdf.set_line('KODE ULANG : ' + p['pending_trx_code'])
                pdf.set_line('DAPAT MELANJUTKAN TRANSAKSI KEMBALI')
                pdf.set_line('PADA MENU CEK/LANJUT TRANSAKSI')
            total_pay = str(int(int(p['value']) * int(p['qty'])))
            pdf.set_line('TOTAL BAYAR : Rp. ' + clean_number(total_pay))
        else:
            pdf.set_line('UANG DITERIMA : Rp. ' + clean_number(str(p['payment_received'])))
            if 'refund_status' in p.keys():
                pdf.set_line('CARA KEMBALIAN: ' + _Common.serialize_refund(p['refund_channel']))
                pdf.set_line('STATUS KEMBALIAN: ' + p['refund_number'] + ' ' + p['refund_status'])
                pdf.set_line('NILAI KEMBALIAN: Rp. ' + clean_number(str(p['refund_amount'])))
                fee_refund_exist, fee_refund = validate_refund_fee(p['refund_channel'])
                if fee_refund_exist:
                    pdf.set_line('ADMIN KEMBALIAN: Rp. ' + clean_number(str(fee_refund)))
            elif 'pending_trx_code' in p.keys():
                pdf.set_line('KODE ULANG : ' + p['pending_trx_code'])
                pdf.set_line('DAPAT MELANJUTKAN TRANSAKSI KEMBALI')
                pdf.set_line('PADA MENU CEK/LANJUT TRANSAKSI')
        # Send Print Data To DIVA Loyalty Service
        ereceipt_data = pdf.generate()
        status, response = _NetworkAccess.post_to_url(_Common.ERECEIPT_URL, ereceipt_data)
        if status == 200:
            output = response['response']
            if output['status'] == 0:
                SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERECEIPT_DONE|'+json.dumps(output))
            else:
                SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERECEIPT_ERROR')
        else:
            _Common.store_request_to_job(name=_Helper.whoami(), url=_Common.ERECEIPT_URL, payload=ereceipt_data)
            SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERECEIPT_ERROR')
    except Exception as e:
        LOGGER.warning(str(e))
        SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.emit('SALEPRINT|ERECEIPT_ERROR')
    finally:
        finalize_trx_process(trxid, p, cash)
        del pdf


