from Crypto.Cipher import DES
from Crypto.Hash import MD4
import binascii

#http://www.berghel.net/col-edit/digital_village/aug-05/dv_8-05.php
#http://www.wirelessdefence.org/Contents/AsleapMain.htm
#http://www.ciscopress.com/articles/article.asp?p=369223&seqNum=4
#http://freeradius.org/rfc/leap.txt
#http://www.rfc-editor.org/rfc/rfc2548.txt
#https://bitbucket.org/msam/pptpkit/src/1d14ccf2a8cf60ab531de29125efd7d7ce31b998?at=default
#http://tools.ietf.org/html/rfc2759#page-9
#http://www.networksorcery.com/enp/protocol/eap.htm
#http://exampledepot.8waytrips.com/egs/javax.crypto/MakeDes.html



# 56 bits to 64 bits
def expand_key(key):        
        bin_key = bin(int(binascii.b2a_hex(key),16))[2:]
        bin_key = '0' *(56 - len(bin_key)) + bin_key                #56 bits
        
        chunk = [bin_key[i*7:7*i+8] for i in range(56/7)]           #0-8,7-15,14-22
        chunk[-1] += '0'                                            #last bit

        for i in range(len(chunk)):
	  num_1 = (chunk[i][0:-1].count("1") ^ 0x1) & 0x1           #parity odd
	  chunk[i] = chunk[i][0:-1] + str(num_1)

        expanded = hex(int(''.join(chunk),2))[2:]                   #64 bits
        
        if expanded[-1] == 'L':
	  expanded = expanded[0:-1]
	  
	expanded = '0'*(16-len(expanded)) + expanded
        expanded =binascii.a2b_hex(expanded)
        return expanded



def NTPasswordHash(password):
        """ Return NTPasswordHash  """
        phash = MD4.new()
        phash.update(unicode(password).encode("utf-16le"))
 
        return phash.digest()
      
      
def ChallengeResponse(challenge, NTHash):
        """ Return Challenge Response""" 
        key1 = expand_key(NTHash[0:7])
        key2 = expand_key(NTHash[7:14])
        key3 = expand_key(NTHash[14:16]+"\x00"*5) 
        
        cr1 = (DES.new(key1, DES.MODE_ECB)).encrypt(challenge)
        cr2 = (DES.new(key2, DES.MODE_ECB)).encrypt(challenge)
        cr3 = (DES.new(key3, DES.MODE_ECB)).encrypt(challenge)
       
        return (cr1 + cr2 + cr3)
      
  
  
key = 'Mypassword'                         #please ask me for real password
key_hash = NTPasswordHash(key)


#AP ==> S
PC = binascii.a2b_hex('784b2af6845212f6')
PR = ChallengeResponse(PC,key_hash)
print "d: 3b4f2d77e8ff180a6f8e67529ef9b0eff348045e2bc787a0"
print len(PR),binascii.b2a_hex(PR)


#S ==> AP
APC = binascii.a2b_hex('e130ba399e139f30')
phash =  MD4.new()
phash.update(key_hash)
key_h_h = phash.digest()
APR = ChallengeResponse(APC,key_h_h)
print "d: 6e4706869b5f18ad373afae911313338d816a3bac6aaa00d"
print len(APR),binascii.b2a_hex(APR)
