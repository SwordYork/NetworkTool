import hmac,hashlib,binascii
from binascii import a2b_hex
from binascii import b2a_hex
from struct import Struct
from operator import xor
from itertools import izip, starmap





#################################
##### https://github.com/mitsuhiko/python-pbkdf2/blob/master/pbkdf2.py
#################################
_pack_int = Struct('>I').pack


def pbkdf2_hex(data, salt, iterations=1000, keylen=24, hashfunc=None):
    """Like :func:`pbkdf2_bin` but returns a hex encoded string."""
    return pbkdf2_bin(data, salt, iterations, keylen, hashfunc).encode('hex')


def pbkdf2_bin(data, salt, iterations=1000, keylen=24, hashfunc=None):
    """Returns a binary digest for the PBKDF2 hash algorithm of `data`
    with the given `salt`.  It iterates `iterations` time and produces a
    key of `keylen` bytes.  By default SHA-1 is used as hash function,
    a different hashlib `hashfunc` can be provided.
    """
    hashfunc = hashfunc or hashlib.sha1
    mac = hmac.new(data, None, hashfunc)
    def _pseudorandom(x, mac=mac):
        h = mac.copy()
        h.update(x)
        return map(ord, h.digest())
    buf = []
    for block in xrange(1, -(-keylen // mac.digest_size) + 1):
        rv = u = _pseudorandom(salt + _pack_int(block))
        for i in xrange(iterations - 1):
            u = _pseudorandom(''.join(map(chr, u)))
            rv = starmap(xor, izip(rv, u))
        buf.extend(rv)
    return ''.join(map(chr, buf))[:keylen]
  

######################################
# Only work for TKIP
######################################


'''
passPhrase="10zZz10ZZzZ"
ssid        = "Netgear 2/158"
A           = "Pairwise key expansion\0"
APmac       = a2b_hex("001e2ae0bdd0")
Clientmac   = a2b_hex("cc08e0620bc8")
ANonce      = a2b_hex("61c9a3f5cdcdf5fae5fd760836b8008c863aa2317022c7a202434554fb38452b")
SNonce      = a2b_hex("60eff10088077f8b03a0e2fc2fc37e1fe1f30f9f7cfbcfb2826f26f3379c4318")
B           = min(APmac,Clientmac)+max(APmac,Clientmac)+min(ANonce,SNonce)+max(ANonce,SNonce)
data = a2b_hex("0103005ffe01090020000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
pmk = a2b_hex("01b809f9ab2fb5dc47984f52fb2d112e13d84ccb6b86d4a7193ec5299f851c48")
'''




def PRF512(pmk,A,B):
  ptk1 = hmac.new(pmk, binascii.a2b_qp(A)+ B + chr(0), hashlib.sha1).digest()
  ptk2 = hmac.new(pmk, binascii.a2b_qp(A)+ B + chr(1), hashlib.sha1).digest()
  ptk3 = hmac.new(pmk, binascii.a2b_qp(A)+ B + chr(2), hashlib.sha1).digest()
  ptk4 = hmac.new(pmk, binascii.a2b_qp(A)+ B + chr(3), hashlib.sha1).digest()
  return ptk1+ptk2+ptk3+ptk4[0:4]


passPhrase = "LINUXZSJ"
ssid = "TP-LINK_4F6C90"
A = "Pairwise key expansion\0"
APmac = a2b_hex("20dce64f6c90")
Clientmac = a2b_hex("e0b9a51fe794")
ANonce = a2b_hex("3320ced2535ed697d52c272aeea799d4d188a4603142f37a240f8064d7cdf58f")
SNonce = a2b_hex("93b0f1cd466efd5f6eb146ffbad9c9c86a74a961539dd3ef3b47f50da5298266")
B = min(APmac,Clientmac)+max(APmac,Clientmac)+min(ANonce,SNonce)+max(ANonce,SNonce)


#### wpa_passphrase TP-LINK_4F6C90 LINUXZSJ
psk = pbkdf2_hex(passPhrase,ssid,4096,256)[:64]
pmk = a2b_hex(psk)
ptk = PRF512(pmk,A,B)



data = a2b_hex("01030077fe01090020000000000000000193b0f1cd466efd5f6eb146ffbad9c9c86a74a961539dd3ef3b47f50da52982660000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000018dd160050f20101000050f20201000050f20201000050f202")
mic = hmac.new(ptk[0:16],data) 
print "EAPOL 2 MIC: cde68e2e62ef20e6ed323b56b04e8b95"
print "Calc    MIC:",mic.hexdigest()


data = a2b_hex("02030077fe01c9002000000000000000023320ced2535ed697d52c272aeea799d4d188a4603142f37a240f8064d7cdf58f0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000018dd160050f20101000050f20201000050f20201000050f202")
mic = hmac.new(ptk[0:16],data) 
print "EAPOL 3 MIC: ce52ff9185830f6bf2f50e1d59d564b4"
print "Calc    MIC:",mic.hexdigest()


data = a2b_hex("0103005ffe01090020000000000000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
mic = hmac.new(ptk[0:16],data) 
print "EAPOL 4 MIC: aa293e1806f3897d642632ee49a0f24f"
print "Calc    MIC:",mic.hexdigest()