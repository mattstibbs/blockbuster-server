__author__ = 'matt'

from blockbuster.messaging import bb_email_sender
import bb_dbconnector_factory
import config
import logging

logger = logging.getLogger('bb_log.' + __name__)


class BBAuditLoggerFactory():

    def __init__(self):
        pass

    def create(self):
        return BBAuditLogger(bb_dbconnector_factory.DBConnectorInterfaceFactory().create())


class BBAuditLogger():

    def __init__(self, DBConnectorInterface):
        self.__DBConnector = DBConnectorInterface
        pass


    def __del__(self):
        pass


    def logAudit(self, process, action, description):
        try:
            self.__DBConnector.add_log_table_entry(process, 'LOG', action, description)

        except Exception, e:
            logger.error("Error adding audit log entry \n" + str(e))
            bb_email_sender.EmailSenderFactory().create().send_email(config.mail_monitoring_addr,
                                                                          'Exception Raised',
                                                                          str(e))

    def logException(self, process, action, description):
        try:
            self.__DBConnector.add_log_table_entry(process, 'EXCEPTION', action, description)

            bb_email_sender.EmailSenderFactory().create().send_email(config.mail_monitoring_addr,
                                                                          'Exception Raised',
                                                                          description)

        except Exception, e:
            logger.error("Error adding exception log entry \n" + str(e))
            bb_email_sender.EmailSenderFactory().create().send_email(config.mail_monitoring_addr,
                                                                          'Exception Raised',
                                                                          str(e))