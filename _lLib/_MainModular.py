from _lLib._InterfacePrepaidDLL import send_command

""" 
Tested Command:
    Mandiri SEQ:
        #OPEN
        send_command("000", "COM9")    
        #MANDIRI_INIT
        send_command("001", "COM9|6D2FE98B75D45FE1|0077|51140488")
        #MANDIRI_INIT_C2C
        send_command("027", "51140488|0114040000770000|1")
        #CHECK SAM BALANCE
        send_command("033", "")
        #CHECK CARD BALANCE
        send_command("003", "")
        #MANDIRI TOPUP 2000
        send_command("026", "2000")

    
    BNI SEQ:
        #OPEN
        send_command("000", "COM9")    
        #UPDATE TID
        send_command("011", "41030418")
        #GET SAM BALANCE
        send_command("014", "0")
        #GET PURSE DATA
        send_command("015", "0")

        #INIT TOPUP
        send_command("012", "0|41030418")
        #TOPUP
        send_command("013", "500|0")
        #GET SAM BALANCE
        send_command("014", "0")

DEV CMD:
    MANDIRI:
        send_command("001", "COM10|0123456789ABCDEF|0001|20010200")
        send_command("027", "20010200|0001028800010000|1")

Config Not Working:
    MANDIRI:
        send_command("001", "COM9|1728E442CA7836B8|0075|51072288")
        send_command("027", "51072288|0107220000750000|1")

"""
import json
import _CPrepaidUtils as utils
import _CPrepaidDLL as prepaid
import _CPrepaidBNI as prepaid_bni
import datetime
import ctypes
from ctypes import *

if __name__ == '__main__':
    # test_timeout()
    # #OPEN
    # send_command("000", "COM9")    
    # #MANDIRI_INIT
    # send_command("001", "COM9|6D2FE98B75D45FE1|0077|51140488")
    # #MANDIRI_INIT_C2C
    # send_command("027", "51140488|0114040000770000|1")
    # #CHECK SAM BALANCE
    # send_command("033", "")
    # #CHECK CARD BALANCE
    # send_command("003", "")
    # #MANDIRI TOPUP 2000\
    # print("helloworld!")
    
    # send_command("000", "COM9")
    # send_command("025", "3")
    # prepaid.topup_get_sn()

    # test = '6013500433175495\xc3\xad'
    # print(utils.fix_report(test))
    # print(utils.fix_report_leave_space(test))
    # print(utils.remove_special_character(test))
    # print(utils.only_alpanum(test))

    # send_command("000", "COM9")    
    # prepaid_bni.test_update_balance_card("reff_no", "TOKEN", "TID", "MID", "card_no")
    # prepaid_bni.test_update_balance_sam("reff_no", "TOKEN", "TID", "MID", "card_no", "sam_slot")

    date_1 = datetime.datetime(1995,1,1,0,0,0)
    print(date_1.strftime("%Y%m%d%H%M%S"))
    date_2 = date_1 + datetime.timedelta(0,50000)
    print(date_2.strftime("%Y%m%d%H%M%S"))
    data = '1'
    print(data)
    data = utils.str_to_bytes(data)
    data_c = c_char(data)    
    print(data_c.value)