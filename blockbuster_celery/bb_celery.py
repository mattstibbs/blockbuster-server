from celery import Celery
import logging

logger = logging.getLogger(__name__)

bg_worker = Celery('bb_celery',
                   include=['blockbuster.messaging.bb_sms_handler',
                            'blockbuster.messaging.bb_mail_handler',
                            'blockbuster.messaging.bb_pushover_handler'])

bg_worker.config_from_object('blockbuster_celery.config_celery')

if __name__ == '__main__':
    bg_worker.start()
