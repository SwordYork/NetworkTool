import smtpd
import asyncore

class anonySmtpServer(smtpd.SMTPServer):

    def process_message(self,peer,mailfrom,rcpttos,data):
        print "Receiving message from:", peer
        print "Message addressed from:", mailfrom
        print "Message addressed to  :", rcpttos 
        print "Message length        :",len(data)
        print "Message relay to      :",self._remoteaddr
        refused = self._deliver(mailfrom, rcpttos, data)
        # TBD: what to do with refused addresses?
        if(refused):
            print 'we got some refusals:', refused

    def _deliver(self, mailfrom, rcpttos, data):
        import smtplib
        refused = {}
        try:
            s = smtplib.SMTP()
            s.connect(self._remoteaddr[0], self._remoteaddr[1])
            try:
                refused = s.sendmail(mailfrom, rcpttos, data)
            finally:
                s.quit()
        except smtplib.SMTPRecipientsRefused, e:
            print 'got SMTPRecipientsRefused'
            refused = e.recipients
        except (socket.error, smtplib.SMTPException), e:
            print 'got', e.__class__
            # All recipients were refused.  If the exception had an associated
            # error code, use it.  Otherwise,fake it with a non-triggering
            # exception code.
            errcode = getattr(e, 'smtp_code', -1)
            errmsg = getattr(e, 'smtp_error', 'ignore')
            for r in rcpttos:
                refused[r] = (errcode, errmsg)
        return refused


server = anonySmtpServer(('127.0.0.1',1025),('relay.jangosmtp.net',25))
asyncore.loop()
