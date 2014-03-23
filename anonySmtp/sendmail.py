# -*- coding: utf-8 -*-
import smtplib
import email.utils
from email.mime.text import MIMEText


Toemail = "test@qq.com"
Fromemail = "joker@joker.com"

msg = MIMEText(u"你好!\n 你作业写完了吗？".encode('utf-8'), _charset='utf-8')
msg['To'] = email.utils.formataddr(("Recipient",Toemail))
msg['From'] = email.utils.formataddr(("joker",Fromemail))

msg['Subject'] = u"作业问题"

server = smtplib.SMTP('127.0.0.1',1025)
server.set_debuglevel(True)

try:
    server.sendmail(Fromemail,[Toemail],msg.as_string())
finally:
    server.quit()
