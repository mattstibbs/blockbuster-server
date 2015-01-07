__author__ = 'mstibbs'

# Internal Modules
import blockbuster.config_services
import blockbuster.bb_dbconnector_factory as bb_dbinterface


# Process a 'Current Status' command
def current_status(request):

    # Create an analytics record for the request
    bb_dbinterface.DBConnectorInterfaceFactory()\
        .create().add_analytics_record("Count", "Command-STATUS", blockbuster.config_services
                                       .identify_service(request.servicenumber)[0])

    # Get the list of people who are blocking you in from the database
    active_blocks_as_blockee = bb_dbinterface.DBConnectorInterfaceFactory()\
        .create().get_list_of_blocks_for_blockee(request.requestormobile)

    # Work through the returned list and put them list of one dictionary object per block
    blocks_as_blockee = []

    for b in active_blocks_as_blockee:
        c = {
            "blocker": b[0],
            "blockee": b[1],
            "blocked_reg": b[2]
        }

        blocks_as_blockee.append(c)

    # Get the list of people you are blocking in from the database
    active_blocks_as_blocker = bb_dbinterface.DBConnectorInterfaceFactory()\
        .create().get_list_of_blocks_for_blocker(request.requestormobile)

    # Work through the returned list and put them in a list of one dictionary object per block
    blocks_as_blocker = []

    for b in active_blocks_as_blocker:
        c = {
            "blocker": b[0],
            "blockee": b[1],
            "blocked_reg": b[2]
        }

        blocks_as_blocker.append(c)

    # Add both lists to a single status dictionary object
    status_dict = {
        'blockedBy': blocks_as_blockee,
        'blocking': blocks_as_blocker
    }

    return status_dict


# Process a 'Block' command
def block(request):
    pass