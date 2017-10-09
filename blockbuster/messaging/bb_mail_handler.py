### This is the entry point for sending emails via the background worker

import logging
import redis
import blockbuster.config as config
from rq import Queue

# Set up RQ queue
conn = redis.from_url(config.REDIS_URL)
q = Queue(connection=conn)

from blockbuster.messaging import bb_email_sender


log = logging.getLogger(__name__)


def send_mail_notification(a, b, c):
    q.enqueue(send_mail, a, b, c)
    log.debug("Email notification queued.")


def send_mail(toaddr, subject, body):
    bb_email_sender.EmailSenderFactory().create().send_email(toaddr, subject, body)
