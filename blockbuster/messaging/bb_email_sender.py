import logging
import smtplib
import blockbuster.config as config

log = logging.getLogger(__name__)


class EmailSenderFactory:
    def __init__(self):
        pass

    def __del__(self):
        pass

    def create(self):
        if config.emailtype == "Gmail":
            return GmailEmailSender()
        elif config.emailtype == "Console":
            return ConsoleEmailSender()
        else:
            return ConsoleEmailSender()


class EmailSender:
    def __init__(self):
        pass

    def __del__(self):
        pass

    def send_email(self):
        raise NotImplementedError


class ConsoleEmailSender(EmailSender):

    def __init__(self):
        # log.debug("Instantiating a ConsoleEmailSender instance.")
        pass

    def __del__(self):
        # log.debug("Destroying a ConsoleEmailSender instance.")
        pass

    # TODO: Need to look at why this is throwing an exception on the celery worker when trying to send an email.
    # Error is  File "/Users/matt/Source/BlockBuster-SMS/bb_email_sender.py", line 52, in send_email body + "\n"
    # TypeError: cannot concatenate 'str' and 'NoneType' objects
    def send_email(self, toaddr=None, subject=None, body=None):
        email_content = ("@\n"
                         "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
                         "To: " + toaddr + "\n"
                         "Subject: " + subject + "\n"
                         "\n" +
                         body + "\n"
                         "===============================")

        print(email_content)

        # BBAuditLogger.BBAuditLoggerFactory().create().logAudit('bgwrk', 'SEND-EMAIL-CONSOLE', email_content)


class GmailEmailSender(EmailSender):

    def __init__(self):
        pass

    def send_email(self, toaddr, subject, body):

        # Set the headers of the email
        # Note: MIMEType headers were removed as they were causing emails to get classified as Junk - plain text doesn't
        # seem to have the same problem.
        headers = "\r\n".join([
                              "from: " + config.mail_username,
                              "to: " + toaddr,
                              "subject: " + "BlockBuster Notification: " + subject
                              ])

        # Combine the headers and the provided body into a single string.
        content = headers + "\r\n\r\n" + body
        log.debug(content)

        # Create a server instance to use for sending emails
        server = smtplib.SMTP(config.smtp_server)

        # Open the connection to the mail server
        log.debug("SMTP - Starting TLS")
        server.starttls()

        # Login to the mail server
        log.debug("SMTP - Logging into server")
        server.login(config.mail_username, config.mail_password)

        # Send the email!
        log.debug("SMTP - Sending email")
        server.sendmail(config.mail_username, toaddr, content)

        # Close the connection to the mail server
        log.debug("SMTP - Closing connection to server")

        print("Email sent to " + toaddr)

        email_content = "To:" + toaddr + "\n" \
                        "Subject:" + subject + "\n" \
                        "Body:" + body

        print(email_content)

        server.quit()
