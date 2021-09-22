__author__ = 'wahyudi@multidaya.id'

from ctypes import Structure, c_int, c_double, c_ubyte, c_char_p, c_byte, c_char, c_char_p, c_wchar, POINTER

class ResponSamSaldo(Structure):
    _fields_ = [
        ("repsaldo", c_char * 20)
    ]

class ResponUID(Structure):
    _fields_ = [
        ("repUID", c_char * 202)
    ]

class ResponCardData(Structure):
    _fields_ = [
        ("repData", c_char * 256)
    ]

class ResponCardAttr(Structure):
    _fields_ = [
        ("repAttr", c_char * 256)
    ]

class ResponSN(Structure):
    _fields_ = [
        ("repSN", c_char * 202)
    ]

class ResponTopUpC2C(Structure):
    _fields_ = [
        ("rep", c_char * 1024),
        ("c_error", c_char * 4)
    ]

class ResponAPDU(Structure):
    _fields_ = [
        ("repcek", c_char * 470)
    ]

class ResponPurseData(Structure):
    _fields_ = [
        ("rep", c_char * 184),
        ("c_error", c_char * 4)
    ]

class ResponTopUpBNI(Structure):
    _fields_ = [
        ("rep", c_char * 284),
        ("c_error", c_char * 4)
    ]

class ResponNIKKL(Structure):
    _fields_ = [
        ("repDATA", c_char * 202)
    ]

class ResponDebit(Structure):
    _fields_ = [
        ("Balance", c_int),
        ("rep", c_char * 202),
        ("c_error", c_char * 4)
    ]

class ResponDebitSingle(Structure):
    _fields_ = [
        ("rep", c_char * 2048),
        ("c_error", c_char * 4)
    ]

class ResponBCATopup1(Structure):
    _fields_ = [
        ("repDATA", c_char * 1024)
    ]

class ResponBCATopup2(Structure):
    _fields_ = [
        ("rep", c_char * 1024),
        ("Balance", c_int),
        ("c_error", c_char*4)
    ]

class ResponBCASession1(Structure):
    _fields_ = [
        ("repDATA", c_char * 500)
    ]

class ResponBCAReversal(Structure):
    _fields_ = [
        ("repDATA", c_char * 2048)
    ]

class ResponTokenBRI(Structure):
    _fields_ = [
        ("repDATA", c_char * 102)
    ]
