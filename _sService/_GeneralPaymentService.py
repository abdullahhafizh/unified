__author__ = "wahyudi@multidaya.id"

from PyQt5.QtCore import QObject, pyqtSignal
from _cConfig import _Common
from _tTools import _Helper
import os
from time import sleep


class GeneralPaymentSignalHandler(QObject):
    __qualname__ = 'GeneralPaymentSignalHandler'
    SIGNAL_GENERAL_PAYMENT = pyqtSignal(str)


GENERALPAYMENT_SIGNDLER = GeneralPaymentSignalHandler()

