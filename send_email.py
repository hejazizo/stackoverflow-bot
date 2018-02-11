"""The first step is to create an SMTP object, each object is used for connection
with one server."""

import smtplib
from validate_email import validate_email
import emoji

def send_mail(receiver, randnum):
    is_valid = validate_email(receiver)
    if not is_valid:
        return "Invalid email address"

    elif is_valid:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        flag = server.verify(receiver)
        print(flag)

        #Next, log in to the server
        passwd = 'ap_project'
        sender = "aptelegrambot@gmail.com"
        server.login(sender, passwd)

        #Send the mail
        email_content = """Welcome to AUT Advanced Programming Forum!\nYour login code: {}""".format(randnum)

        msg = "\r\n".join([
          "From: {0}".format(sender),
          "To: {0}".format(receiver),
          "Subject: {0}".format('Advanced Programming Course BOT Login'),
          "",
          email_content
          ])

        server.sendmail(sender, receiver, msg)

        return emoji.emojize(':key: Enter the confirmation code sent to:\n:e-mail: ') + receiver