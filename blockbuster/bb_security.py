__author__ = 'matt'

from blockbuster import bb_dbconnector_factory


def credentials_are_valid(username, password):
    db = bb_dbconnector_factory.DBConnectorInterfaceFactory().create()
    print(username)
    result = db.api_credentials_are_valid(username, password)
    print (result)
    return result
