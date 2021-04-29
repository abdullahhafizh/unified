__author__ = "fitrah.wahyudi.imam@gmail.com"

import os
import sys
import logging
from PyQt5.QtCore import QObject, pyqtSignal
from _cConfig import _ConfigParser, _Common
from time import sleep


class AudioSignalHandler(QObject):
    __qualname__ = 'AudioSignalHandler'
    SIGNAL_START_AUDIO = pyqtSignal(str)
    SIGNAL_STOP_AUDIO = pyqtSignal(str)

AUD_SIGNDLER = AudioSignalHandler()
LOGGER = logging.getLogger()

AUDIO_MAPPING = {
    '': ''
}