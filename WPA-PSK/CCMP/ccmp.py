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
ANonce = a2b_hex("3320ced2535ed697d52c272aeea799d4d188a4603142f37a240f8064d7cdf588")
SNonce = a2b_hex("b4455d0bc446645c5957434f653ad0bfa59f6be1a265fbf33b7d547b1b484534")
B = min(APmac,Clientmac)+max(APmac,Clientmac)+min(ANonce,SNonce)+max(ANonce,SNonce)


#### wpa_passphrase TP-LINK_4F6C90 LINUXZSJ
psk = pbkdf2_hex(passPhrase,ssid,4096,256)[:64]
pmk = a2b_hex(psk)
ptk = PRF512(pmk,A,B)




data = a2b_hex("0103007502010a00000000000000000001b4455d0bc446645c5957434f653ad0bfa59f6be1a265fbf33b7d547b1b484534000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001630140100000fac040100000fac040100000fac020000")
mic = hmac.new(ptk[0:16],data,hashlib.sha1) 
print "EAPOL 2 MIC: 887342b8161df230c84880cbe9074ff8"
print "Calc    MIC:",mic.hexdigest()[0:32]


data = a2b_hex("020300970213ca001000000000000000023320ced2535ed697d52c272aeea799d4d188a4603142f37a240f8064d7cdf58800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000384bcaf58aee04b67d65c62b951ece909c5c5ae86e455ecfd5059ac633ad1e69fc480863014155b620e0b5350297306f3c76245cb1ec6f306a")
mic = hmac.new(ptk[0:16],data,hashlib.sha1)
print "EAPOL 3 MIC: d88518e6e4076d06c20879a9366831c9"
print "Calc    MIC:",mic.hexdigest()[0:32]


data = a2b_hex("0103005f02030a0000000000000000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
mic = hmac.new(ptk[0:16],data,hashlib.sha1) 
print "EAPOL 4 MIC: 52d7b03a01c73a73899adcfabbc06098"
print "Calc    MIC:",mic.hexdigest()[0:32]