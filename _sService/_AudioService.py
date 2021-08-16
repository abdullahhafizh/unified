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
    'welcome': os.path.join(AUDIO_PATH, 'intro.wav'),
    'failed_read_qr': os.path.join(AUDIO_PATH, 'failed_read_qr.wav'),
    'failed_validate_qr': os.path.join(AUDIO_PATH, 'failed_validate_qr.wav'),
    'card_not_available': os.path.join(AUDIO_PATH, 'card_not_available.wav'),
    'take_otp_card': os.path.join(AUDIO_PATH, 'take_otp_card.wav'),
    'scan_vm_qr_to_mobile': os.path.join(AUDIO_PATH, 'scan_vm_qr_to_mobile.wav'),
    'scan_phone_qr_to_vm': os.path.join(AUDIO_PATH, 'scan_phone_qr_to_vm.wav'),
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
