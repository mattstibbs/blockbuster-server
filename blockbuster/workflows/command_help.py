from blockbuster.messaging import bb_sms_handler
import blockbuster.bb_logging
import blockbuster.bb_dbconnector_factory


def go(smsrequest):
    instance_name = smsrequest.instancename
    service_number = smsrequest.servicenumber
    requestor_mobile = smsrequest.requestormobile

    blockbuster.bb_dbconnector_factory.DBConnectorInterfaceFactory().create()\
        .add_analytics_record("Count", "Command-HELP", instance_name)

    blockbuster.bb_logging.logger.info("Returning Help Info")

    send_command_guide(service_number, requestor_mobile)

    return


# Respond to the user with an SMS containing hints on commands to use with BlockBuster
def send_command_guide(service_number, requestor_mobile):

    message = "'REGISTER G857TYL John Smith' to register a car.\n\n" \
              "'WHOIS G857TYL' or just 'G857TYL' for car info.\n \n" \
              "'B GF58YTL' to block someone. (1/4)"

    message2 = "'B GF58YTL AB05REF' to block multiple people.\n \n" \
               "'M G857TYL' to request someone moves their car.\n \n" \
               "'M' to ask anyone currently blocking you to move. (2/4)\n \n"

    message3 = "'OK' to acknowledge a move request.\n \n" \
               "'U GF58YTL' to unblock someone. \n \n" \
               "'U' to unblock everyone you are blocking. (3/4) \n \n"

    message4 = "'.' to get your current status.\n \n" \
               "'UNREGISTER G857TYL' to unregister a car.\n \n" \
               "Full list of commands available on the AdvancedHub. (4/4)"

    bb_sms_handler.send_sms_notification(service_number, requestor_mobile, message)
    bb_sms_handler.send_sms_notification(service_number, requestor_mobile, message2)
    bb_sms_handler.send_sms_notification(service_number, requestor_mobile, message3)
    bb_sms_handler.send_sms_notification(service_number, requestor_mobile, message4)

    return