# This is the entry point for sending SMS via the background queue

# Local imports
import blockbuster.config as config
import logging
import redis
from rq import Queue

# Set up RQ queue
conn = redis.from_url(config.REDIS_URL)
q = Queue(connection=conn)

import blockbuster.bb_auditlogger
from blockbuster.messaging import bb_sms_sender

logger = logging.getLogger(__name__)


def send_sms_notification(originator, recipient, body):
    try:
        # send_sms.delay(originator, recipient, body)
        q.enqueue(send_sms, originator, recipient, body)
        logger.debug("SMS notification queued.")

    except Exception as e:

        logger.exception("Error trying to queue an SMS to be sent.")

        blockbuster.bb_auditlogger.BBAuditLoggerFactory().create().logException('app', 'QUEUE-SMS', str(e))


def send_sms(originator, recipient, body):
    logger.debug("Starting SMS send")
    bb_sms_sender.SMSSenderFactory().create().send_sms(originator, recipient, body)
