from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.text import MIMEText
import logging
import email.utils
from email.header import Header as EHeader
import sys
import traceback
from flask import url_for

from app.config import Config


MAIL_LOGIN = Config.core.get('mail', 'login')
MAIL_PASSWORD = Config.core.get('mail', 'password')
MAIL_HOST = Config.core.get('mail', 'host')


class MailSender(object):
    @staticmethod
    def send_invite(email_addr, invite_id):
        MailSender\
            .send_with_attachement(
                [email_addr], [email_addr], 'You have been invited to QFI',
                [], [],
                text=Config.core.get('mail', 'invite_text').format(
                    link=url_for('SignIn.index', invite_id=invite_id, _external=True)))

    @staticmethod
    def send_with_attachement(addresses, to_names, subject, attachements, att_names, text=None, html=None):
        try:
            eml = MIMEMultipart()
            body = MIMEMultipart('alternative')
            if text:
                cs = email.charset.Charset('utf-8')
                cs.body_encoding = email.charset.QP
                txt_body = MIMENonMultipart('text', 'plain', charset='utf-8')
                txt_body.set_payload(unicode(text), charset=cs)
                body.attach(txt_body)
            if html:
                html_body = MIMEText(html, 'html', 'utf-8')
                body.attach(html_body)

            for content, name in zip(attachements, att_names):
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(content)
                encode_base64(attachment)
                attachment.add_header('Content-Disposition', 'attachment; filename=%s' % name)
                eml.attach(attachment)

            eml['To'] = ', '.join(email.utils.formataddr((unicode(name), addr))
                                  for name, addr in zip(to_names, addresses))

            eml.attach(body)

            eml['Message-ID'] = email.utils.make_msgid()
            eml['Subject'] = EHeader(unicode(subject), 'utf-8')
            eml['From'] = 'qif@corkez.as'

            logging.getLogger('mail').info(eml.as_string())

            # smtp = SMTP_SSL(MAIL_HOST, 465)
            # smtp.login(MAIL_LOGIN, MAIL_PASSWORD)
            # smtp.sendmail(MAIL_LOGIN, addresses, eml.as_string())
            # smtp.quit()
        except:
            ex_type, ex_val, ex_tb = sys.exc_info()
            text = u'\nrecipients: %s\n' \
                   u'error: %s' % (addresses, u''.join(traceback.format_exception(ex_type, ex_val, ex_tb)))
            logging.getLogger('mail').error(text)
