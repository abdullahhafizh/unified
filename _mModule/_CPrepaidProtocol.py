__author__ = "wahyudi@multidaya.id"

from _mModule import _CPrepaidLog as LOG

def Compose_Request(len_data, data):
    out_data = b"\x10\x02\x08\x00\x00\x00\x00\x00\x00"
    len_str = format(len_data, 'x').upper().zfill(4)
    out_data = out_data + bytearray.fromhex(len_str)
    out_data = out_data + data
    c = 0
    for x in range(2,len(out_data)):
        c = c ^ out_data[x]
    # c = bytearray.fromhex(format(len_data, 'x').upper().zfill(2))
    out_data = out_data + c.to_bytes(1, byteorder='big') + b"\x10\x03"
    # print(out_data)
    LOG.fw("WRITE:", out_data)
    return len(out_data), out_data