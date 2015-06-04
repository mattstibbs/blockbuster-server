# Internal Modules
import json
import bb_dbconnector_factory
import datetime
from json import JSONEncoder
from bb_logging import logger
import blockbuster.bb_command_processor
import blockbuster.bb_types

# External Modules


class DateEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        return JSONEncoder.default(self, obj)


class APIRequestProcessor():

    def __init__(self):
        self.number = 1
        pass

    # Method to handle a service status request through the API.
    # Parameters: None
    # Returns: The status of the BlockBuster service
    def service_status_get(self):
        status = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().db_status_check()
        logger.debug(status)
        return status

    # Method to handle a stats request through the API.
    # Parameters: None
    # Returns: Today's stats for the BlockBuster service
    def service_stats_get(self):
        stats = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().db_stats_check()
        logger.debug(stats)
        return stats

    # Method to handle a user status request through the API.
    # Parameters: User Mobile Number
    # Returns: JSON object containing list of blocks by user, and a list of blocks against user
    def status_get(self, requestermobile):
        request = blockbuster.bb_types.APIRequestFactory().create()
        request.requestormobile = requestermobile
        request.servicenumber = 'API'
        status = blockbuster.bb_command_processor.current_status(request)

        print(status)
        blocking = []
        for b in status['blocking']:
            block = {
                "contact": b['blockee'],
                "registration": b['blocked_reg']
            }
            blocking.append(block)

        blockedBy = []
        for b in status['blockedBy']:
            block = {
                "contact": b['blocker'],
                "registration": b['blocked_reg']
            }
            blockedBy.append(block)

        api_response = {
            "blocking": blocking,
            "blockedBy": blockedBy
        }

        return api_response

    def cars_get(self, registration):
        results = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().api_registrations_get(registration)

        if results is None:
            return registration + " Not Found", 404
        else:
            return results

    def cars_getall(self):
        results = bb_dbconnector_factory.DBConnectorInterfaceFactory()\
            .create().api_registrations_getall()

        print(results)

        if results is None:
            return "Not Found", 404
        else:
            return results

    def blocks_getall(self):
        results = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().api_blocks_getall()

        if results is None:
            return "Not Found", 404
        else:
            return results

    def smslogs_get(self):
        results = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().api_smslogs_get()

        if results is None:
            return "Not Found", 404
        else:
            return results

    def logs_get(self):
        results = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().api_logs_get()

        if results is None:
            return "Not Found", 404
        else:
            return results

    def logsms_get(self):
        dict = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().api_logsms_get()
        results = json.dumps(dict, cls=DateEncoder)
        return results