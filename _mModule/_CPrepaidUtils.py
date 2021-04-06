__author__ = 'fitrah.wahyudi.imam@gmail.com'

from _mModule import _CPrepaidLog as LOG
import re, string;

pattern = re.compile('[\W_]+', re.UNICODE)
pattern2 = re.compile("(?:[^A-Za-z0-9 ]|(?<=['""])s)", re.UNICODE)
pattern3 = re.compile("[^A-Z0-9 ]*", re.UNICODE)
pattern4 = re.compile('[^A-Za-z0-9]')

def get_balance_from_report(reportSAM, bank_type="MANDIRI"):
    if bank_type == "MANDIRI":
        if reportSAM[0:4] == "6308":
            reportSAM = reportSAM[4:200]
        else :
            reportSAM = reportSAM[2:198]
            
        reportDeposit = reportSAM[0:102]
        reportEMoney = reportSAM[-102:]
        
        balanceDepositStr = reportDeposit[54:62]
        balanceDepositStr = "".join(reversed([balanceDepositStr[i:i+2] for i in range(0, len(balanceDepositStr), 2)]))
        valueDeposit = int(balanceDepositStr, 16)

        LOG.debuging("val Deposit: ", str(valueDeposit))

        balanceEmoneyStr = reportEMoney[62:70]
        balanceEmoneyStr = "".join(reversed([balanceEmoneyStr[i:i+2] for i in range(0, len(balanceEmoneyStr), 2)]))
        valueEMoney = int(balanceEmoneyStr, 16)

        LOG.debuging("val EMoney: ", str(valueEMoney))

    return valueDeposit, valueEMoney, reportSAM

def fix_report(reportSAM):
    # LOG.fw("[UTILS] fix_report FROM: ", reportSAM)
    # new_report = re.sub(pattern, "", reportSAM)
    # LOG.fw("[UTILS] fix_report TO: ", new_report)
    return only_alpanum(reportSAM)

def remove_special_character(data):
    new_data = re.sub(pattern2, "", data)
    return new_data

def fix_report_leave_space(data):
    new_data = re.sub(pattern3, "", data)
    return new_data

def to_4digit(res):
    res_str = format(res, 'x').upper()
    if len(res_str) < 4 :
        res_str = res_str.zfill(4)
    return res_str

def str_to_bytes(instance):
    if type(instance) == str:
        return instance.encode("utf-8")
    elif type(instance) == bytes:
        #bytes type will be ignored
        return instance
    elif type(instance) == int:
        #int type will be ignored
        return instance
    else:
        raise Exception("Invalid Instance: "+ str(type(instance)))

def bytes_to_str(instance):
    if type(instance) == str:
        return instance
    elif type(instance) == bytes:
        return instance.decode("utf-8")
    else:
        raise Exception("Invalid Instance: "+ str(type(instance)))

def getint(data):
    data_str = data.zfill(8)
    data_str = "".join(reversed([data[i:i+2] for i in range(0, len(data), 2)]))
    valueDeposit = int(data_str, 16)
    return valueDeposit

def getint2(data):
    data_str = data.zfill(4)
    data_str = "".join(reversed([data[i:i+2] for i in range(0, len(data), 2)]))
    valueDeposit = int(data_str, 16)
    return valueDeposit

def only_alpanum(data):
    x =str(data)
    new_data = re.sub(pattern4, "", x)
    return new_data