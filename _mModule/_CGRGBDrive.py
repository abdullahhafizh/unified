__author__ = 'wahyudi@multidaya.id'

# This lib not used, for documentation only
from ctypes import *
import os.path
# import datetime
# import time
# import sys

DLL_LOAD = None

def loadDll():
    global DLL_LOAD
    me = os.path.abspath(os.path.dirname(__file__))
    DLL_PATH = os.path.join(me, "BillDepositDevDll.dll")
    print("pyt: DLL Path", DLL_PATH)
    DLL_LOAD =  windll.LoadLibrary(DLL_PATH)  

class tGRGNoteGoDest(Structure):
    pass
    _fields_ = [
        ("iType", c_byte),
        ("acDest", c_char * 8),
    ]

class SystemTime(Structure):
    pass
    _fields_ = [
        ("wYear", c_uint),
        ("wMonth", c_uint),
        ("wDayOfWeek", c_uint),
        ("wDay", c_uint),
        ("wHour", c_uint),
        ("wMinute", c_uint),
        ("wSecond", c_uint),
        ("wMilliseconds", c_uint),
    ]


class tDevReturn(Structure):
    _fields_ = [
        ("iLogicCode", c_int),
        ("iPhyCode", c_int),
        ("iHandle", c_int),
        ("iType", c_int),
        ("acDevReturn", c_char * 128 ),
        ("acReserve", c_char * 128 ),
    ]

class tCIMStatusInfo(Structure):
    _fields_ = [
        ("wDevice", c_int),
        ("wCashIn", c_int),
        ("wCashOut", c_int),
        ("wBuffer", c_int),
        ("wEnableMode", c_int),
        ("wTransport", c_int),
        ("wStacker", c_int),
        ("iStackerCount", c_int),
    ]

class tCIMCashInfo(Structure):
    _fields_ = [
        ("acCurrency", c_char * 4),
        ("iCount", c_int),
        ("lDenomination", c_int),
        ("cSerial", c_char),
        ("iDirection", c_int),
        ("iWay", c_int),
    ]    

class tGRGNoteDetails(Structure):
    _fields_ = [
        ("uiID", c_int),
        ("sSysTime", POINTER(SystemTime)),
        ("acJournalNo", c_char * 32),
        ("acAccountNo", c_char * 48),
        ("byTimes", c_byte),
        ("wNoteIndex", c_uint),
        ("byValidation", c_byte),
        ("byFaceWay", c_byte),
        ("wDenomination", c_uint),
        ("sNoteGoDest", POINTER(tGRGNoteGoDest)),
        ("acImageFileName", c_char * 64),
        ("acSerialNo", c_char * 32),
        ("acMac", c_char * 8),
        ("byMatchCount", c_byte),
    ]

class tGRGNoteDetails(Structure):
    _fields_ = [
        ("uiID", c_int),
        ("sSysTime", POINTER(SystemTime)),
        ("acJournalNo", c_char * 32),
        ("acAccountNo", c_char * 48),
        ("byTimes", c_byte),
        ("wNoteIndex", c_uint),
        ("byValidation", c_byte),
        ("byFaceWay", c_byte),
        ("wDenomination", c_uint),
        ("sNoteGoDest", POINTER(tGRGNoteGoDest)),
        ("acImageFileName", c_char * 64),
        ("acSerialNo", c_char * 32),
        ("acMac", c_char * 8),
        ("byMatchCount", c_byte),
    ]

class tCIMOCRInfo(Structure):
    _fields_ = [
        ("acORCInfo", c_char),
        ("byImageBuffer", POINTER(c_ubyte)),
        ("uiBuferrLen", c_uint32),
    ]

class tDevReturnArray(Structure):
    _fields_ = [
        ("arrDevReturn",  tDevReturn * 8),
    ]

class GRGBDrive():    
    BILL_DEPOSIT_STATCUOK= (0)
    BILL_DEPOSIT_STATCUFULL=(1)
    BILL_DEPOSIT_STATCUHIGH=(2)
    BILL_DEPOSIT_STATCULOW=(3)
    BILL_DEPOSIT_STATCUEMPTY=(4)
    BILL_DEPOSIT_STATCUINOP=(5)
    BILL_DEPOSIT_STATCUMISSING=(6)
    BILL_DEPOSIT_STATCUNOVAL=(7)
    BILL_DEPOSIT_STATCUNOREF=(8)
    BILL_DEPOSIT_STATCUMANIP=(9)

    BILL_CASH_DIRECTION_ONE=(0)
    BILL_CASH_DIRECTION_TWO=(1)
    BILL_CASH_DIRECTION_THR=(2)
    BILL_CASH_DIRECTION_FOR=(3)
    BILL_CASH_DIRECTION_STA	=(4)
    BILL_CASH_DIRECTION_BOX=(5)
    BILL_CASH_DIRECTION_BV=(6)
    BILL_CASH_DIRECTION_PORT=(7)

# 通用定义
    SUCCESS=0	                                                # 成功

    FAIL=1	                                                    # 失败
    GRG_BNCTL_REC_MAX=4                                         # 失败

    W_UNSUPPORT_COMMAND=998		                                # 不支持的命令
#================================================================================================
        
#=== BA08机芯 ====PHYSICAL=ERROR==DEFINE========================= BEGIN
                                                                # 错误分类
    S_BA08DEV_BASE=14400					                    # 错误码定义起始值
    W_BA08DEV_BASE=S_BA08DEV_BASE+10		                    # 14410 警告阈值
    E_BA08DEV_FATA_BASE	=S_BA08DEV_BASE+40		                # 14440 严重错阈值

    W_BA08DEV_CASH_INLET=W_BA08DEV_BASE+1		                # 14411 0001,入钞口有钞票,警告，请拿走入钞口钞票
    W_BA08DEV_NV_PARAM_ERROR=W_BA08DEV_BASE+2		            # 14412 0002,读出NV的配置数与给定的不符,警告：重新配置
    W_BA08DEV_NO_CASH=W_BA08DEV_BASE+3		                    # 14413 0003,存钞的时候通道没有钞票,警告：塞入钞票
    W_BA08DEV_MODULE_STATUS	=W_BA08DEV_BASE+4		            # 14414 0004,获取钞票信息的时候，机芯状态不正确,警告：机芯状态不正确
    W_BA08DEV_OUTPUT_HAS_ITEM=W_BA08DEV_BASE+5		            # 14415 0005,退钞口有钞票
    W_BA08DEV_REJECT_ALL_ITEM=W_BA08DEV_BASE+6		            # 14416 0006,钞票整叠拒收
    W_BA08DEV_NO_GET_CASHINFO=W_BA08DEV_BASE+7		            # 14417 0007,未获取钞票信息
    W_BA08DEV_INIT_ITEM_REJECT=W_BA08DEV_BASE+8		            # 14418 0008,初始化有钞票退到退钞口
    W_BA08DEV_INIT_ITEM_CASS_IN	=W_BA08DEV_BASE+9		        # 14419 0009,初始化有钞票入钱箱
    W_BA08DEV_CASH_FROM_ENTRANCE=W_BA08DEV_BASE+10		        # 14420 00011,初始化时，有钞票从入钞口进入钱箱
    W_BA08DEV_USB_ERROR	=W_BA08DEV_BASE+11		                # 14421	  ,传输图像的USB通道有错,检查是否已接USB线

    W_BA08DEV_CASH_IN_STATE	= W_BA08DEV_BASE+27		            # 14437      已开始入钞动作
    W_BA08DEV_NOCASH_RECEIVED=W_BA08DEV_BASE+28		            # 14438      没有检测到钞票
    W_BA08DEV_CASH_REJECTED	=W_BA08DEV_BASE+29		            # 14439 02xx,不能识别的钞票,警告：xx为拒钞原因

    E_BA08DEV_MAIN_MOTOR_CW	=E_BA08DEV_FATA_BASE+0	            # 14440 3000,主马达正转失败,错误，检查主马达或传感器
    E_BA08DEV_MAIN_MOTOR_CCW=E_BA08DEV_FATA_BASE+1	            # 14441 3001,主马达反转失败,错误，检查主马达或传感器
    E_BA08DEV_PUSHER_MOTOR_CW=E_BA08DEV_FATA_BASE+2	            # 14442 3002,压钞马达正传失败,错误，检查压钞马达或传感器
    E_BA08DEV_PUSHER_MOTOR_CCW	=E_BA08DEV_FATA_BASE+3	        # 14443 3003,压钞马达反传失败,错误，检查压钞马达或传感器
    E_BA08DEV_RECTIFY_MOTOR_CW	=E_BA08DEV_FATA_BASE+4	        # 14444 3004,纠偏马达正传失败,错误，检查纠偏马达或传感器
    E_BA08DEV_RECTIFY_MOTOR_CCW	=E_BA08DEV_FATA_BASE+5	        # 14445 3005,纠偏马达反传失败,错误，检查纠偏马达或传感器
    E_BA08DEV_EM_OPEN_FAIL	=E_BA08DEV_FATA_BASE+6	            # 14446 3006,夹钞拉力挚打开失败,错误，检查入口连杆拉力挚或传感器
    E_BA08DEV_EM_CLOSE_FAIL	=E_BA08DEV_FATA_BASE+7          	# 14447 3007,夹钞拉力挚释放失败,错误，检查入口连杆拉力挚或传感器

    E_BA08DEV_CASSETTE_FULL	=E_BA08DEV_FATA_BASE+8	            # 14448 3100,钱箱满,错误，换钱箱
    E_BA08DEV_CASSETTE_INEXISTS	=E_BA08DEV_FATA_BASE+9	        # 14449 3101,检测不到钱箱,错误，放入钱箱，并锁上钱箱
    E_BA08DEV_NV_NO_CALIBRATE=E_BA08DEV_FATA_BASE+10	        # 14450 3102,NV未校准,错误，校准NV
    E_BA08DEV_NV_NOT_CONFIGURE=E_BA08DEV_FATA_BASE+11	        # 14451 3103,NV未配置,错误，配置NV
    E_BA08DEV_NV_TIMEOUT=E_BA08DEV_FATA_BASE+12	                # 14452 3104,识别超时,错误，检查NV
    E_BA08DEV_CASHIN_SYSTEM_ERROR=E_BA08DEV_FATA_BASE+13	    # 14453 3200,准备入钞时，系统处于错误状态,错误，检查机芯
    E_BA08DEV_CASHIN_CASH_IN_CHANNEL=E_BA08DEV_FATA_BASE+14	    # 14454 3201,准备入钞时，通道内有钞票,错误，检查通道传感器，清理通道
    E_BA08DEV_CASHIN_CASSETTE_FULL=E_BA08DEV_FATA_BASE+15	    # 14455 3202,准备入钞时，钱箱已满,错误，检查机芯，更换钱箱
    E_BA08DEV_CASHIN_EM_ABNORMAL=E_BA08DEV_FATA_BASE+16	        # 14456 3203,准备入钞时，夹钞电磁阀异常,检查夹钞电磁阀或者U型传感器
    E_BA08DEV_CASHIN_RECTIFY_MOTOR_ORG=	E_BA08DEV_FATA_BASE+17  # 14457 3204,准备入钞时，纠偏马达回归初始位置失败
    E_BA08DEV_CASS_NOEXIST_CASHIN = E_BA08DEV_FATA_BASE+47	    # 14487 3205,准备入钞时，钱箱不存在...

    E_BA08DEV_INIT_CASSETTE_INEXISTS=E_BA08DEV_FATA_BASE+18	    # 14458 4000,初始化时，钱箱不存在,错误：检查钱箱或者钱箱到位传感器
    E_BA08DEV_INIT_CASH_IN_CHANNEL=E_BA08DEV_FATA_BASE+19	    # 14459 4001,初始化时，通道内有钞票,错误：清里通道
    E_BA08DEV_INIT_CASSETTE_EXIST_SENSOR=E_BA08DEV_FATA_BASE+20	# 14460 4002,初始化时，钱箱存在检测错误,错误：传感器错误或者压钞马达错误
    E_BA08DEV_INIT_PUSHER_OPEN_FAIL=E_BA08DEV_FATA_BASE+21	    # 14461 4003,初始化时，压钞电磁阀吸合错误,错误：检查电磁阀
    E_BA08DEV_INIT_PUSHER_CLOSE_FAIL=E_BA08DEV_FATA_BASE+22	    # 14462 4004,初始化时，压钞电磁阀释放错误,错误：检查电磁阀
    E_BA08DEV_INIT_RECTIFY_R_SENSOR=E_BA08DEV_FATA_BASE+23	    # 14463 4005,初始化时，纠偏马达或纠偏右传感器错误
    E_BA08DEV_INIT_RECTIFY_L_SENSOR=E_BA08DEV_FATA_BASE+24	    # 14464 4006,初始化时，纠偏马达或纠偏左传感器错误
    E_BA08DEV_DISPART_SENSOR= E_BA08DEV_FATA_BASE+46	        # 14486 4007,分钞传感器被挡,...

    E_BA08DEV_RECTIFY_ORG=E_BA08DEV_FATA_BASE+25	            # 14465 8000,塞入钞票时，检测到纠偏不在初始位置,错误：检查纠偏是否到位
    E_BA08DEV_RECTIFY_STOPPER=E_BA08DEV_FATA_BASE+26	        # 14466 8001,塞钞时纠偏不在初始位置,错误：检查纠偏挡机构
    E_BA08DEV_SCAN_TIMEOUT=E_BA08DEV_FATA_BASE+27	            # 14467 8002,扫描超时,错误：检查主马达或码盘
    E_BA08DEV_PUSHER_PULL_FAIL=E_BA08DEV_FATA_BASE+28	        # 14468 8003,钱箱压钞杆收回失败,错误：检查压钞杆或者传感器
    E_BA08DEV_CASSETTE_PUSHER_FAIL=E_BA08DEV_FATA_BASE+42	    # 14482 8004,钱箱压钞杆推出失败...
    E_BA08DEV_CASSETTE_CHANNEL_FAIL	=E_BA08DEV_FATA_BASE+43	    # 14483 8005,钞票进入钱箱通道失败...
    E_BA08DEV_PUSH_CASHOUT_ERROR=E_BA08DEV_FATA_BASE+44	        # 14484 8006,压钞时有钞票从钱箱通道退出...
    E_BA08DEV_CASSETTE_FULL_ERROR=E_BA08DEV_FATA_BASE+45	    # 14485 8007,钱箱满...
    E_BA08DEV_DISPART_TIMEOUT=E_BA08DEV_FATA_BASE+33	        # 14473 8008,分钞超时,...
    E_BA08DEV_EJECT_CASH_IN_CHANNEL	=E_BA08DEV_FATA_BASE+34	    # 14474 8009,退钞时,通道有钞...

    E_BA08DEV_CMD_ERROR=E_BA08DEV_FATA_BASE+29	                # 14469 9000,命令帧错,错误，确认硬件工作状态，命令格式和命令校验信息
    E_BA08DEV_PARAM_ERROR=E_BA08DEV_FATA_BASE+30	            # 14470 9001,参数错误,错误，更改成正确命令参数，详见第6章
    E_BA08DEV_VERIFY_ERROR=E_BA08DEV_FATA_BASE+31	            # 14471 9002,校验错误,错误，更改成正确命令参数，详见第6章
    E_BA08DEV_UNSUPPORT_CMD=E_BA08DEV_FATA_BASE+32	            # 14472 9003,不支持的命令,...

    E_BA08DEV_MAIN_CHANNEL_ERROR=E_BA08DEV_FATA_BASE+35	        # 14475 8010,主通道传感器异常...
    E_BA08DEV_EJECT_FAIL_CASSETTE_ERROR=E_BA08DEV_FATA_BASE+36	# 14476 8011,钱箱错误后退钞失败...
    E_BA08DEV_DISPART_CASSETTE_FULL=E_BA08DEV_FATA_BASE+37	    # 14477 8012,分钞失败后压钞检测到钱箱满...
    E_BA08DEV_DISPART_PUSHER_FAIL=E_BA08DEV_FATA_BASE+38	    # 14478 8013,分钞失败后推出压钞板失败...
    E_BA08DEV_DISPART_CASHOUT_CASS=E_BA08DEV_FATA_BASE+39	    # 14479 8014,分钞失败后压钞时有钞票从钱箱通道退出...
    E_BA08DEV_DISPART_PUSHER_BACK_ERR=E_BA08DEV_FATA_BASE+40	# 14480 8015,分钞失败后钱箱压钞杆收回失败...
    E_BA08DEV_DISPART_CASHOUT_ERROR=E_BA08DEV_FATA_BASE+41	    # 14481 8016,压钞失败后有退钞...
    E_BA08DEV_DISPART_TOP_ERROR=E_BA08DEV_FATA_BASE+42	        # 14482 8021,钞票脱离上部机芯失败

    E_BA08DEV_UNKOWN_ERROR=E_BA08DEV_FATA_BASE+50	            # 14490 未知错误
    E_BA08DEV_CASHIN_START=E_BA08DEV_FATA_BASE+51	            # 14491 已经开始存款过程
    E_BA08DEV_CASHIN_NOT_START=E_BA08DEV_FATA_BASE+52	        # 14492 未开始存款过程

    E_BA08DEV_UNSUPPORT=E_BA08DEV_FATA_BASE+54	                # 14494 不支持的命令
    E_BA08DEV_LOADLIBRARY=E_BA08DEV_FATA_BASE+55	            # 14495 装载动态库失败
    E_BA08DEV_SENDDATA=E_BA08DEV_FATA_BASE+56	                # 14496 发送数据失败
    E_BA08DEV_RECVDATA=E_BA08DEV_FATA_BASE+57	                # 14497 接收数据错误
    E_BA08DEV_DEVCFG=E_BA08DEV_FATA_BASE+58	                    # 14498 配置文件错
    E_BA08DEV_TIMEOUT=E_BA08DEV_FATA_BASE+59	                # 14499 通信超时

    W_BA08DEV_NEW_ERROR=14410
    W_BA08DEV_FSN_ERROR	=14501

    def __init__(self):
        me = os.path.abspath(os.path.dirname(__file__))
        DLL_PATH = os.path.join(me, "BillDepositDevDll.dll")
        print("pyt: DLL Path", DLL_PATH)
        self.dll =  windll.LoadLibrary(DLL_PATH)    

    def CIM_SetCommPara(self, p_psStatus=tDevReturn()):
        global DLL_LOAD
        p_pointer = pointer(p_psStatus)
        func = DLL_LOAD.CIM_SetCommPara
        res = func(p_pointer)
        return res, p_psStatus
    
    def CIM_Init(self, p_iAction=0, p_psStatus=tDevReturn()):
        p_pointer = pointer(p_psStatus)
        res = self.dll.CIM_Init(p_iAction, p_pointer)
        return res, p_psStatus

    def CIM_GetStatus(self, p_psStatusInfo=tCIMStatusInfo(), p_psStatus=tDevReturn()):
        p_pointer = pointer(p_psStatusInfo)        
        p_pointer1 = pointer(p_psStatus)
        res = self.dll.CIM_GetStatus(p_pointer, p_pointer1)
        return res, p_psStatusInfo, p_psStatus

    def CIM_PrepareDeposit(self,  p_psStatus=tDevReturn()):
        p_pointer = pointer(p_psStatus)
        res = self.dll.CIM_PrepareDeposit(p_pointer)
        return res, p_psStatus
    
    def CIM_GetCashInfo(self, p_psCashInfo=tCIMCashInfo(), p_iCashNumber = 0, p_psStatus=tDevReturn()):
        p_pointer1 = pointer(p_psCashInfo)
        p_pointer2 = pointer(p_iCashNumber)
        p_pointer3 = pointer(p_psStatus)
        res = self.dll.CIM_GetCashInfo(p_pointer1, p_pointer2, p_pointer3)
        return res, p_psCashInfo, p_iCashNumber, p_psStatus
    
    def CIM_CashInTo(self, p_pcPosition = 0, p_psStatus=tDevReturn()):
        p_pointer = pointer(p_psStatus)
        res = self.dll.CIM_CashInTo(p_pcPosition, p_pointer)
        return res, p_psStatus

    def CIM_CashOutFrom(self, p_pcPosition = 0, p_psStatus=tDevReturn()):
        p_pointer = pointer(p_psStatus)
        res = self.dll.CIM_CashOutFrom(p_pcPosition, p_pointer)
        return res, p_psStatus

    def CIM_CancelPrepare(self, p_psStatus=tDevReturn()):
        p_pointer = pointer(p_psStatus)
        res = self.dll.CIM_CancelPrepare(p_pointer)
        return res, p_psStatus
    
    def CIM_GetNvNotesInfoEx(self, p_psNoteDetails=tGRGNoteDetails(), p_uiNumOfItems=0, p_byNoteType=0x00, p_pcFsnFileName="", p_psStatus=tDevReturnArray()):
        p_pointer1 = pointer(p_psNoteDetails)
        p_pointer2 = pointer(p_uiNumOfItems)
        p_pointer3 = pointer(p_byNoteType)
        p_pointer4 = pointer(p_pcFsnFileName)
        p_pointer5 = pointer(p_psStatus)

        res = self.dll.CIM_GetNvNotesInfoEx(p_pointer1,p_pointer2,p_pointer3,p_pointer4,p_pointer5)
        return res, p_psNoteDetails, p_uiNumOfItems, p_byNoteType, p_pcFsnFileName, p_psStatus
    
    def CIM_GetNvNotesInfo(self, p_psNoteDetails=tGRGNoteDetails(), p_uiNumOfItems=0, p_byNoteType=0x00, p_psStatus=tDevReturnArray()):
        p_pointer1 = pointer(p_psNoteDetails)
        p_pointer2 = pointer(p_uiNumOfItems)
        p_pointer3 = pointer(p_byNoteType)
        p_pointer5 = pointer(p_psStatus)

        res = self.dll.CIM_GetNvNotesInfo(p_pointer1,p_pointer2,p_pointer3,p_pointer5)
        return res, p_psNoteDetails, p_uiNumOfItems, p_byNoteType, p_psStatus 
    
    def CIM_GetCashOCRInfo(self, p_wCashNum=0, p_psOCRInfo=tCIMOCRInfo(), p_psStatus=tDevReturn()):
        p_pointer1 = pointer(p_psOCRInfo)
        p_pointer2 = pointer(p_psStatus)

        res = self.dll.CIM_GetCashOCRInfo(p_wCashNum,p_pointer1,p_pointer2)
        return res, p_psOCRInfo, p_psStatus