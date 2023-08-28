__author__ = 'wahyudi@multidaya.id'

import pprint
import os
import sys
import datetime
from _mModule import _CPrepaidUtils as utils

LOG_FILE = os.path.join(sys.path[0], "_mModule", "Logs")

INFO_TYPE_INFO = 0
INFO_TYPE_ERROR = 1

FLOW_TYPE_OUT = 0
FLOW_TYPE_PROC = 1
FLOW_TYPE_IN = 2
FLOW_TYPE_NO_FLOW = 3


if not os.path.exists(LOG_FILE):
    os.makedirs(LOG_FILE)


def bvlog(message, info_type, flow_type, fw_object=None, file_name_prefix="GRGLOG_", prettyprint=False, show_log=True):
    if show_log is True:
        do_logging(message, info_type, flow_type, fw_object, file_name_prefix, prettyprint)
        
        
def cdlog(message, info_type, flow_type, fw_object=None, file_name_prefix="CardDispenser_", prettyprint=False, show_log=True):
    if show_log is True:
        do_logging(message, info_type, flow_type, fw_object, file_name_prefix, prettyprint)
        

def ecrlog(message, info_type, flow_type, fw_object=None, file_name_prefix="ECR_", prettyprint=False, show_log=True):
    if show_log is True:
        do_logging(message, info_type, flow_type, fw_object, file_name_prefix, prettyprint)


def tracing(func, message):
    pp = pprint.PrettyPrinter(indent=2)
    pass
    # prefix = "PREPAID_TRACE > " + func
    # print(prefix)
    # pp.pprint(message)
    # print("------------------------------")


def debuging(func, message):
    pp = pprint.PrettyPrinter(indent=2)
    pass
    # prefix = "PREPAID_DEBUG > " + func
    # print(prefix)
    # pp.pprint(message)
    # print("----------")


def fw(message, fw_object=None,err=False):
    global LOG_FILE
    date_now = str(datetime.datetime.now().strftime("%d%m%Y"))
    time_now = str(datetime.datetime.now().strftime("%H:%M:%S"))
    file_path = os.path.join(LOG_FILE, "PrepaidDLL_" + date_now + ".log")

    if message == "<-- CMD RESULT = " and fw_object != "0000":
        info = "[ERROR]"
    else:
        info = "[INFO]"
    
    if err:
        info = "[ERROR]"
    
    if len(message) >= 3:
        arrow = message[0:3]
        if arrow == "-->" or arrow == "<--" :
            process_arrow = ""
        else:
            process_arrow = "+-+ "
    else:
        process_arrow = ""

    if fw_object is None:
        message_to_write = time_now + " "+info+" "+ process_arrow + message + "\r\n"
    else:
        pobject = pprint.pformat(fw_object)
        message_to_write = time_now + " "+info+" "+ process_arrow + message + pobject + "\r\n"
    
    if os.path.exists(file_path):
        append_write = 'ab'
    else:
        append_write = 'wb'
    
    with open(file_path, append_write) as file_log:
        datas = utils.str_to_bytes(message_to_write)
        file_log.write(datas)
        # print(datas)


def do_logging(message, info_type, flow_type, fw_object, file_name_prefix, prettyprint=False):
    global LOG_FILE
    date_now = str(datetime.datetime.now().strftime("%d%m%Y"))
    time_now = str(datetime.datetime.now().strftime("%H:%M:%S"))
    file_path = os.path.join(LOG_FILE, file_name_prefix + date_now + ".log")

    if info_type == INFO_TYPE_INFO:
        info = "[ INFO]"
    else:
        info = "[ERROR]"

    if flow_type == FLOW_TYPE_OUT:
        process_arrow = "--> "
    elif flow_type == FLOW_TYPE_PROC:
        process_arrow = "+-+ "
    elif flow_type == FLOW_TYPE_IN:
        process_arrow = "<-- "
    else:
        process_arrow = ""
    
    if fw_object is None:
        message_to_write = time_now + " "+info+" "+ process_arrow + message + "\r\n"
    elif prettyprint:
        pobject = pprint.pformat(fw_object)
        message_to_write = time_now + " "+info+" "+ process_arrow + message + pobject + "\r\n"
    else:
        pobject = "{0}".format(fw_object)
        message_to_write = time_now + " "+info+" "+ process_arrow + message + pobject + "\r\n"
    
    if os.path.exists(file_path):
        append_write = 'ab'
    else:
        append_write = 'wb'
    
    with open(file_path, append_write) as file_log:
        datas = utils.str_to_bytes(message_to_write)
        file_log.write(datas)
