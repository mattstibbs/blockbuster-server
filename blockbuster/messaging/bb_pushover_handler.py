import http.client
import urllib
import logging

import blockbuster.config as config
import blockbuster.bb_auditlogger as bb_auditlogger
from blockbuster_celery.bb_celery import bg_worker

log = logging.getLogger(__name__)


def send_push_notification(a, b, c, d):
    send_push_message.delay(a, b, c, d)
    log.debug("Pushover notification queued.")


@bg_worker.task
def send_push_message(user_key, message, message_title, service_number):

    try:
        conn = http.client.HTTPSConnection("api.pushover.net:443")

        conn.request("POST", "/1/messages.json",
          urllib.urlencode({
            "token": config.pushover_app_token,
            "user": user_key,
            "title": message_title,
            "message": message,
            "url": "sms:" + service_number,
            "url_title": "Send SMS to BlockBuster",
            "priority": 1
          }), {"Content-type": "application/x-www-form-urlencoded"})

        log.debug(conn.getresponse())

        audit_description = "Key:" + user_key + \
                            ";Title:" + message_title + \
                            ";Message:" + message

        bb_auditlogger.BBAuditLoggerFactory().create().logAudit('bgwrk', 'SEND-PUSHOVER', audit_description)

        print("Pushover notification sent to " + user_key)

    except Exception as e:
        log.error("Error sending Pushover notification \n" + str(e))
        bb_auditlogger.BBAuditLoggerFactory().create().logException('bgwrk','SEND-PUSHOVER', str(e))
