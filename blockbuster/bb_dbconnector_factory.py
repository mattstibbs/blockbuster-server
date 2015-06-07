import bb_dbconnector_pg

class DBConnectorInterfaceFactory:

    def __init__(self):
        pass

    @staticmethod
    def create():
        return bb_dbconnector_pg.PostgresConnector()