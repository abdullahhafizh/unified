from _sService import _bniSCard2
from _cConfig import _Common
import traceback
import binascii

class BniActivate(object):

    def __init__(self):
        self.debug = True
    
    def send_command(self, param, _Command):
        try:
            print("Prosess request "+param)
            response, result = _Command.send_request(param=param)
            if response == 0:
                return 0, result
            else:
                return 1, result
        except Exception as e:
            print(e)

    def activate_bni_sequence(self):
        result = ""
        code = 1
        retry = int(_Common.BNI_ACTIVATION_RETRY) - 1
        

        while retry < 5:
            print('Mencoba proses ke '+ str(5 - retry))
            print('Mengulang proses ke '+ str(retry))
            try:
                # Purse Data BNI
                res, hasil = _bniSCard2._Command.send_request(param=_bniSCard2._QPROX.QPROX['PURSE_DATA_BNI'] + '|' + str(4), output=None)
                if res == 0:
                    _bniSCard2.LOGGER.info("Purse Sebelum Aktivasi = "+ hasil)
                
                # Init BNI
                param = _bniSCard2._QPROX.QPROX['INIT_BNI']+'|'+str(4) + '|' + _Common.TID_BNI
                response, result = _bniSCard2._Command.send_request(param=param, output=_bniSCard2._Command.MO_REPORT, wait_for = 1.5)
                if response != 0 or "12292" in result : raise _bniSCard2.bniSCardError("Error response = "+ str(response) + " result = "+ result)
                
                bniHTTP = _bniSCard2.bniSCard2(mode=3, debug=True, card_no = _Common.BNI_SAM_1_NO)
                bniService = _bniSCard2.bniSCard2(mode=4, debug=True)

                TM_KEY = b"\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4A\x4B\x4C\x4D\x4E\x4F"
                IV = b"\x00\x00\x00\x00\x00\x00\x00\x00"
                BNI_PIN = b"\x12\x34\x56\x00\x00\x00\x00\x00"
                APDU_TAPCASH_SELECT = b"\x00\xA4\x04\x00\x08\xA0\x00\x42\x4E\x49\x10\x00\x01"
                CMD_GET_CREDIT_CRIPTOGRAM = b"\x80\x33\x00\x00\x73"
                CMD_GET_CREDIT_TRANSREC = b"\x80\x37\x14\x01\x32"

                # bniService.cmdTerminalInit(TM_KEY, IV, BNI_PIN)
        
                """ CREDIT PROCESSING """ 
                print("Start CREDIT PROCESSING")
                # print("APDU TAPCASH SELECT")
                # _bniSCard2.LOGGER.info("Start CREDIT PROCESSING")
                # _bniSCard2.LOGGER.info("APDU TAPCASH SELECT")
                # bniHTTP.devTransmit(APDU_TAPCASH_SELECT)    
            
                """ bniTopupSecureReadPurse """
                # bniHTTP.cmdSecureReadPurse()

                """ cmd_tapcash_get_chalange """
                CRN = bniService.cmdGetCRN()   
                SRAND = bniHTTP.cmdGetSAMRandomNumber(CRN)
                SRAND = SRAND[0:len(SRAND)-2]
                SRAND = SRAND + b'\x00'
                
                print("GET TOPUP_SECURE_PACK_DATA")
                _bniSCard2.LOGGER.info("GET TOPUP_SECURE_PACK_DATA")
                TOPUP_SECURE_PACK_DATA = bniService.devTransmit(SRAND)    
                GCC = CMD_GET_CREDIT_CRIPTOGRAM + TOPUP_SECURE_PACK_DATA
                
                print("GET_CREDIT_CRIPTOGRAM")
                _bniSCard2.LOGGER.info("GET_CREDIT_CRIPTOGRAM")
                data = bniHTTP.devTransmit(GCC)
                data = data[0:len(data)-2]
                
                print("CREDIT")
                _bniSCard2.LOGGER.info("CREDIT")
                data = bniService.devTransmit(data)
                
                print("GET GET_CREDIT_TRANSREC")
                _bniSCard2.LOGGER.info("GET GET_CREDIT_TRANSREC")
                GCT = CMD_GET_CREDIT_TRANSREC + data
                data = bniHTTP.devTransmit(GCT)   

                res2, hasil2 = _bniSCard2._Command.send_request(param=_bniSCard2._QPROX.QPROX['PURSE_DATA_BNI'] + '|' + str(4), output=None)
                if res2 == 0:
                    _bniSCard2.LOGGER.info("Purse Setelah Aktivasi = "+ hasil2)

                code = 0
                result = "Success"
            except Exception as e:
                print(traceback.format_exc())
                retry = retry - 1
                print('Mengulang proses ke '+ str(retry))
                result = "Error, see log"
            finally:
                bniHTTP.devClose()
                return code, result






    # def activate_bni_sequence(self):
    #     result = ""
    #     code = 1
    #     try:
            
            
    #         res, hasil = _bniSCard2._Command.send_request(param=_bniSCard2._QPROX.QPROX['PURSE_DATA_BNI'] + '|' + str(4), output=None)
    #         if res == 0:
    #             _bniSCard2.LOGGER.info("Purse Sebelum Aktivasi = "+ hasil)
            
            
    #         param = _bniSCard2._QPROX.QPROX['INIT_BNI']+'|'+str(4) + '|' + _Common.TID_BNI
    #         response, result = _bniSCard2._Command.send_request(param=param, output=_bniSCard2._Command.MO_REPORT, wait_for = 1.5)

    #         if response != 0 or "12292" in result : raise bniSCardError("Error response = "+ str(response) + " result = "+ result)

    #         bniHTTP = _bniSCard2.bniSCard2(mode=3, debug=True, card_no = _Common.BNI_SAM_1_NO)
    #         bniService = _bniSCard2.bniSCard2(mode=4, debug=True)

    #         TM_KEY = b"\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4A\x4B\x4C\x4D\x4E\x4F"
    #         IV = b"\x00\x00\x00\x00\x00\x00\x00\x00"
    #         BNI_PIN = b"\x12\x34\x56\x00\x00\x00\x00\x00"
    #         APDU_TAPCASH_SELECT = b"\x00\xA4\x04\x00\x08\xA0\x00\x42\x4E\x49\x10\x00\x01"
    #         CMD_GET_CREDIT_CRIPTOGRAM = b"\x80\x33\x00\x00\x73"
    #         CMD_GET_CREDIT_TRANSREC = b"\x80\x37\x14\x01\x32"

    #         # bniService.cmdTerminalInit(TM_KEY, IV, BNI_PIN)
    
    #         """ CREDIT PROCESSING """ 
    #         print("Start CREDIT PROCESSING")
    #         print("APDU TAPCASH SELECT")
    #         _bniSCard2.LOGGER.info("Start CREDIT PROCESSING")
    #         _bniSCard2.LOGGER.info("APDU TAPCASH SELECT")
    #         bniHTTP.devTransmit(APDU_TAPCASH_SELECT)    
        
    #         """ bniTopupSecureReadPurse """
    #         bniHTTP.cmdSecureReadPurse()

    #         """ cmd_tapcash_get_chalange """
    #         CRN = bniHTTP.cmdGetCRN()   
    #         SRAND = bniService.cmdGetSAMRandomNumber(CRN)
    #         SRAND = SRAND[0:len(SRAND)-2]
    #         SRAND = SRAND + b'\x00'
            
    #         print("GET TOPUP_SECURE_PACK_DATA")
    #         _bniSCard2.LOGGER.info("GET TOPUP_SECURE_PACK_DATA")
    #         TOPUP_SECURE_PACK_DATA = bniHTTP.devTransmit(SRAND)    
    #         GCC = CMD_GET_CREDIT_CRIPTOGRAM + TOPUP_SECURE_PACK_DATA
            
    #         print("GET_CREDIT_CRIPTOGRAM")
    #         _bniSCard2.LOGGER.info("GET_CREDIT_CRIPTOGRAM")
    #         data = bniService.devTransmit(GCC)
    #         data = data[0:len(data)-2]
            
    #         print("CREDIT")
    #         _bniSCard2.LOGGER.info("CREDIT")
    #         data = bniHTTP.devTransmit(data)
            
    #         print("GET GET_CREDIT_TRANSREC")
    #         _bniSCard2.LOGGER.info("GET GET_CREDIT_TRANSREC")
    #         GCT = CMD_GET_CREDIT_TRANSREC + data
    #         data = bniService.devTransmit(GCT)   

    #         res2, hasil2 = _bniSCard2._Command.send_request(param=_bniSCard2._QPROX.QPROX['PURSE_DATA_BNI'] + '|' + str(4), output=None)
    #         if res2 == 0:
    #             _bniSCard2.LOGGER.info("Purse Setelah Aktivasi = "+ hasil2)

    #         code = 0
    #         result = "Success"
    #     except Exception as e:
    #         print(traceback.format_exc())
    #         result = "Error, see log"
    #     finally:
    #         return code, result

    # def activate_bni_sequence_2(self):

    #     CMD_GET_CREDIT_CRIPTOGRAM = "8033000073"
    #     CMD_GET_CREDIT_TRANSREC = "8037140132"

    #     result = ""
    #     code = 1
        
    #     bniService = _bniSCard2.bniSCard2(mode=4, debug=True)

    #     try:
    #         res, hasil = _bniSCard2._Command.send_request(param=_bniSCard2._QPROX.QPROX['PURSE_DATA_BNI'] + '|' + str(4), output=None)
    #         if res == 0:
    #             _bniSCard2.LOGGER.info("Purse Sebelum Aktivasi = "+ hasil)
            
    #         # param = _bniSCard2._QPROX.QPROX['INIT_BNI']+'|'+str(4) + '|' + _Common.TID_BNI
    #         # response, result = _bniSCard2._Command.send_request(param=param, output=_bniSCard2._Command.MO_REPORT, wait_for = 1.5)
            
    #         # if response != 0 or "12292" in result : raise bniSCardError("Error response = "+ str(response) + " result = "+ result)

    #         bniHTTP = _bniSCard2.bniSCard2(mode=3, debug=True, card_no = _Common.BNI_SAM_1_NO)
            
    #         # hasil_kartu = bniHTTP.devTransmit(_Common.TID_BNI)
    #         # _bniSCard2.LOGGER.info("Hasil kesatu kartu = "+ binascii.b2a_hex(hasil_kartu).decode('utf-8'))
            
    #         res, hasil = _bniSCard2._Command.send_request(param='036|' + str(4), output=None)
    #         _bniSCard2.LOGGER.info("Hasil Sam = "+ hasil)

    #         hasil = hasil + "9000"
    #         crn = bytearray.fromhex(hasil)

    #         hasil_kartu = bniHTTP.cmdGetSAMRandomNumber(hasil)
    #         _bniSCard2.LOGGER.info("Hasil kedua kartu = "+ binascii.b2a_hex(hasil_kartu).decode('utf-8'))

    #         print("GET TOPUP_SECURE_PACK_DATA")
    #         _bniSCard2.LOGGER.info("GET TOPUP_SECURE_PACK_DATA")
    #         TOPUP_SECURE_PACK_DATA = bniHTTP.devTransmit(SRAND)    
    #         GCC = CMD_GET_CREDIT_CRIPTOGRAM + TOPUP_SECURE_PACK_DATA
            
    #         res, hasil = _bniSCard2._Command.send_request(param='037|' + str(4) + '|' + hasil_kartu, output=None)
    #         _bniSCard2.LOGGER.info("Hasil Kedua Sam = "+ hasil)

    #         hasil_kartu = bniHTTP.devTransmit(hasil)
    #         _bniSCard2.LOGGER.info("Hasil ketiga kartu = "+ binascii.b2a_hex(hasil_kartu).decode('utf-8'))

    #         res, hasil = _bniSCard2._Command.send_request(param='038|' + str(4) + '|' + hasil_kartu, output=None)
    #         _bniSCard2.LOGGER.info("Hasil Ketiga Sam = "+ hasil)
            
    #         hasil_kartu = bniHTTP.devTransmit(hasil)
    #         _bniSCard2.LOGGER.info("Hasil keempat kartu = "+ binascii.b2a_hex(hasil_kartu).decode('utf-8'))
                        
    #         code = 0
    #         result = "Success"
    #     except Exception as e:
    #         print(traceback.format_exc())
    #         result = "Error, see log"
    #     finally:
    #         return code, result
    