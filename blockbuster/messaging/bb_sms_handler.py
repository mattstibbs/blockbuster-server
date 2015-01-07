# This is the entry point for sending SMS via the background queue

# Local imports
import logging

from blockbuster_celery.BBCelery import bg_worker
import blockbuster.bb_auditlogger
from blockbuster.messaging import bb_sms_sender


logger = logging.getLogger('bb_log.' + __name__)

def send_sms_notification(originator, recipient, body):
    try:
        send_sms.delay(originator, recipient, body)
        logger.debug("SMS notification queued.")

    except Exception, e:

        logger.exception("Error trying to queue an SMS to be sent.")

        blockbuster.bb_auditlogger.BBAuditLoggerFactory().create().logException('app', 'QUEUE-SMS', str(e))


@bg_worker.task
def send_sms(originator, recipient, body):
    bb_sms_sender.SMSSenderFactory().create().send_sms(originator, recipient, body)
