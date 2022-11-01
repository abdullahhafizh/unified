__author__ = 'wahyudi@multidaya.id'

import traceback
# from _mModule import _CPrepaidDLL as prepaid_dll
from _mModule import _CPrepaidCommon as prepaid_common
from _mModule import _CPrepaidBNI as prepaid_bni
from _mModule import _CPrepaidMandiri as prepaid_mandiri
from _mModule import _CPrepaidBCA as prepaid_bca
from _mModule import _CPrepaidBRI as prepaid_bri
from _mModule import _CPrepaidLog as LOG
from _mModule import _CPrepaidDKI as prepaid_dki
from _cConfig import _Common
# from func_timeout import func_set_timeout

# @func_set_timeout(2.5)
# def test_timeout():
#     while True:
#         print("1")

def send_command(cmd, param):
    LOG.fw("LIB [{0}]: Param = ".format(cmd), param)

    __global_response__ = {
        "Command": cmd,
        "Parameter": param,
        "Response": "",
        "ErrorDesc": "",
        "Result": ""
    }
    
    try:
        LOG.fw("{0}:Mulai".format(cmd))
        if cmd == "ST0":
            prepaid_common.reset_contactless(__global_response__)
        elif cmd == "000":
            prepaid_common.open_only(param, __global_response__)
        elif cmd == "001":
            prepaid_common.init_topup(param, __global_response__)
        elif cmd == "002":
            #This is KA Type too, but try to not raise the exception
            prepaid_common.auth_ka(param, __global_response__)
        elif cmd == "003":
            prepaid_common.balance_with_sn(param, __global_response__)
            prepaid_bni.bni_validation(param, __global_response__)
        elif cmd == "004":
            #This is KA Type too, but try to raise exception under function
            prepaid_common.topup(param, __global_response__)
        elif cmd == "005":
            raise SystemError("KA Type, deprecated")
        elif cmd == "006":
            raise SystemError("KA Type, deprecated")
        elif cmd == "007":
            raise SystemError("KA Type, deprecated")
        elif cmd == "008":
            prepaid_common.debit(param, __global_response__)
        elif cmd == "009":
            prepaid_common.balance(param, __global_response__)
        elif cmd == "010":
            # prepaid_dll.topup_done(param, __global_response__)
            prepaid_common.done(param, __global_response__)
        elif cmd == "011":
            prepaid_bni.bni_terminal_update(param, __global_response__)
        elif cmd == "012":
            prepaid_bni.bni_init_topup(param, __global_response__)
        elif cmd == "013":
            prepaid_bni.bni_topup(param, __global_response__)
        elif cmd == "014":
            prepaid_bni.bni_sam_balance_multi(param, __global_response__)
        elif cmd == "015":
            prepaid_bni.bni_get_purse_data_sam_multi(param, __global_response__)
        elif cmd == "016":
            prepaid_bni.bni_update_sam_crypto(param, __global_response__)
        elif cmd == "017":
            prepaid_bni.bni_get_card_no_sam_multi(param, __global_response__)
        elif cmd == "018":
            prepaid_bni.bni_reset_count_sam_multi(param, __global_response__)
        elif cmd == "019":
            prepaid_mandiri.update_balance_mandiri(param, __global_response__)
        elif cmd == "020":
            prepaid_common.get_purse_data(param, __global_response__)
        elif cmd == "021":
            prepaid_bni.bni_update_card_crypto(param, __global_response__)
        elif cmd == "022":
            prepaid_common.debit_no_init_single_report(param, __global_response__)
        elif cmd == "024":
            prepaid_bri.update_balance_bri(param,__global_response__)
        elif cmd == "025":
            prepaid_bri.GetLogBRI(param, __global_response__)
        elif cmd == "026":
            prepaid_mandiri.mandiri_C2C_refill(param, __global_response__)
        elif cmd == "027":
            prepaid_mandiri.mandiri_C2C_init(param, __global_response__)
        elif cmd == "028":
            prepaid_mandiri.mandiri_C2C_Correct(param, __global_response__)
        elif cmd == "029":
            prepaid_mandiri.mandiri_C2C_getfee(param, __global_response__)
        elif cmd == "030":
            prepaid_mandiri.mandiri_C2C_setfee(param, __global_response__)
        elif cmd == "031":
            prepaid_mandiri.mandiri_C2C_force(param, __global_response__)
        elif cmd == "033":
            prepaid_common.check_balance_C2C(param, __global_response__)
        elif cmd == "034":
            prepaid_common.send_apdu(param, __global_response__)
        elif cmd == "035":
            prepaid_mandiri.mandiri_update_sam_balance(param, __global_response__)
        elif cmd == "039":
            prepaid_mandiri.mandiri_get_log(param, __global_response__)
        elif cmd == "040":
            prepaid_bni.bni_card_get_log(param, __global_response__)
        elif cmd == "077":
            prepaid_bni.bni_card_get_log_custom(param, __global_response__)
        elif cmd == "042":
            prepaid_bni.bni_sam_get_log(param, __global_response__)
        elif cmd == "041":
            prepaid_mandiri.mandiri_get_last_report(param, __global_response__)
        elif cmd == "043":
            # TopUpDKI
            raise SystemError("Deprecated, use 051 and 052")
        elif cmd == "044":
            prepaid_bca.update_balance_bca(param,__global_response__)
        elif cmd == "045":
            prepaid_bca.reversal_bca(param, __global_response__)
        elif cmd == "046":
            prepaid_bca.update_bca(param, __global_response__)
        elif cmd == "048":
            prepaid_bca.get_card_info_bca(param, __global_response__)
        elif cmd == "049":
            prepaid_bri.reversal_bri(param, __global_response__)
        elif cmd == "051":
            prepaid_dki.DKI_RequestTopup(param, __global_response__)
        elif cmd == "052":
            prepaid_dki.DKI_Topup(param, __global_response__)
        elif cmd == "064":
            prepaid_bri.reversal_bri(param, __global_response__)
        else:
            raise SystemError("Command ["+cmd+"] not included in Service VM Command Sub [QPROX] ")
    except:
        trace = traceback.format_exc()
        formatted_lines = trace.splitlines()
        err_message = traceback._cause_message
        LOG.fw("LIB ERROR = ", formatted_lines[-1], True)
        print(err_message)
        __global_response__["Result"] = "EXCP"
        __global_response__["ErrorDesc"] = trace
    finally:
        LOG.fw("LIB [{0}]: DONE".format(cmd))
        # Bind Last Reader Resposne Into Common Variable
        _Common.LAST_READER_ERR_CODE = __global_response__["Result"]
        return __global_response__
