__author__ = "fitrah.wahyudi.imam@gmail.com"

import os
import sys
import logging
from PyQt5.QtCore import QObject, pyqtSignal
from _cConfig import _ConfigParser, _Common
from time import sleep
import multiprocessing
from playsound import playsound
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

# TODO: Register All Audio Files Here
AUDIO_MAPPING = {
    'welcome': os.path.join(AUDIO_PATH, 'welcome.mp3')
}


def start_play_audio(track):
    _Helper.get_thread().apply_async(play_audio, (track,))


def play_audio(track):
    global SOUND
    try:
        if SOUND is not None:
            SOUND.terminate()
        audio = AUDIO_MAPPING.get(track)
        if audio is None:
            AUD_SIGNDLER.SIGNAL_START_AUDIO.emit('START_AUDIO|NOT_FOUND')
            return
        SOUND = multiprocessing.Process(target=playsound, args=(audio,))
        SOUND.start()
        AUD_SIGNDLER.SIGNAL_START_AUDIO.emit('START_AUDIO|SUCCESS')
    except Exception as e:
        LOGGER.warning((e))
        AUD_SIGNDLER.SIGNAL_START_AUDIO.emit('START_AUDIO|ERROR')
    