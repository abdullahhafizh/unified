__author__ = "wahyudi@multidaya.id"

from PyQt5.QtCore import QObject, pyqtSignal

class GeneralPaymentSignalHandler(QObject):
    __qualname__ = 'GeneralPaymentSignalHandler'
    SIGNAL_GENERAL_PAYMENT = pyqtSignal(str)


GENERALPAYMENT_SIGNDLER = GeneralPaymentSignalHandler()

