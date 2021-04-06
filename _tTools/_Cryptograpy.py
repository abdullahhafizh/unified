__author__ = 'fitrah.wahyudi.imam@gmail.com'

import os
import hashlib
import base64
import datetime

from Crypto.Cipher import AES
import Crypto.Cipher.AES
from binascii import hexlify, unhexlify

import json


def bin2hex(string):
    bytes_str = bytes(string, 'utf-8')
    return hexlify(bytes_str)


# public static function toHexReverse($string, $length=6){
#   $dec = dechex((int)($string));
#   if (strlen($dec) != $length) $dec = str_pad($dec, $length, '0', STR_PAD_LEFT);
#   return self::reverse($dec);
# }

def to_hex_reverse(string='', length=6):
    dec = hex(int(string))
    if len(dec) != length:
        dec = dec.zfill(length)
    return reverse(dec)

#    public static function reverse($string, $length=2){
#         return implode('', array_reverse(str_split($string, $length)));
#     }

def reverse(string='', length=2):
    if len(string) % 2 != 0:
        string += ' '
    return "".join(map(str.__add__, string[-length::-length], string[-1::-length]))


    # public static function convertToKey($clue='0'){
    #     return strtoupper(md5($clue));
    # }
    
def convert_to_key(clue='0'):
    return hashlib.md5(clue.encode('utf-8')).hexdigest()


    # public static function convertToIV($clue='0', $length=16){
    #     $iv = '';
    #     do {
    #         $iv .= (string)$clue;
    #     } while(strlen($iv) < $length);
    #     return strrev(substr($iv, -$length));
    # }
    
def convert_to_iv(clue='0', length=16):
    iv = ''
    while (len(iv) < length):
        iv += clue
        if len(iv) == length:
            break
    return iv[:16][::-1]


BLOCK_SIZE = 32;
BLOCK_SZ = 14;
PADDING = '^';


    # private static function padString($string){
    #     $pad_no = self::BLOCK_SIZE - strlen($string) % self::BLOCK_SIZE;
    #     $result = $string.str_repeat(self::PADDING, $pad_no);
    #     return $result;
    # }

def pad_string(string=''):
    pad_no = BLOCK_SIZE - len(string) % BLOCK_SIZE
    return string + (PADDING*pad_no)


#  public static function encrypt($string, $key='1DD08E3FC32981B96EDAA6E1768A454D', $direct=FALSE, $method='AES-128-CBC', $mode='HEX', $iv=null){
#         $class_method = explode('-', $method)[0];
#         $output = new \stdClass();
#         $output->status = FALSE;
#         $output->result = null;
#         $output->key = $key;
#         $output->length = 0;
#         $output->process = FALSE;
#         $output->method = $method;
#         $output->raw = $string;
#         $output->class_method = $class_method;
#         if (empty($string)){
#             $output->error = 'Missing Input String';
#             if ($direct) return $output->status;
#             return $output;
#         }
#         // Give Padding Input String
#         $string = self::padString($string);
#         $output->raw_padded = $string;
#         if (empty($key)) {
#             $output->error = 'Missing Secret Key';
#             if ($direct) return $output->status;
#             return $output;
#         }
#         // if ($class_method=='AES') $key = pack("H*", $key);
#         // if ($class_method=='3DES') $key .= substr($key, 0, 8);
#         // if (!self::supported($key, $method)){
#         //     $output->error = 'Key Length & Method Not Match';
#         //     if ($direct) return $output->status;
#         //     return $output;
#         // }
#         if (empty($iv)){
#             if ($method == 'AES-128-ECB') $iv = "";
#             else if ($method == '3DES-CBC') $iv = str_repeat(chr(0), mb_strlen($key, '8bit')/3);
#             else $iv = str_repeat(chr(0), mb_strlen($key, '8bit'));
#         }

#         // TARGET : CC7DC2B23C0BC32D42FA2AC1B590830C4B00C49AD8EEACBFBAAFB47457392CEA
#         $output->iv = $iv;
#         switch($class_method){
#             case 'AES':
#                 try{
#                     if ($mode=='HEX-3'){
#                         $output->process = \openssl_encrypt($string, $method, hex2bin($key), 3, $iv);
#                     } else if ($mode=='HEX') {
#                         $key = substr($key, 0, 16);
#                         $output->key = $key;
#                         $output->process = \openssl_encrypt($string, $method, $key, 3, $iv);
#                     } else {
#                         $output->process = \openssl_encrypt($string, $method, $key, OPENSSL_RAW_DATA, $iv);
#                     }
#                 } catch (Exception $e){
#                     $output->process = FALSE;
#                     $output->error = $e->getMessage();
#                 }
#                 break;
#             case '3DES':
#                 try{
#                     $output->process = \mcrypt_encrypt('tripledes', $key, $string, 'cbc', $iv);
#                 } catch (Exception $e){
#                     $output->process = FALSE;
#                     $output->error = $e->getMessage();
#                 }
#             break;
#             default:
#                 $output->process = FALSE;
#                 $output->error = 'Unknown Encryption Class Method';
#             break;
#         }
#         if (!empty($output->process)){
#             if ($mode=='HEX' && $class_method=='AES') $output->result = strtoupper(self::reverse(bin2hex($output->process)));
#             if ($mode=='HEX-3' && $class_method=='AES') $output->result = strtoupper(self::reverse(bin2hex($output->process)));
#             if ($mode=='HEX' && $class_method=='3DES') $output->result = strtoupper(bin2hex($output->process));
#             if ($mode=='BASE64') $output->result = base64_encode(bin2hex($output->process));
#         }             
#         $output->status = TRUE;
#         $output->length = strlen($output->result);
#         $output->mode = $mode;
#         unset($output->process);
#         // dd($output);
#         if ($direct) return $output->result;
#         return $output;
#     }


def encrypt(
    string='', 
    key='1DD08E3FC32981B96EDAA6E1768A454D', 
    direct=False, 
    method='AES-128-CBC', 
    mode='HEX', 
    iv=None):
    output = {
        'status': False,
        'result': None,
        'length': 0,
        'process': False,
        'method': method,
        'class_method': method.split('-')[0]
    }
    if len(string) == 0:
        output['error'] = 'Missing Input String'
        return output
    string = pad_string(string)
    output['raw'] = string
    if len(key) == 0:
        output['error'] = 'Missing Secret Key'
        return output
    output['key'] = key
    if iv is None:
        if method == 'AES-128-ECB':
            iv = ""
        elif method == '3DES-CBC':
            iv = chr(0) * (len(key)/3)
        else:
            iv = chr(0) * len(key)
    output['iv'] = iv
    if output['class_method'] == 'AES':
        try:
            if 'HEX' in mode:
                key = unhexlify(key)
            cipher = AES.new(key,AES.MODE_CBC,iv)
            output['process'] = cipher.encrypt(string)
        except Exception as e:
            output['process'] = False
            output['error'] = e
    # elif output['class_method'] == '3DES':
    #     output['process'] = False
    #     output['error'] = 'Class Method Not Supported'
    else:
        output['process'] = False
        output['error'] = 'Unknown/Unsupported Class Method'
    # Set Output
    if output['process'] is not False:
        if ('HEX' in mode and output['class_method']=='AES'):
            output['result'] = reverse(hexlify(output['process'])).upper()
        elif (mode=='HEX' and output['class_method']=='3DES'):
            output['result'] = hexlify(output['process']).upper()
        elif mode == 'BASE64':
            output['result'] = base64.encode(hexlify(output['process']))
    output['status'] = True
    output['length'] = len(output['result'])
    output.pop('process')
    if direct is True:
        return output['result']
    return output
    

def decrypt(
    string = '', 
    key='1DD08E3FC32981B96EDAA6E1768A454D', 
    direct=False, 
    method='AES-128-CBC', 
    mode='HEX', 
    iv=None, 
    padding=None
    ):
    output = {
        'status': False,
        'result': None,
        'length': 0,
        'process': False,
        'method': method,
        'class_method': method.split('-')[0]
    }
    if len(string) == 0:
        output['error'] = 'Missing Input String'
        return output       
    output['raw'] = string
    if len(key) == 0:
        output['error'] = 'Missing Secret Key'
        return output
    output['key'] = key
    if iv is None:
        if method == 'AES-128-ECB':
            iv = ""
        elif method == '3DES-CBC':
            iv = chr(0) * (len(key)/3)
        else:
            iv = chr(0) * len(key)
    output['iv'] = iv
    if output['class_method'] == 'AES':
        try:
            key = unhexlify(key)
            if 'HEX' in mode:
                string = unhexlify(reverse(string))
            elif 'mode' == 'BASE64':
                string = base64.decode(string)
            cipher = AES.new(key,AES.MODE_CBC,iv)
            output['process'] = cipher.decrypt(string)
        except Exception as e:
            output['result'] = False
            output['error'] = e
    # elif output['class_method'] == '3DES':
        # try:
        #     if mode=='HEX':
        #         output['process'] = 'DD'
        #     elif mode=='BASE64':
        #         output['process'] = 'EE'
        # except Exception as e:
        #     output['result'] = False
        #     output['error'] = e
    else:
        output['process'] = False
        output['error'] = 'Unknown/Unsupported Class Method'
    if output['process'] is not False:
        output['result'] = output['process']
        if padding is not None:
            output['result'] = output['result'].replace(padding, '')
        output['status'] = True
    else:
        output['status'] = False;
        output['result'] = False;
        output['error'] = 'Failed To Decrypt Cipher';
    output.pop('process')
    output['mode'] = mode
    if direct is True:
        return output['result']
    return output


#     public static function decrypt($string, $key='1DD08E3FC32981B96EDAA6E1768A454D', $direct=FALSE, $method='AES-128-CBC', $mode='HEX', $iv=null, $padding=null){
#         $class_method = explode('-', $method)[0];
#         $output = new \stdClass();
#         $output->status = FALSE;
#         $output->result = null;
#         $output->key = $key;
#         $output->length = 0;
#         $output->process = FALSE;
#         $output->method = $method;
#         $output->raw = $string;
#         $output->class_method = $class_method;
#         if (empty($string)){
#             $output->error = 'Missing Input String';
#             if ($direct) return $output->status;
#             return $output;
#         } 
#         if (empty($key)) {
#             $output->error = 'Missing Secret Key';
#             if ($direct) return $output->status;
#             return $output;
#         }
#         // if ($class_method=='AES') $key = pack("H*", $key);
#         // if ($class_method=='3DES') $key .= substr($key, 0, 8);
#         // if (!self::supported($key, $method)){
#         //     $output->error = 'Key Length & Method Not Match';
#         //     if ($direct) return $output->status;
#         //     return $output;
#         // }
#         // $output->input = $string;
#         if (empty($iv)){
#             if ($method == 'AES-128-ECB') $iv = "";
#             else if ($method == '3DES-CBC') $iv = str_repeat(chr(0), mb_strlen($key, '8bit')/3);
#             else $iv = str_repeat(chr(0), mb_strlen($key, '8bit'));
#         }
#         $output->iv = $iv;
#         switch($class_method){
#             case 'AES':
#                 try{
#                     if ($mode=='HEX') {
#                         $key = substr($key, 0, 16);
#                         $output->key = $key;
#                         $output->process = \openssl_decrypt(hex2bin(self::reverse($string)), $method, $key, 3, $iv);
#                     } else if ($mode=='HEX-3') {
#                         $output->process = \openssl_decrypt(hex2bin(self::reverse($string)), $method, hex2bin($key), 3, $iv);
#                     } else {
#                         $output->process = \openssl_decrypt(hex2bin(base64_decode($string)), $method, $key, OPENSSL_RAW_DATA, $iv);
#                     }
#                 } catch (Exception $e){
#                     $output->process = FALSE;
#                     $output->error = $e->getMessage();
#                 }
#             break;
#             case '3DES':
#                 try{
#                     // $key = md5(utf8_encode($key), true);
#                     // $key .= substr($key, 0, 8);
#                     if ($mode=='HEX') $output->process = \mcrypt_decrypt(MCRYPT_3DES, $key, hex2bin($string), MCRYPT_MODE_CBC, $iv);
#                     if ($mode=='BASE64') $output->process = \mcrypt_decrypt(MCRYPT_3DES, $key, base64_decode($string), MCRYPT_MODE_CBC, $iv);
#                 } catch (Exception $e){
#                     $output->process = FALSE;
#                     $output->error = $e->getMessage();
#                 }
#             break;
#             default:
#                 $output->process = FALSE;
#                 $output->error = 'Unknown Encryption Class Method';
#             break;
#         }
#         if (empty($output->process)){
#             $output->status = FALSE;
#             $output->result = FALSE;
#             $output->error = 'Failed To Decrypt Cipher';
#         } else {
#             $output->result =  iconv("UTF-8","UTF-8//IGNORE", $output->process);
#             if (!empty($padding)){
#                 $output->result = rtrim($output->result, $padding);
#             } else {
#                 $output->result = rtrim($output->result, self::PADDING);
#             }
#             $output->status = TRUE;
#         }
#         unset($output->process);
#         $output->mode = $mode;
#         $output->length = strlen($output->result);
#         if ($direct) return $output->result;
#         return $output;
#     }


if __name__ == '__main__':
    time_format = '%Y-%m-%d %H:%M:%S'
    sn = '0811223344'.zfill(16)
    print('SN', sn)
    key = convert_to_key(sn)
    print('Key', key)
    iv = convert_to_iv(sn)
    print('IV', iv)
    raw_message = json.dumps({
            'reff_no'   : 'TEST123',
            'caller_id' : 'TERMINAL0001',
            'amount'    : '1000',
            'expired_at': datetime.datetime.now().strftime(time_format),
            'trx_type'  : 'SALE'
            })
    print('Raw', raw_message)
    encrypted = encrypt(
            raw_message, 
            key,
            True,
            'AES-128-CBC',
            'HEX',
            iv
        )
    print('Encrypted', encrypted)
    decrypted = decrypt(
            encrypted, 
            key,
            True,
            'AES-128-CBC',
            'HEX',
            iv,
            PADDING
        )
    print('Decrypted', decrypted)
