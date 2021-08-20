__author__ = "fitrah.wahyudi.imam@gmail.com"

import os
import sys
import logging
from PyQt5.QtCore import QObject, pyqtSignal
from _cConfig import _ConfigParser, _Common
from time import sleep
import subprocess
# import multiprocessing
# from playsound import playsound
from _tTools import _Helper


AUDIO_PATH = sys.path[0] + '/_aAudio/'
if not os.path.exists(AUDIO_PATH):
    os.makedirs(AUDIO_PATH)
    
SOUND = None

class AudioSignalHandler(QObject):
    __qualname__ = 'AudioSignalHandler'
    SIGNAL_START_AUDIO = pyqtSignal(str)
    SIGNAL_STOP_AUDIO = pyqtSignal(str)

AUD_SIGNDLER = AudioSignalHandler()
LOGGER = logging.getLogger()

SOUNDER = os.path.join(sys.path[0], 'sounder.exe')

# TODO: Register All Audio Files Here
AUDIO_MAPPING = {
    # 'welcome': os.path.join(AUDIO_PATH, 'intro.wav'),
    'cancel_transaction_confirmation': os.path.join(AUDIO_PATH, 'cancel_transaction_confirmation.wav'),
    'card_not_detected': os.path.join(AUDIO_PATH, 'card_not_detected.wav'),
    'choose_item_product': os.path.join(AUDIO_PATH, 'choose_item_product.wav'),
    'choose_payment_press_proceed': os.path.join(AUDIO_PATH, 'choose_payment_press_proceed.wav'),
    'choose_prepaid_card': os.path.join(AUDIO_PATH, 'choose_prepaid_card.wav'),
    'choose_product_operator': os.path.join(AUDIO_PATH, 'choose_product_operator.wav'),
    'choose_topup_denom': os.path.join(AUDIO_PATH, 'choose_topup_denom.wav'),
    'follow_payment_instruction': os.path.join(AUDIO_PATH, 'follow_payment_instruction.wav'),
    'homepage_greeting': os.path.join(AUDIO_PATH, 'homepage_greeting.wav'),
    'insert_cash_with_good_condition': os.path.join(AUDIO_PATH, 'insert_cash_with_good_condition.wav'),
    'keep_card_in_reader_untill_finished': os.path.join(AUDIO_PATH, 'keep_card_in_reader_untill_finished.wav'),
    'open_app_scan_qr': os.path.join(AUDIO_PATH, 'open_app_scan_qr.wav'),
    'please_input_register_no_press_proceed': os.path.join(AUDIO_PATH, 'please_input_register_no_press_proceed.wav'),
    'please_input_retry_code': os.path.join(AUDIO_PATH, 'please_input_retry_code.wav'),
    'please_input_voucher_code': os.path.join(AUDIO_PATH, 'please_input_voucher_code.wav'),
    'please_input_wa_no': os.path.join(AUDIO_PATH, 'please_input_wa_no.wav'),
    'please_insert_card_press_proceed': os.path.join(AUDIO_PATH, 'please_insert_card_press_proceed.wav'),
    'please_pull_retap_card': os.path.join(AUDIO_PATH, 'please_pull_retap_card.wav'),
    'please_take_new_card_with_receipt': os.path.join(AUDIO_PATH, 'please_take_new_card_with_receipt.wav'),
    'put_card_and_press_proceed': os.path.join(AUDIO_PATH, 'put_card_and_press_proceed.wav'),
    'read_tnc_press_proceed': os.path.join(AUDIO_PATH, 'read_tnc_press_proceed.wav'),
    'scan_qr_ereceipt': os.path.join(AUDIO_PATH, 'scan_qr_ereceipt.wav'),
    'summary_transaction_press_proceed': os.path.join(AUDIO_PATH, 'summary_transaction_press_proceed.wav'),
    'transaction_failed': os.path.join(AUDIO_PATH, 'transaction_failed.wav'),
}


def sounder(track):
    try:
        cmd = ' '.join([SOUNDER, '/stop', track])
        # os.system(cmd)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output = process.communicate()[0].decode('utf-8').strip().split("\r\n")
        LOGGER.debug((output))
        return True
    except Exception as e:
        LOGGER.warning((e))
        return False


def start_play_audio(track):
    _Helper.get_thread().apply_async(play_audio, (track,))


def play_audio(track):
    global SOUND
    try:
        # if SOUND is not None:
        #     SOUND.terminate()
        audio = AUDIO_MAPPING.get(track)
        if audio is None or not os.path.exist(audio):
            AUD_SIGNDLER.SIGNAL_START_AUDIO.emit('START_AUDIO|NOT_FOUND')
            return
        # SOUND = multiprocessing.Process(target=playsound, args=(audio,))
        # SOUND.start()
        play_sound = sounder(track=audio)
        if not play_sound:
            AUD_SIGNDLER.SIGNAL_START_AUDIO.emit('START_AUDIO|ERROR')
            return
        AUD_SIGNDLER.SIGNAL_START_AUDIO.emit('START_AUDIO|SUCCESS')
    except Exception as e:
        LOGGER.warning((e))
        AUD_SIGNDLER.SIGNAL_START_AUDIO.emit('START_AUDIO|ERROR')
        

def start_trigger_stop_audio():
    _Helper.get_thread().apply_async(trigger_stop_audio,)
    
    
def trigger_stop_audio():
    global SOUND
    try:
        if SOUND is not None:
            SOUND.terminate()
        SOUND = None
        AUD_SIGNDLER.SIGNAL_START_AUDIO.emit('STOP_AUDIO|SUCCESS')
    except Exception as e:
        LOGGER.warning((e))
        AUD_SIGNDLER.SIGNAL_START_AUDIO.emit('STOP_AUDIO|ERROR')
