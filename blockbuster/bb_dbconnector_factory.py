import logging
import bb_dbconnector_pg

log = logging.getLogger('bb_log.' + __name__)


class DBConnectorInterfaceFactory:

    def __init__(self):
        pass

    @staticmethod
    def create():
        return bb_dbconnector_pg.PostgresConnector()