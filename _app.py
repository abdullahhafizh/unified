__author__ = "wahyudi@multidaya.id"

import os
from re import M
import sys
from PyQt5.QtCore import QUrl, QObject, pyqtSlot, QTranslator, Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQuick import QQuickView
import logging
import logging.handlers
import subprocess
from _cConfig import _ConfigParser, _Common
from _nNetwork import _HTTPAccess
from _dDB import _Database
from _sService import _KioskService
from _sService import _UserService
from _tTools import _Helper
from _sSync import _Sync
from _dDevice import _EDC
from _dDevice import _QPROX
from _dDevice import _CD
from _dDevice import _Printer
from time import sleep
from _tTools import _CheckIn
from _tTools import _SalePrintTool
from _sService import _ProductService
from _dDevice import _BILL
from _sService import _TopupService
from _sService import _SettlementService
# from _sService import _UpdateAppService
from _sService import _PPOBService
from _sService import _QRPaymentService
from _sService import _GeneralPaymentService
from _sService import _AudioService
# from _mModule import _MainService
import json
import sentry_sdk

if _Common.IS_WINDOWS:
    import wmi

if _Common.chatbot_feature():
    from _sService import _ChatbotService



print("""
        Unik Vending Kiosk
    App Ver: """ + _Common.VERSION + """
Powered By: PT. MultiDaya Dinamika
              -2022-
""")

# Set Default Screen Frame Size
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080


class SlotHandler(QObject):
    __qualname__ = 'SlotHandler'

    # def set_language(self, s):
    #     print("pyt: selected_language ", s)
    #     translator.load(path + s)
    # set_language = pyqtSlot(str)(set_language)

    def get_file_list(self, dir_):
        _KioskService.get_file_list(dir_=dir_)
    get_file_list = pyqtSlot(str)(get_file_list)

    def post_tvc_log(self, media):
        _KioskService.post_tvc_log(media)
    post_tvc_log = pyqtSlot(str)(post_tvc_log)

    def get_gui_version(self):
        _KioskService.get_gui_version()
    get_gui_version = pyqtSlot()(get_gui_version)

    def get_kiosk_name(self):
        _KioskService.get_kiosk_name()
    get_kiosk_name = pyqtSlot()(get_kiosk_name)

    def post_gui_version(self):
        _KioskService.post_gui_version()
    post_gui_version = pyqtSlot()(post_gui_version)

    def set_tvc_player(self, command):
        set_tvc_player(command)
    set_tvc_player = pyqtSlot(str)(set_tvc_player)

    def create_sale_edc(self, amount):
        _EDC.create_sale_edc(amount=amount)
    create_sale_edc = pyqtSlot(str)(create_sale_edc)

    def start_get_payments(self):
        _KioskService.start_get_payments()
    start_get_payments = pyqtSlot()(start_get_payments)

    # def start_init_qprox_config(self):
    #     _QPROX.start_init_config()
    # start_init_qprox_config = pyqtSlot()(start_init_qprox_config)

    def start_debit_qprox(self, amount):
        _QPROX.start_debit_qprox(amount)
    start_debit_qprox = pyqtSlot(str)(start_debit_qprox)

    def start_auth_ka_mandiri(self):
        _QPROX.start_auth_ka_mandiri()
    start_auth_ka_mandiri = pyqtSlot()(start_auth_ka_mandiri)

    def start_check_card_balance(self):
        _QPROX.start_check_card_balance()
    start_check_card_balance = pyqtSlot()(start_check_card_balance)

    def start_topup_offline_mandiri(self, amount, trxid):
        _QPROX.start_topup_offline_mandiri(amount, trxid)
    start_topup_offline_mandiri = pyqtSlot(str, str)(start_topup_offline_mandiri)

    def start_ka_info(self):
        _QPROX.start_ka_info()
    start_ka_info = pyqtSlot()(start_ka_info)

    def start_create_online_info_mandiri(self):
        _QPROX.start_create_online_info_mandiri()
    start_create_online_info_mandiri = pyqtSlot()(start_create_online_info_mandiri)

    def start_init_online_mandiri(self):
        _QPROX.start_init_online_mandiri()
    start_init_online_mandiri = pyqtSlot()(start_init_online_mandiri)

    def start_disconnect_edc(self):
        _EDC.start_disconnect_edc()
    start_disconnect_edc = pyqtSlot()(start_disconnect_edc)

    def start_disconnect_qprox(self):
        _QPROX.start_disconnect_qprox()
    start_disconnect_qprox = pyqtSlot()(start_disconnect_qprox)

    def start_default_print(self, path):
        _Printer.start_default_print(path)
    start_default_print = pyqtSlot(str)(start_default_print)

    def start_get_kiosk_status(self):
        _KioskService.start_get_kiosk_status()
    start_get_kiosk_status = pyqtSlot()(start_get_kiosk_status)

    def start_get_price_setting(self):
        _KioskService.start_get_price_setting()
    start_get_price_setting = pyqtSlot()(start_get_price_setting)

    def start_restart_mdd_service(self):
        _KioskService.start_restart_mdd_service()
    start_restart_mdd_service = pyqtSlot()(start_restart_mdd_service)

    def start_safely_shutdown(self, mode):
        safely_shutdown(mode)
    start_safely_shutdown = pyqtSlot(str)(start_safely_shutdown)

    def start_get_cash_data(self):
        _KioskService.start_get_cash_data()
    start_get_cash_data = pyqtSlot()(start_get_cash_data)

    def start_begin_collect_cash(self):
        _KioskService.start_begin_collect_cash()
    start_begin_collect_cash = pyqtSlot()(start_begin_collect_cash)

    def start_idle_mode(self):
        _Sync.start_idle_mode()
    start_idle_mode = pyqtSlot()(start_idle_mode)

    def stop_idle_mode(self):
        _Sync.stop_idle_mode()
    stop_idle_mode = pyqtSlot()(stop_idle_mode)

    def start_get_settlement(self):
        _EDC.start_get_settlement()
    start_get_settlement = pyqtSlot()(start_get_settlement)

    def start_edc_settlement(self):
        _EDC.start_edc_settlement()
    start_edc_settlement = pyqtSlot()(start_edc_settlement)

    def start_void_data(self):
        _EDC.start_void_data()
    start_void_data = pyqtSlot()(start_void_data)

    def start_dummy_edc_receipt(self):
        _EDC.start_dummy_edc_receipt()
    start_dummy_edc_receipt = pyqtSlot()(start_dummy_edc_receipt)

    def start_check_booking_code(self, param):
        _CheckIn.start_check_booking_code(param)
    start_check_booking_code = pyqtSlot(str)(start_check_booking_code)

    def start_get_boarding_pass(self, param):
        _CheckIn.start_get_boarding_pass(param)
    start_get_boarding_pass = pyqtSlot(str)(start_get_boarding_pass)

    def start_get_admin_key(self):
        _KioskService.start_get_admin_key()
    start_get_admin_key = pyqtSlot()(start_get_admin_key)

    def start_check_wallet(self, amount):
        _KioskService.start_check_wallet(amount)
    start_check_wallet = pyqtSlot(str)(start_check_wallet)

    def kiosk_get_product_stock(self):
        _KioskService.kiosk_get_product_stock()
    kiosk_get_product_stock = pyqtSlot()(kiosk_get_product_stock)

    def start_sync_product_stock(self):
        _Sync.start_sync_product_stock()
    start_sync_product_stock = pyqtSlot()(start_sync_product_stock)

    def start_set_direct_price(self, price):
        _BILL.start_set_direct_price(price)
    start_set_direct_price = pyqtSlot(str)(start_set_direct_price)

    def start_set_direct_price_with_current(self, current, price):
        _BILL.start_set_direct_price_with_current(current, price)
    start_set_direct_price_with_current = pyqtSlot(str, str)(start_set_direct_price_with_current)

    def start_multiple_eject(self, attempt, multiply):
        _CD.start_multiple_eject(attempt, multiply)
    start_multiple_eject = pyqtSlot(str, str)(start_multiple_eject)
    
    def start_card_validate_redeem(self, attempt, multiply, vcode):
        _CD.start_card_validate_redeem(attempt, multiply, vcode)
    start_card_validate_redeem = pyqtSlot(str, str, str)(start_card_validate_redeem)

    def start_store_transaction_global(self, param):
        _KioskService.start_store_transaction_global(param)
    start_store_transaction_global = pyqtSlot(str)(start_store_transaction_global)

    def start_kiosk_get_topup_amount(self):
        _KioskService.start_kiosk_get_topup_amount()
    start_kiosk_get_topup_amount = pyqtSlot()(start_kiosk_get_topup_amount)

    def start_get_topup_readiness(self):
        _TopupService.start_get_topup_readiness()
    start_get_topup_readiness = pyqtSlot()(start_get_topup_readiness)

    def start_check_topup_readiness(self):
        _TopupService.start_check_topup_readiness()
    start_check_topup_readiness = pyqtSlot()(start_check_topup_readiness)

    def start_sale_print_global(self):
        _SalePrintTool.start_sale_print_global()
    start_sale_print_global = pyqtSlot()(start_sale_print_global)

    def start_topup_offline_bni(self, amount, trxid):
        _QPROX.start_topup_offline_bni(amount, trxid)
    start_topup_offline_bni = pyqtSlot(str, str)(start_topup_offline_bni)

    def start_get_multiple_eject_status(self):
        _CD.start_get_multiple_eject_status()
    start_get_multiple_eject_status = pyqtSlot()(start_get_multiple_eject_status)

    def create_sale_edc_with_struct_id(self, amount, trxid):
        _EDC.create_sale_edc_with_struct_id(amount, trxid)
    create_sale_edc_with_struct_id = pyqtSlot(str, str)(create_sale_edc_with_struct_id)

    def start_store_topup_transaction(self, param):
        _KioskService.start_store_topup_transaction(param)
    start_store_topup_transaction = pyqtSlot(str)(start_store_topup_transaction)

    def get_kiosk_login(self, username, password):
        _UserService.get_kiosk_login(username, password)
    get_kiosk_login = pyqtSlot(str, str)(get_kiosk_login)

    def get_kiosk_logout(self):
        _UserService.get_kiosk_logout()
    get_kiosk_logout = pyqtSlot()(get_kiosk_logout)

    def kiosk_get_machine_summary(self):
        _KioskService.kiosk_get_machine_summary()
    kiosk_get_machine_summary = pyqtSlot()(kiosk_get_machine_summary)

    def start_change_product_stock(self, payload):
        _ProductService.start_change_product_stock(payload)
    start_change_product_stock = pyqtSlot(str)(start_change_product_stock)

    def start_bill_receive_note(self, trxid):
        _BILL.start_bill_receive_note(trxid)
    start_bill_receive_note = pyqtSlot(str)(start_bill_receive_note)

    def stop_bill_receive_note(self, trxid):
        _BILL.stop_bill_receive_note(trxid)
    stop_bill_receive_note = pyqtSlot(str)(stop_bill_receive_note)

    def start_get_status_bill(self):
        _BILL.start_get_status_bill()
    start_get_status_bill = pyqtSlot()(start_get_status_bill)

    def start_do_topup_deposit_bni(self, slot):
        _TopupService.start_do_topup_deposit_bni(slot)
    start_do_topup_deposit_bni = pyqtSlot(str)(start_do_topup_deposit_bni)

    def start_define_topup_slot_bni(self):
        _TopupService.start_define_topup_slot_bni()
    start_define_topup_slot_bni = pyqtSlot()(start_define_topup_slot_bni)

    def start_reset_bill(self):
        _BILL.start_reset_bill()
    start_reset_bill = pyqtSlot()(start_reset_bill)

    def start_upload_device_state(self, device, state):
        _Common.start_upload_device_state(device, state)
    start_upload_device_state = pyqtSlot(str, str)(start_upload_device_state)

    def start_generate_cash_collection_event(self, struct_id):
        _SalePrintTool.start_generate_cash_collection_event(struct_id)
    start_generate_cash_collection_event = pyqtSlot(str)(start_generate_cash_collection_event)

    def start_admin_change_stock_print(self, struct_id):
        _SalePrintTool.start_admin_change_stock_print(struct_id)
    start_admin_change_stock_print = pyqtSlot(str)(start_admin_change_stock_print)

    def start_reprint_global(self):
        _SalePrintTool.start_reprint_global()
    start_reprint_global = pyqtSlot()(start_reprint_global)

    # def start_manual_trigger_topup_bni(self):
    #     _Sync.start_manual_trigger_topup_bni()
    # start_manual_trigger_topup_bni = pyqtSlot()(start_manual_trigger_topup_bni)

    def start_master_activation_bni(self):
        _TopupService.start_master_activation_bni()
    start_master_activation_bni = pyqtSlot()(start_master_activation_bni)

    def start_slave_activation_bni(self):
        _TopupService.start_slave_activation_bni()
    start_slave_activation_bni = pyqtSlot()(start_slave_activation_bni)

    def bni_reset_update_balance_master(self):
        _TopupService.bni_reset_update_balance_master()
    bni_reset_update_balance_master = pyqtSlot()(bni_reset_update_balance_master)

    def bni_reset_update_balance_slave(self):
        _TopupService.bni_reset_update_balance_slave()
    bni_reset_update_balance_slave = pyqtSlot()(bni_reset_update_balance_slave)

    def retry_store_transaction_global(self):
        _KioskService.retry_store_transaction_global()
    retry_store_transaction_global = pyqtSlot()(retry_store_transaction_global)

    def kiosk_get_cd_readiness(self):
        _CD.kiosk_get_cd_readiness()
    kiosk_get_cd_readiness = pyqtSlot()(kiosk_get_cd_readiness)

    def user_action_log(self, log):
        _KioskService.user_action_log(log)
    user_action_log = pyqtSlot(str)(user_action_log)

    def system_action_log(self, log, level):
        _KioskService.system_action_log(log, level)
    system_action_log = pyqtSlot(str, str)(system_action_log)

    def python_dump(self, log):
        _KioskService.python_dump(log)
    python_dump = pyqtSlot(str)(python_dump)

    def start_do_mandiri_topup_settlement(self):
        _SettlementService.start_do_mandiri_topup_settlement()
    start_do_mandiri_topup_settlement = pyqtSlot()(start_do_mandiri_topup_settlement)

    def start_dummy_mandiri_topup_settlement(self):
        _SettlementService.start_dummy_mandiri_topup_settlement()
    start_dummy_mandiri_topup_settlement = pyqtSlot()(start_dummy_mandiri_topup_settlement)

    def start_reset_mandiri_settlement(self):
        _SettlementService.start_reset_mandiri_settlement()
    start_reset_mandiri_settlement = pyqtSlot()(start_reset_mandiri_settlement)

    def start_validate_update_balance(self):
        _SettlementService.start_validate_update_balance()
    start_validate_update_balance = pyqtSlot()(start_validate_update_balance)

    def start_check_bni_deposit(self):
        _Sync.start_check_bni_deposit()
    start_check_bni_deposit = pyqtSlot()(start_check_bni_deposit)

    # def start_do_update(self):
    #     _UpdateAppService.start_do_update()
    # start_do_update = pyqtSlot()(start_do_update)

    def start_get_ppob_product(self):
        _PPOBService.start_get_ppob_product()
    start_get_ppob_product = pyqtSlot()(start_get_ppob_product)

    def start_kiosk_get_payment_setting(self):
        _KioskService.start_kiosk_get_payment_setting()
    start_kiosk_get_payment_setting = pyqtSlot()(start_kiosk_get_payment_setting)

    def start_define_ads(self):
        _KioskService.start_define_ads()
    start_define_ads = pyqtSlot()(start_define_ads)

    def start_check_ppob_product(self, msisdn, product_id):
        _PPOBService.start_check_ppob_product(msisdn, product_id)
    start_check_ppob_product = pyqtSlot(str, str)(start_check_ppob_product)

    def start_do_pay_ppob(self, payload):
        _PPOBService.start_do_pay_ppob(payload)
    start_do_pay_ppob = pyqtSlot(str)(start_do_pay_ppob)

    def start_do_topup_ppob(self, payload):
        _PPOBService.start_do_topup_ppob(payload)
    start_do_topup_ppob = pyqtSlot(str)(start_do_topup_ppob)

    def start_check_status_trx(self, reff_no):
        _PPOBService.start_check_status_trx(reff_no)
    start_check_status_trx = pyqtSlot(str)(start_check_status_trx)

    def start_get_qr_gopay(self, payload):
        _QRPaymentService.start_get_qr_gopay(payload)
    start_get_qr_gopay = pyqtSlot(str)(start_get_qr_gopay)

    def start_get_qr_dana(self, payload):
        _QRPaymentService.start_get_qr_dana(payload)
    start_get_qr_dana = pyqtSlot(str)(start_get_qr_dana)

    def start_get_qr_ovo(self, payload):
        _QRPaymentService.start_get_qr_ovo(payload)
    start_get_qr_ovo = pyqtSlot(str)(start_get_qr_ovo)

    def start_get_qr_linkaja(self, payload):
        _QRPaymentService.start_get_qr_linkaja(payload)
    start_get_qr_linkaja = pyqtSlot(str)(start_get_qr_linkaja)

    def start_get_qr_jakone(self, payload):
        _QRPaymentService.start_get_qr_jakone(payload)
    start_get_qr_jakone = pyqtSlot(str)(start_get_qr_jakone)

    def start_do_check_jakone_qr(self, payload):
        _QRPaymentService.start_do_check_jakone_qr(payload)
    start_do_check_jakone_qr = pyqtSlot(str)(start_do_check_jakone_qr)

    def start_do_check_gopay_qr(self, payload):
        _QRPaymentService.start_do_check_gopay_qr(payload)
    start_do_check_gopay_qr = pyqtSlot(str)(start_do_check_gopay_qr)

    def start_do_check_dana_qr(self, payload):
        _QRPaymentService.start_do_check_dana_qr(payload)
    start_do_check_dana_qr = pyqtSlot(str)(start_do_check_dana_qr)

    def start_do_check_ovo_qr(self, payload):
        _QRPaymentService.start_do_check_ovo_qr(payload)
    start_do_check_ovo_qr = pyqtSlot(str)(start_do_check_ovo_qr)

    def start_do_check_linkaja_qr(self, payload):
        _QRPaymentService.start_do_check_linkaja_qr(payload)
    start_do_check_linkaja_qr = pyqtSlot(str)(start_do_check_linkaja_qr)

    def start_do_pay_ovo_qr(self, payload):
        _QRPaymentService.start_do_pay_ovo_qr(payload)
    start_do_pay_ovo_qr = pyqtSlot(str)(start_do_pay_ovo_qr)

    def start_confirm_ovo_qr(self, payload):
        _QRPaymentService.start_confirm_ovo_qr(payload)
    start_confirm_ovo_qr = pyqtSlot(str)(start_confirm_ovo_qr)

    def start_check_voucher(self, voucher):
        _ProductService.start_check_voucher(voucher)
    start_check_voucher = pyqtSlot(str)(start_check_voucher)

    def start_use_voucher(self, voucher, reff_no):
        _ProductService.start_use_voucher(voucher, reff_no)
    start_use_voucher = pyqtSlot(str, str)(start_use_voucher)

    def start_get_qr_global(self, payload):
        _QRPaymentService.start_get_qr_global(payload)
    start_get_qr_global = pyqtSlot(str)(start_get_qr_global)

    def start_direct_store_transaction_data(self, payload):
        _KioskService.start_direct_store_transaction_data(payload)
    start_direct_store_transaction_data = pyqtSlot(str)(start_direct_store_transaction_data)

    def start_check_diva_balance(self, username):
        _PPOBService.start_check_diva_balance(username)
    start_check_diva_balance = pyqtSlot(str)(start_check_diva_balance)

    def start_global_refund_balance(self, payload):
        _PPOBService.start_global_refund_balance(payload)
    start_global_refund_balance = pyqtSlot(str)(start_global_refund_balance)

    def start_update_balance_online(self, bank):
        _TopupService.start_update_balance_online(bank)
    start_update_balance_online = pyqtSlot(str)(start_update_balance_online)

    def start_fake_update_dki(self, card_no, amount):
        _QPROX.start_fake_update_dki(card_no, amount)
    start_fake_update_dki = pyqtSlot(str, str)(start_fake_update_dki)

    def start_log_book_cash(self, pid, amount):
        _BILL.start_log_book_cash(pid, amount)
    start_log_book_cash = pyqtSlot(str, str)(start_log_book_cash)

    def start_trigger_global_refund(self, payload):
        _PPOBService.start_trigger_global_refund(payload)
    start_trigger_global_refund = pyqtSlot(str)(start_trigger_global_refund)

    def start_do_force_topup_bni(self):
        _TopupService.start_do_force_topup_bni()
    start_do_force_topup_bni = pyqtSlot()(start_do_force_topup_bni)

    def start_mandiri_update_schedule(self):
        _SettlementService.start_trigger_mandiri_sam_update()
    start_mandiri_update_schedule = pyqtSlot()(start_mandiri_update_schedule)

    def start_reset_receipt_count(self, count):
        _KioskService.start_reset_receipt_count(count)
    start_reset_receipt_count = pyqtSlot(str)(start_reset_receipt_count)

    def start_trigger_edc_settlement(self):
        _SettlementService.start_trigger_edc_settlement()
    start_trigger_edc_settlement = pyqtSlot()(start_trigger_edc_settlement)

    def start_cancel_qr_global(self, trx_id):
        _QRPaymentService.start_cancel_qr_global(trx_id)
    start_cancel_qr_global = pyqtSlot(str)(start_cancel_qr_global)

    def start_confirm_qr_payment(self):
        _QRPaymentService.start_confirm_qr_payment()
    start_confirm_qr_payment = pyqtSlot()(start_confirm_qr_payment)

    def start_get_refunds(self):
        _KioskService.start_get_refunds()
    start_get_refunds = pyqtSlot()(start_get_refunds)

    def start_direct_sale_print_global(self, payload):
        _SalePrintTool.start_direct_sale_print_global(payload)
    start_direct_sale_print_global = pyqtSlot(str)(start_direct_sale_print_global)
    
    def start_finalise_transaction(self, payload):
        _SalePrintTool.start_finalise_transaction(payload)
    start_finalise_transaction = pyqtSlot(str)(start_finalise_transaction)
    
    def start_push_pending_trx_global(self, payload):
        _SalePrintTool.start_push_pending_trx_global(payload)
    start_push_pending_trx_global = pyqtSlot(str)(start_push_pending_trx_global)

    def start_direct_sale_print_ereceipt(self, payload):
        _SalePrintTool.start_direct_sale_print_ereceipt(payload)
    start_direct_sale_print_ereceipt = pyqtSlot(str)(start_direct_sale_print_ereceipt)

    def start_topup_mandiri_correction(self, amount, trxid):
        _QPROX.start_topup_mandiri_correction(amount, trxid)
    start_topup_mandiri_correction = pyqtSlot(str, str)(start_topup_mandiri_correction)
    
    def start_topup_bni_correction(self, amount, trxid):
        _QPROX.start_topup_bni_correction(amount, trxid)
    start_topup_bni_correction = pyqtSlot(str, str)(start_topup_bni_correction)

    def start_check_online_topup(self, mode, payload):
        _TopupService.start_check_online_topup(mode, payload)
    start_check_online_topup = pyqtSlot(str, str)(start_check_online_topup)

    def start_topup_online_bri(self, cardno, amount, trxid):
        _TopupService.start_topup_online_bri(cardno, amount, trxid)
    start_topup_online_bri = pyqtSlot(str, str, str)(start_topup_online_bri)

    def start_do_c2c_update_fee(self):
        _SettlementService.start_do_c2c_update_fee()
    start_do_c2c_update_fee = pyqtSlot()(start_do_c2c_update_fee)

    def start_do_topup_deposit_mandiri(self):
        _TopupService.start_do_topup_deposit_mandiri()
    start_do_topup_deposit_mandiri = pyqtSlot()(start_do_topup_deposit_mandiri)

    def start_get_card_history(self, bank):
        _QPROX.start_get_card_history(bank)
    start_get_card_history = pyqtSlot(str)(start_get_card_history)
    
    def start_enable_reader_dump(self):
        _QPROX.start_enable_reader_dump()
    start_enable_reader_dump = pyqtSlot()(start_enable_reader_dump)
    
    def start_disable_reader_dump(self):
        _QPROX.start_disable_reader_dump()
    start_disable_reader_dump = pyqtSlot()(start_disable_reader_dump)
    
    def start_reset_reader_contact(self):
        _QPROX.start_reset_reader_contact()
    start_reset_reader_contact = pyqtSlot()(start_reset_reader_contact)

    def start_print_card_history(self, payload):
        _SalePrintTool.start_print_card_history(payload)
    start_print_card_history = pyqtSlot(str)(start_print_card_history)

    def start_check_mandiri_deposit(self):
        _SettlementService.start_check_mandiri_deposit()
    start_check_mandiri_deposit = pyqtSlot()(start_check_mandiri_deposit)

    def start_mandiri_c2c_force_settlement(self, amount, trxid):
        _QPROX.start_mandiri_c2c_force_settlement(amount, trxid)
    start_mandiri_c2c_force_settlement = pyqtSlot(str, str)(start_mandiri_c2c_force_settlement)

    def start_topup_online_dki(self, card_no, amount, trxid):
        _TopupService.start_topup_online_dki(card_no, amount, trxid)
    start_topup_online_dki = pyqtSlot(str, str, str)(start_topup_online_dki)

    def start_topup_online_bca(self, cardno, amount, trxid):
        _TopupService.start_topup_online_bca(cardno, amount, trxid)
    start_topup_online_bca = pyqtSlot(str, str, str)(start_topup_online_bca)
    
    def start_retry_topup_online_bca(self, amount, trxid):
        _TopupService.start_retry_topup_online_bca(amount, trxid)
    start_retry_topup_online_bca = pyqtSlot(str, str)(start_retry_topup_online_bca)
    
    def start_retry_topup_online_bri(self, amount, trxid):
        _TopupService.start_retry_topup_online_bri(amount, trxid)
    start_retry_topup_online_bri = pyqtSlot(str, str)(start_retry_topup_online_bri)
    
    def start_retry_topup_online_dki(self, amount, trxid):
        _TopupService.start_retry_topup_online_dki(amount, trxid)
    start_retry_topup_online_dki = pyqtSlot(str, str)(start_retry_topup_online_dki)
    
    def start_trigger_explorer(self):
        _KioskService.start_trigger_explorer()
    start_trigger_explorer = pyqtSlot()(start_trigger_explorer)
    
    def start_do_check_customer(self, payload, mode):
        _PPOBService.start_do_check_customer(payload, mode)
    start_do_check_customer = pyqtSlot(str, str)(start_do_check_customer)
    
    def start_sync_topup_amount(self):
        _Sync.start_sync_topup_amount()
    start_sync_topup_amount = pyqtSlot()(start_sync_topup_amount)
    
    def start_check_detail_trx_status(self, payload, mode):
        _PPOBService.start_check_detail_trx_status(payload, mode)
    start_check_detail_trx_status = pyqtSlot(str, str)(start_check_detail_trx_status)
    
    def start_do_inquiry_trx(self, payload):
        _PPOBService.start_do_inquiry_trx(payload)
    start_do_inquiry_trx = pyqtSlot(str)(start_do_inquiry_trx)
    
    def start_use_pending_code(self, pending_code, reff_no):
        _KioskService.start_use_pending_code(pending_code, reff_no)
    start_use_pending_code = pyqtSlot(str, str)(start_use_pending_code)

    def start_play_audio(self, track):
        _AudioService.start_play_audio(track)
    start_play_audio = pyqtSlot(str)(start_play_audio)
    
    # def start_trigger_stop_audio(self):
    #     _AudioService.start_trigger_stop_audio()
    # start_trigger_stop_audio = pyqtSlot()(start_trigger_stop_audio)
    
    def start_update_usage_retry_code(self, trxid):
        _Common.start_update_usage_retry_code(trxid)
    start_update_usage_retry_code = pyqtSlot(str)(start_update_usage_retry_code)
    
    def start_deposit_update_balance(self, bank):
        _TopupService.start_deposit_update_balance(bank)
    start_deposit_update_balance = pyqtSlot(str)(start_deposit_update_balance)
    
    def start_check_payment_status(self, mode):
        _QRPaymentService.start_check_payment_status(mode)
    start_check_payment_status = pyqtSlot(str)(start_check_payment_status)
    
    def start_do_print_qr_receipt(self, mode):
        _QRPaymentService.start_do_print_qr_receipt(mode)
    start_do_print_qr_receipt = pyqtSlot(str)(start_do_print_qr_receipt)

    def start_do_inquiry_promo(self, payload):
        _PPOBService.start_do_inquiry_promo(payload)
    start_do_inquiry_promo = pyqtSlot(str)(start_do_inquiry_promo)
    
    def start_do_confirm_promo(self, payload):
        _PPOBService.start_do_confirm_promo(payload)
    start_do_confirm_promo = pyqtSlot(str)(start_do_confirm_promo)
    
    def start_startup_task(self):
        start_startup_task()
    start_startup_task = pyqtSlot()(start_startup_task) 
    
    def start_recheck_bni_sam_balance(self):
        _QPROX.start_recheck_bni_sam_balance()
    start_recheck_bni_sam_balance = pyqtSlot()(start_recheck_bni_sam_balance)
    
    def start_bill_store_note(self, trxid):
        _BILL.start_bill_store_note(trxid)
    start_bill_store_note = pyqtSlot(str)(start_bill_store_note)

    def start_bill_reject_note(self, trxid):
        _BILL.start_bill_reject_note(trxid)
    start_bill_reject_note = pyqtSlot(str)(start_bill_reject_note)

    def start_reset_cd_status(self, slot):
        _CD.start_reset_cd_status(slot)
    start_reset_cd_status = pyqtSlot(str)(start_reset_cd_status)


def set_signal_handler():
    _KioskService.K_SIGNDLER.SIGNAL_GET_FILE_LIST.connect(view.rootObject().result_get_file_list)
    _KioskService.K_SIGNDLER.SIGNAL_GET_GUI_VERSION.connect(view.rootObject().result_get_gui_version)
    _KioskService.K_SIGNDLER.SIGNAL_GET_KIOSK_NAME.connect(view.rootObject().result_get_kiosk_name)
    _EDC.E_SIGNDLER.SIGNAL_SALE_EDC.connect(view.rootObject().result_sale_edc)
    _KioskService.K_SIGNDLER.SIGNAL_GET_PAYMENTS.connect(view.rootObject().result_get_payment)
    _KioskService.K_SIGNDLER.SIGNAL_GET_REFUNDS.connect(view.rootObject().result_get_refund)
    _QPROX.QP_SIGNDLER.SIGNAL_INIT_QPROX.connect(view.rootObject().result_init_qprox_config)
    _QPROX.QP_SIGNDLER.SIGNAL_DEBIT_QPROX.connect(view.rootObject().result_debit_qprox)
    _QPROX.QP_SIGNDLER.SIGNAL_AUTH_QPROX.connect(view.rootObject().result_auth_qprox)
    _QPROX.QP_SIGNDLER.SIGNAL_BALANCE_QPROX.connect(view.rootObject().result_balance_qprox)
    _QPROX.QP_SIGNDLER.SIGNAL_TOPUP_QPROX.connect(view.rootObject().result_topup_qprox)
    _QPROX.QP_SIGNDLER.SIGNAL_KA_INFO_QPROX.connect(view.rootObject().result_ka_info_qprox)
    _QPROX.QP_SIGNDLER.SIGNAL_ONLINE_INFO_QPROX.connect(view.rootObject().result_online_info_qprox)
    _QPROX.QP_SIGNDLER.SIGNAL_INIT_ONLINE_QPROX.connect(view.rootObject().result_init_online_mandiri)
    _QPROX.QP_SIGNDLER.SIGNAL_STOP_QPROX.connect(view.rootObject().result_stop_qprox)
    _KioskService.K_SIGNDLER.SIGNAL_GENERAL.connect(view.rootObject().result_general)
    _KioskService.K_SIGNDLER.SIGNAL_GET_KIOSK_STATUS.connect(view.rootObject().result_kiosk_status)
    _KioskService.K_SIGNDLER.SIGNAL_PRICE_SETTING.connect(view.rootObject().result_price_setting)
    _KioskService.K_SIGNDLER.SIGNAL_LIST_CASH.connect(view.rootObject().result_list_cash)
    _KioskService.K_SIGNDLER.SIGNAL_COLLECT_CASH.connect(view.rootObject().result_collect_cash)
    _EDC.E_SIGNDLER.SIGNAL_GET_SETTLEMENT_EDC.connect(view.rootObject().result_get_settlement)
    _EDC.E_SIGNDLER.SIGNAL_PROCESS_SETTLEMENT_EDC.connect(view.rootObject().result_process_settlement)
    _EDC.E_SIGNDLER.SIGNAL_VOID_SETTLEMENT_EDC.connect(view.rootObject().result_void_settlement)
    _CheckIn.CI_SIGNDLER.SIGNAL_CHECK_FLIGHTCODE.connect(view.rootObject().result_check_booking_code)
    _CheckIn.CI_SIGNDLER.SIGNAL_GET_BOARDINGPASS.connect(view.rootObject().result_get_boarding_pass)
    _CheckIn.CI_SIGNDLER.SIGNAL_PRINT_BOARDINGPASS.connect(view.rootObject().result_print_boarding_pass)
    _KioskService.K_SIGNDLER.SIGNAL_ADMIN_KEY.connect(view.rootObject().result_admin_key)
    _KioskService.K_SIGNDLER.SIGNAL_WALLET_CHECK.connect(view.rootObject().result_wallet_check)
    _CD.CD_SIGNDLER.SIGNAL_CD_HOLD.connect(view.rootObject().result_cd_hold)
    _CD.CD_SIGNDLER.SIGNAL_CD_MOVE.connect(view.rootObject().result_cd_move)
    _CD.CD_SIGNDLER.SIGNAL_CD_STOP.connect(view.rootObject().result_cd_stop)
    _KioskService.K_SIGNDLER.SIGNAL_GET_PRODUCT_STOCK.connect(view.rootObject().result_product_stock)
    _KioskService.K_SIGNDLER.SIGNAL_STORE_TRANSACTION.connect(view.rootObject().result_store_transaction)
    _KioskService.K_SIGNDLER.SIGNAL_GET_TOPUP_AMOUNT.connect(view.rootObject().result_topup_amount)
    _SalePrintTool.SPRINTTOOL_SIGNDLER.SIGNAL_SALE_PRINT_GLOBAL.connect(view.rootObject().result_sale_print)
    _CD.CD_SIGNDLER.SIGNAL_MULTIPLE_EJECT.connect(view.rootObject().result_multiple_eject)
    _KioskService.K_SIGNDLER.SIGNAL_STORE_TOPUP.connect(view.rootObject().result_store_topup)
    _UserService.US_SIGNDLER.SIGNAL_USER_LOGIN.connect(view.rootObject().result_user_login)
    _KioskService.K_SIGNDLER.SIGNAL_GET_MACHINE_SUMMARY.connect(view.rootObject().result_kiosk_admin_summary)
    _ProductService.PR_SIGNDLER.SIGNAL_CHANGE_STOCK.connect(view.rootObject().result_change_stock)
    _BILL.BILL_SIGNDLER.SIGNAL_BILL_STATUS.connect(view.rootObject().result_bill_status)
    _BILL.BILL_SIGNDLER.SIGNAL_BILL_RECEIVE.connect(view.rootObject().result_bill_receive)
    _BILL.BILL_SIGNDLER.SIGNAL_BILL_STOP.connect(view.rootObject().result_bill_stop)
    _BILL.BILL_SIGNDLER.SIGNAL_BILL_STORE.connect(view.rootObject().result_bill_store)
    _BILL.BILL_SIGNDLER.SIGNAL_BILL_REJECT.connect(view.rootObject().result_bill_reject)
    _TopupService.TP_SIGNDLER.SIGNAL_DO_TOPUP_BNI.connect(view.rootObject().result_do_topup_deposit_bni)
    _SalePrintTool.SPRINTTOOL_SIGNDLER.SIGNAL_ADMIN_PRINT_GLOBAL.connect(view.rootObject().result_admin_print)
    _SalePrintTool.SPRINTTOOL_SIGNDLER.SIGNAL_SALE_REPRINT_GLOBAL.connect(view.rootObject().result_reprint_global)
    _BILL.BILL_SIGNDLER.SIGNAL_BILL_INIT.connect(view.rootObject().result_init_bill)
    _QPROX.QP_SIGNDLER.SIGNAL_REFILL_ZERO.connect(view.rootObject().result_activation_bni)
    _CD.CD_SIGNDLER.SIGNAL_CD_READINESS.connect(view.rootObject().result_cd_readiness)
    _SettlementService.ST_SIGNDLER.SIGNAL_MANDIRI_SETTLEMENT.connect(view.rootObject().result_mandiri_settlement)
    # _UpdateAppService.UPDATEAPP_SIGNDLER.SIGNAL_UPDATE_APP.connect(view.rootObject().result_update_app)
    _PPOBService.PPOB_SIGNDLER.SIGNAL_GET_PRODUCTS.connect(view.rootObject().result_get_ppob_product)
    _KioskService.K_SIGNDLER.SIGNAL_GET_PAYMENT_SETTING.connect(view.rootObject().result_get_payment_setting)
    _KioskService.K_SIGNDLER.SIGNAL_SYNC_ADS_CONTENT.connect(view.rootObject().result_sync_ads)
    _PPOBService.PPOB_SIGNDLER.SIGNAL_CHECK_PPOB.connect(view.rootObject().result_check_ppob)
    _PPOBService.PPOB_SIGNDLER.SIGNAL_TRX_PPOB.connect(view.rootObject().result_trx_ppob)
    _PPOBService.PPOB_SIGNDLER.SIGNAL_TRX_CHECK.connect(view.rootObject().result_check_trx)
    _PPOBService.PPOB_SIGNDLER.SIGNAL_CHECK_CUSTOMER.connect(view.rootObject().result_ppob_check_customer)
    _QRPaymentService.QR_SIGNDLER.SIGNAL_GET_QR.connect(view.rootObject().result_get_qr)
    _QRPaymentService.QR_SIGNDLER.SIGNAL_PAY_QR.connect(view.rootObject().result_pay_qr)
    _QRPaymentService.QR_SIGNDLER.SIGNAL_CHECK_QR.connect(view.rootObject().result_check_qr)
    _QRPaymentService.QR_SIGNDLER.SIGNAL_CONFIRM_QR.connect(view.rootObject().result_confirm_qr)
    _ProductService.PR_SIGNDLER.SIGNAL_CHECK_VOUCHER.connect(view.rootObject().result_check_voucher)
    _ProductService.PR_SIGNDLER.SIGNAL_USE_VOUCHER.connect(view.rootObject().result_use_voucher)
    _PPOBService.PPOB_SIGNDLER.SIGNAL_CHECK_BALANCE.connect(view.rootObject().result_diva_balance_check)
    _PPOBService.PPOB_SIGNDLER.SIGNAL_TRANSFER_BALANCE.connect(view.rootObject().result_global_refund_balance)
    _KioskService.K_SIGNDLER.SIGNAL_ADMIN_GET_PRODUCT_STOCK.connect(view.rootObject().result_admin_sync_stock)
    _CD.CD_SIGNDLER.SIGNAL_CD_PORT_INIT.connect(view.rootObject().result_init_check_cd)
    _TopupService.TP_SIGNDLER.SIGNAL_CHECK_ONLINE_TOPUP.connect(view.rootObject().result_check_online_topup)
    _TopupService.TP_SIGNDLER.SIGNAL_DO_ONLINE_TOPUP.connect(view.rootObject().result_do_online_topup)
    _TopupService.TP_SIGNDLER.SIGNAL_GET_TOPUP_READINESS.connect(view.rootObject().result_topup_readiness)
    _TopupService.TP_SIGNDLER.SIGNAL_UPDATE_BALANCE_ONLINE.connect(view.rootObject().result_update_balance_online)
    _QPROX.QP_SIGNDLER.SIGNAL_CARD_HISTORY.connect(view.rootObject().result_card_log_history)
    _GeneralPaymentService.GENERALPAYMENT_SIGNDLER.SIGNAL_GENERAL_PAYMENT.connect(view.rootObject().result_general_payment)
    _KioskService.K_SIGNDLER.SIGNAL_PANEL_SETTING.connect(view.rootObject().result_panel_setting)


LOGGER = None


def safely_shutdown(mode):
    print("pyt: safely_shutdown_initiated...")
    # _Command.handle_file(mode='w', param='315|', path=_Command.MI_GUI)
    # sleep(1)
    os.system('taskkill /f /im cmd.exe')
    sleep(1)
    if mode == 'RESTART':
        os.system('shutdown -r -f -t 5')
    elif mode == 'SHUTDOWN':
        os.system('shutdown /s')
    sleep(3)
    exit()


def config_log():
    global LOGGER
    # Sentry Initiation
    sentry_dsn = _ConfigParser.get_set_value('GENERAL', 'sentry^dsn', "https://d1e7e31740c147b289ee1414b2d48874@sentry-logging.multidaya.id/3")
    try:
        sentry_sdk.init(
            sentry_dsn,
            max_breadcrumbs=10,
            debug=False,
            environment=_Common.APP_MODE,
            server_name='VM-ID '+_Common.TID,
            release='APP-VER. '+_Common.VERSION,
            # default_integrations=False,
        )
        if not os.path.exists(sys.path[0] + '/_lLog/'):
            os.makedirs(sys.path[0] + '/_lLog/')
        handler = logging.handlers.TimedRotatingFileHandler(filename=sys.path[0] + '/_lLog/debug.log',
                                                            when='MIDNIGHT',
                                                            interval=1,
                                                            backupCount=60)
        logging.basicConfig(handlers=[handler],
                            level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(funcName)s:%(lineno)d: %(message)s',
                            datefmt='%d/%m %H:%M:%S')
        
        logging.getLogger("requests").setLevel(logging.WARNING)
        LOGGER = logging.getLogger()

        _Common.init_temp_data()
    except Exception as e:
        print("pyt: Logging Configuration ERROR : ", e)


def get_disk_info():
    encrypt_str = ''
    disk_info = []
    try:
        c = wmi.WMI()
        for physical_disk in c.Win32_DiskDrive():
            encrypt_str = encrypt_str + physical_disk.SerialNumber.strip()
    except Exception as e:
        LOGGER.warning((e))
    disk_info.append(encrypt_str)
    _HTTPAccess.DISK_SERIAL_NUMBER = disk_info[0]
    return disk_info[0] if disk_info[0] is not None else "N/A"


def get_screen_resolution():
    global SCREEN_HEIGHT, SCREEN_WIDTH
    try:
        if _Common.IS_WINDOWS:
            import ctypes
            user32 = ctypes.windll.user32
            # user32.SetProcessDPIAware()
            resolution = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
        else:
            output = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=subprocess.PIPE).communicate()[0]
            resolution = output.split()[-1].decode('utf-8').split('x')
            resolution[0] = int(resolution[0])
            resolution[1] = int(resolution[1])
        LOGGER.info(('SCREEN RESOLUTION : ', str(resolution)))
        SCREEN_WIDTH = resolution[0]
        SCREEN_HEIGHT = resolution[1]
    except Exception as e:
        resolution = [0, 0]
        LOGGER.warning((e))
    # print(res)
    return resolution


def process_exist(processname):
    tlcall = 'TASKLIST', '/FI', 'imagename eq %s' % processname
    tlproc = subprocess.Popen(tlcall, shell=True, stdout=subprocess.PIPE)
    tlout = tlproc.communicate()[0].decode('utf-8').strip().split("\r\n")
    if len(tlout) > 1 and processname in tlout[-1]:
        # print('process "%s" is running!' % processname)
        return True
    else:
        # print('process "%s" is NOT running!' % processname)
        return False


def check_db(data_name):
    data_name = data_name + ".db" if ".db" not in data_name else data_name
    if not os.path.exists(sys.path[0] + '/_dDB/' + data_name):
        _Database.init_db()
    LOGGER.info(("DB : ", data_name))


def kill_explorer():
    if INITIAL_SETTING['dev_mode'] is False:
        os.system('taskkill /f /im explorer.exe')
        pass
    else:
        LOGGER.info('Development Mode is ON')


def disable_screensaver():
    try:
        os.system('reg delete "HKEY_CURRENT_USER\Control Panel\Desktop" /v SCRNSAVE.EXE /f')
    except Exception as e:
        LOGGER.warning(('Screensaver Disabling ERROR : ', e))


def run_script(scripts):
    if len(scripts) == 0:
        return
    try:
        import platform
        os_ver = platform.platform()
        if 'Windows-7' in os_ver:
            for script in scripts:
                process = subprocess.Popen(sys.path[0] + script, shell=True, stdout=subprocess.PIPE)
                output = process.communicate()[0].decode('utf-8').strip().split("\r\n")
                LOGGER.info(('[INFO] run_script result : ', str(output)))
        else:
            return
    except Exception as e:
        LOGGER.warning(('[ERROR] run_script: ', str(e)))
    # print(('init time result : ', init_time_result))


def check_path(new):
    try:
        process = subprocess.Popen("PATH", shell=True, stdout=subprocess.PIPE)
        output = process.communicate()[0].decode('utf-8').strip().split("\r\n")
        output_ = output[0].split(";")
        if new in output_:
            return True
        else:
            return False
    except Exception as e:
        LOGGER.warning(('check_path is failed : ', e))
        return False


def set_tvc_player(command):
    try:
        if command == 'START':
            player = os.path.join(os.getcwd(), '_pPlayer', 'vlc_player.py')
            os.system('python3 ' + player)
            return
        LOGGER.info(('Unknown Command: ', command))
    except Exception as e:
        LOGGER.warning((e))


def set_ext_keyboard(command):
    if command == "":
        return
    elif command == "STOP":
        os.system('taskkill /f /IM osk.exe')
    elif command == "START":
        if not process_exist('osk.exe'):
            os.system('osk')
        else:
            print('pyt: External Keyboard is already running..!')
    else:
        return


INITIAL_SETTING = dict()
TEMP_CONFIG_JS = '''
var mandiri_update_schedule = "02:00";
var edc_settlement_schedule = "23:00";
var bank_ubal_online = ["MANDIRI", "BNI"];
var master_logo = ["20200226174450cs4c79p1DvSstTqxPV.png"];
var partner_logos = ["202002261744501WN95z1DClnpPR6COJ.png", "20200226174450E1r8h3I4g2NDfMMgvM.png"];
var backgrounds = ["202002261744502niSQy0MVpaktdm8z1.png"];
var running_text = "Silahkan Tekan Layar Untuk Mulai Transaksi";
var running_text_color = "steelblue";
var text_color = "white";
var frame_color = "steelblue";
var background_color = "black";
var tvc_waiting_time = 60;
'''


def init_local_setting():
    global INITIAL_SETTING
    # Disabled - Move View Config To Context Property - 2022-08-02
    # qml_config = sys.path[0] + '/'+_Common.VIEW_FOLDER+'/config.js'
    # if not os.path.exists(qml_config):
    #     with open(sys.path[0] + '/'+_Common.VIEW_FOLDER+'/config.js', 'w+') as qml:
    #         qml.write(TEMP_CONFIG_JS)
    #         qml.close()
    #     LOGGER.info(("CREATE INITIATION_QML_CONFIG ON ", qml_config))
    INITIAL_SETTING['dev_mode'] = _Common.TEST_MODE
    INITIAL_SETTING['db'] = _ConfigParser.get_set_value('GENERAL', 'DB', 'kiosk.db')
    INITIAL_SETTING['display'] = get_screen_resolution()
    INITIAL_SETTING['devices'] = _Common.get_devices()
    INITIAL_SETTING['tid'] = _Common.TID
    # setting['prepaid'] = _QPROX.BANKS
    INITIAL_SETTING['server'] = _Common.BACKEND_URL
    # Force Reload Service To True
    INITIAL_SETTING['reloadService'] = True
    INITIAL_SETTING['allowedSyncTask'] = _Common.ALLOWED_SYNC_TASK
    # setting['sftpMandiri'] = _Common.SFTP_MANDIRI
    # setting['ftp'] = _Common.FTP
    # setting['bankConfig'] = _Common.BANKS
    # INITIAL_SETTING['serviceVersion'] = _Common.get_service_version()
    # pprint(setting)


def update_module(module_list):
    if len(module_list) == 0 or module_list is None:
        return
    try:
        if check_path("C:\Python34\Scripts") is False:
            os.system("PATH %PATH%;C:\Python34\Scripts")
        for mod in module_list:
            subprocess.call("pip install --upgrade " + mod)
            LOGGER.info((str(mod), 'is updated successfully'))
    except Exception as e:
        LOGGER.warning(("update module is failed : ", e))


def install_font():
    # vb script template
    _TEMPL = """ 
    Set objShell = CreateObject("Shell.Application")
    Set objFolder = objShell.Namespace("%s")
    Set objFolderItem = objFolder.ParseName("%s")
    objFolderItem.InvokeVerb("Install")
    """
    vbs_path = os.path.join(os.getcwd(), 'font_install.vbs')
    try:
        font_dir = os.path.join(os.getcwd(), '_fFonts')
        available_fonts = [f for f in os.listdir(font_dir) if f.endswith('.ttf')]
        system_font_dir = os.path.join('C:\\', 'Windows', 'Fonts')
        installed_fonts = [f for f in os.listdir(system_font_dir) if f.endswith('.ttf')]
        new_fonts = list(set(available_fonts) - set(installed_fonts))
        print('pyt: Found fonts to be installed : ' + json.dumps(new_fonts))
        if len(new_fonts) > 0:
            for font in new_fonts:
                f_path = os.path.join(font_dir, font)
                with open(vbs_path, 'w') as _f:
                    _f.write(_TEMPL % (font_dir, font))
                subprocess.call(['cscript.exe', vbs_path])
                print('pyt: Registering Font -> ' + f_path)
                sleep(1)
    except Exception as e:
        print('pyt: Error Register Font -> ' + str(e))
    finally:
        if os.path.exists(vbs_path):
            os.remove(vbs_path)


def check_git_status(log=False):
    process = subprocess.Popen('git status', shell=True, stdout=subprocess.PIPE)
    response = process.communicate()[0].decode('utf-8').strip().split("\r\n")
    if len(response) > 0 and log is True:
        print('pyt: check_git_status : ')
        for r in response:
            print(str(r))
            

def init_local_setting_from_host():
    url = _Common.BACKEND_URL + 'get/init-setting'
    status, response = _HTTPAccess.get_from_url(url=url, force=True)
    if status == 200 and response['result'] == 'OK':
        if len(response['data']) > 0:
            _Common.store_to_temp_data('host-setting', response['data'])
            for set in response['data']:
                LOGGER.debug(('SET TO LOCAL', str(set)))
                sleep(.25)
                _ConfigParser.set_value(set['section'], set['option'], set['value'])
    else:
        LOGGER.warning((status, response))
        print("pyt: Failed Initiating Config From Host...")


def start_webserver():
    pass
    # _MainService.start()
    
    
def start_startup_task():
    _Helper.get_thread().apply_async(startup_task,)


STARTUP_TASK = False

def startup_task():
    global STARTUP_TASK
    
    if not STARTUP_TASK:
        STARTUP_TASK = True
        _Common.REBOOT_TIME = _Helper.now()
        print("pyt: Table Adjustment/Migration...")
        _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Table Adjustment/Migration...')
        _KioskService.migrate_table([
            "ALTER TABLE ProductStock ADD COLUMN bid INT DEFAULT 1;",
            "ALTER TABLE Product ADD COLUMN bid INT DEFAULT 1;",
            "ALTER TABLE Settlement ADD COLUMN remarks TEXT;",
            "ALTER TABLE Settlement ADD COLUMN trx_type VARCHAR(100);",	
            "ALTER TABLE TransactionsNew ADD COLUMN trxNotes TEXT;",	
            "UPDATE ProductStock SET updatedAt = 1 WHERE updatedAt IS NULL;",
            "ALTER TABLE TransactionsNew ADD COLUMN serviceCharge DEFAULT 0;",	
            ])
        sleep(1)
        _KioskService.alter_table('_CashBox.sql')
        sleep(1)
        _KioskService.alter_table('_DailySummary.sql')
        sleep(1)
        _KioskService.alter_table('_SAMAudit.sql')
        sleep(1)
        _KioskService.alter_table('_TransactionsNew.sql')
        sleep(1)
        if INITIAL_SETTING['reloadService'] is True and _Common.IS_WINDOWS:
            print("pyt: Restarting MDDTopUpService...")
            _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Restarting MDDTopUpService...')
            _KioskService.start_restart_mdd_service()
            sleep(1)
        print("pyt: HouseKeeping Old Local Data/Files...")
        _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|HouseKeeping Old Local Data/Files...')
        _KioskService.house_keeping(age_month=6)
        sleep(1)
        _KioskService.reset_db_record()
        sleep(1)
        print("pyt: Syncing Remote Task...")
        _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Syncing Remote Task...')
        _Sync.start_sync_task()
        sleep(1)
        # print("pyt: Syncing Offline Item Transaction...")
        # _Sync.start_sync_product_data()
        # sleep(1)
        # print("pyt: Syncing Product Stock...")
        # _Sync.start_sync_product_stock()
        # sleep(1)
        print("pyt: Syncing Transaction...")
        _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Syncing Transaction...')
        _Sync.start_sync_data_transaction()
        sleep(1)
        # print("pyt: Syncing Transaction Failure Data...")
        # _Sync.start_sync_data_transaction_failure()
        # sleep(1)
        # print("pyt: Syncing Topup Records...")
        # _Sync.start_sync_topup_records()
        # sleep(1)
        print("pyt: Syncing Topup Amount...")
        _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Syncing Topup Amount...')
        _Sync.start_sync_topup_amount()
        sleep(1)
        # print("pyt: Syncing SAM Audit...")
        # _Sync.start_sync_sam_audit()
        # sleep(.5)
        # print("pyt: Retrying Pending Refund...")
        # _Sync.start_sync_pending_refund()
        # sleep(.5)
        print("pyt: Syncing PPOB Product...")
        _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Syncing PPOB Product...')
        _PPOBService.start_init_ppob_product()
        sleep(1)
        print("pyt: Do Reprint Jobs...")
        _SalePrintTool.start_reprint_pending_task()
        sleep(1)
        # Disable Load As WebServer, Call as Direct Module Instead
        # print("pyt: Start Topup Service...")
        # _Helper.get_thread().apply_async(start_webserver)
        # sleep(1)
<<<<<<< HEAD

	#Disabled By Wahyudi 2023-10-28
        #print("pyt: Start Init Cash Activity...")
        #_KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Start Init Cash Activity...')
        #_Common.init_cash_activity()
        #sleep(1)

=======
        
        # Disable Below To Prevent Double Claim Bill Receive : 20231025
        # print("pyt: Start Init Cash Activity...")
        # _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Start Init Cash Activity...')
        # _Common.init_cash_activity()
        
        sleep(1)
>>>>>>> 7c4ed118e102832210c5b9a2480573dcbc1f7a7c
        if _Common.BILL['status'] is True:
            sleep(1)
            print("pyt: Connecting to " +_Common.BILL_TYPE+ " Bill Acceptor...")
            _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Connecting to ' +_Common.BILL_TYPE+ ' Bill Acceptor...')
            _BILL.init_bill()
        if _Common.QPROX['status'] is True:
            print("pyt: Connecting to Prepaid Reader...")
            _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Connecting to Prepaid Reader...')
            sleep(1)
            if _QPROX.open() is True:
                print("pyt: [INFO] Init Prepaid Reader...")
                _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Init Prepaid Reader...')
                _QPROX.init_config()
            else:
                print("pyt: [ERROR] Connect to Prepaid Reader...")
                _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Init Prepaid Reader...ERROR')
        sleep(1)
        print("pyt: Resync Data MDD Global Card Blacklist...")
        _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Resync Data MDD Global Card Blacklist...')
        _TopupService.get_mdd_card_blocked_list()
        if _QPROX.INIT_BCA is True:
            # TODO Add Special Handler For BCA Initiation
            sleep(1)
            print("pyt: Triggering Topup BCA Init Config...")
            _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Triggering Topup BCA Init Config...')
            _QPROX.start_init_config_bca()
            print("pyt: Triggering Topup BCA Reset Session...")
            _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Triggering Topup BCA Reset Session...')
            _TopupService.reset_bca_session()
        if _QPROX.INIT_BRI is True:
            # TODO Add Special Handler For BRI Initiation
            # sleep(.5)
            # print("pyt: Triggering BRI Balance Validation...")
            pass
        if _QPROX.INIT_MANDIRI is True:
            sleep(1)
            print("pyt: Check Mandiri Deposit Update Balance...")
            _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Check Mandiri Deposit Update Balance...')
            _TopupService.check_mandiri_deposit_update_balance()
            sleep(1)
            print("pyt: Resync Data Mandiri Card Blacklist...")
            _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Resync Data Mandiri Card Blacklist...')
            _TopupService.get_mandiri_card_blocked_list()
            sleep(1)
            print("pyt: Resync Mandiri C2C Fee To Host...")
            _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Resync Mandiri C2C Fee To Host...')
            _SettlementService.start_do_c2c_send_fee()    
            sleep(1)
            print("pyt: Check Last Mandiri Settlement...")
            _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Check Last Mandiri Settlement...')
            _SettlementService.start_check_last_mandiri_settlement()
            # Below Handler Move into Sync
            # if '02:3' in _Helper.time_string('%H:%M'):
            #     sleep(1)
            #     print("pyt: Check Mandiri C2C Settlement...")
            #     _SettlementService.start_daily_mandiri_c2c_settlement()    
        if _QPROX.INIT_BNI is True:
            sleep(1)
            print("pyt: Check BNI Deposit Balance...")
            _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Check BNI Deposit Balance...')
            _QPROX.start_recheck_bni_sam_balance()
            sleep(1)
            print("pyt: Triggering BNI Settlement Sync...")
            _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Triggering BNI Settlement Sync...')
            _Sync.start_sync_settlement_bni()
            sleep(1)
            print("pyt: Check BNI Deposit Balance Refill...")
            _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Check BNI Deposit Balance Refill...')
            _Sync.start_check_bni_deposit()
        if _Common.EDC['mobile'] is True:
            sleep(1)
            print("pyt: [INFO] Re/Binding VM Machine Into EDC...")
            _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Re/Binding VM Machine Into EDC...')
            _EDC.edc_mobile_start_binding_edc()
        if not _Common.validate_system_version():
            print("pyt: Syncing Ads Content...")
            _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Syncing Ads Content...')
            sleep(1)
        _KioskService.start_define_ads(3)
        print("pyt: Reset Open Previous Pending Jobs...")
        _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Reset Open Previous Pending Jobs...')
        sleep(2)
        _KioskService.reset_open_job()
        print("pyt: Do Pending Request Jobs...")
        _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Do Pending Request Jobs...')
        sleep(1)
        _Sync.start_do_pending_request_job()
        if _Common.chatbot_feature():
            print("pyt: Init Chatbot Engine...")
            _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Initiate Chatbot Engine...')
            sleep(1)
            _ChatbotService.start_initiation()
        print("pyt: Do Pending Daily Report...")
        _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Do Pending Daily Report...')
        sleep(1)
        _Sync.start_send_all_not_synced_daily_report()
        _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Startup Completed...')
        print("pyt: Get Kiosk Terminal Status...")
        _KioskService.K_SIGNDLER.SIGNAL_GENERAL.emit('STARTUP|Get Kiosk Terminal Status...')
        _KioskService.start_get_kiosk_status()
    

if __name__ == '__main__':
    print("pyt: Initiating Config...")
    config_log()
    init_local_setting()
    # sleep(1)
    # print("pyt: Initiating Setting From Host...")
    # init_local_setting_from_host()
    update_module(['ntplib'])
    # install_font()
    check_db(INITIAL_SETTING['db'])
    # disable_screensaver()
    if _Common.LIVE_MODE and _Common.IS_WINDOWS:
        kill_explorer()
    print("pyt: Checking Auth to Server...")
    _Sync.start_sync_machine(url=INITIAL_SETTING['server'].replace('v2/', '')+'ping', param=INITIAL_SETTING)
    print("pyt: Setting Up Function(s)/Method(s)...")
    SLOT_HANDLER = SlotHandler()
    # os.environ["QT_DEBUG_PLUGINS"] = "1"
    app = QGuiApplication(sys.argv)
    print("pyt: Setting Up View...")
    if os.name == 'nt':
        path = _Common.VIEW_FOLDER+'/'
    else:
        path = sys.path[0] + '/'+_Common.VIEW_FOLDER+'/'
    view = QQuickView()
    context = view.rootContext()
    context.setContextProperty('_SLOT', SLOT_HANDLER)
    context.setContextProperty('SCREEN_WIDTH', SCREEN_WIDTH)
    context.setContextProperty('SCREEN_HEIGHT', SCREEN_HEIGHT)
    context.setContextProperty('IS_WINDOWS', _Common.IS_WINDOWS)
    context.setContextProperty('IS_LINUX', _Common.IS_LINUX)
    context.setContextProperty('VIEW_CONFIG', _Common.VIEW_CONFIG)
    # translator = QTranslator()
    # translator.load(path + 'INA.qm')
    # app.installTranslator(translator)
    view.engine().quit.connect(app.quit)
    if _Common.IS_WINDOWS:
        view.setSource(QUrl(path + 'Main.qml'))
    else:
        view.setSource(QUrl(path + 'MainLinux.qml'))
    set_signal_handler()
    if _Common.LIVE_MODE:
        app.setOverrideCursor(Qt.BlankCursor)
    view.setFlags(Qt.WindowFullscreenButtonHint)
    view.setFlags(Qt.FramelessWindowHint)
    view.resize(SCREEN_WIDTH, SCREEN_HEIGHT - 1)
    # Move Sync Task Into Another Thread
    view.show()
    app.exec_()
    del view
