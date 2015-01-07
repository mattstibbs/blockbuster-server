### This is the entry point for sending emails via the background worker

import logging

from blockbuster_celery.BBCelery import bg_worker
from blockbuster.messaging import bb_email_sender


log = logging.getLogger('bb_log.' + __name__)


def send_mail_notification(a, b, c):
    send_mail.delay(a, b, c)
    log.debug("Email notification queued.")


@bg_worker.task
def send_mail(toaddr, subject, body):
    bb_email_sender.EmailSenderFactory().create().send_email(toaddr, subject, body)
