import blockbuster.bb_logging as log
import blockbuster.bb_dbconnector_factory
from blockbuster.messaging import bb_sms_handler


def go(smsrequest):

    instance_name = smsrequest.instancename

    blockbuster.bb_dbconnector_factory.DBConnectorInterfaceFactory().create()\
        .add_analytics_record("Count", "Command-START", instance_name)

    send_welcome_message(smsrequest)

    return


# This method simply sends a 'Welcome' text message to the user
def send_welcome_message(smsrequest):
    blockbuster.bb_logging.logger.info("Sending Welcome Message destination_mobile=\"%s\"",
                                       smsrequest.requestormobile)

    message = "Welcome to Blockbuster! \n" \
              "\n" \
              "To register a car, text 'REGISTER AB05TYR Firstname Surname'. \n" \
              "\n" \
              "For more commands text '?'"

    bb_sms_handler.send_sms_notification(smsrequest.servicenumber,
                                         smsrequest.requestormobile,
                                         message)

    return


# This method is a WORK IN PROGRESS
def workflow_start(smsrequest):

    print(str.format("Request from: {0}", smsrequest.requestormobile))

    # Is the user registered?
    log.logger.debug("Checking if the mobile number is already registered")

    # If so - do they have any vehicles registered?
    log.logger.debug("User already has registered vehicles.")
    message = "Welcome back, Joe Bloggs! \n" \
              "\n" \
              "You have the following vehicles registered: \n" \
              "\n" \
              "Vehicle 1\n" \
              "Vehicle 2\n" \
              "\n" \
              "Text 'REGISTER AB05TYR' to add a vehicle."

    bb_sms_handler.send_sms_notification(smsrequest.servicenumber,
                                         smsrequest.requestormobile,
                                         message)

    # If not - prompt them to add a vehicle
    log.logger.debug("User has no registered vehicles - prompting to add one.")
    message = "Welcome back, Joe Bloggs! \n" \
              "\n" \
              "You don't currently have any vehicles registered." \
              "\n" \
              "Text 'REGISTER AB05TYR' to add a vehicle."

    bb_sms_handler.send_sms_notification(smsrequest.servicenumber,
                                         smsrequest.requestormobile,
                                         message)

    # Is the user on the blacklist?
    log.logger.debug("Checking if the mobile number is blacklisted")
    message = "Welcome back!\n" \
              "\n" \
              "Messages from this service are currently 'Stopped'.\n" \
              "\n" \
              "Text 'RESTART' to remove the stop on this number."

    # In which case - welcome them!
    log.logger.debug("New user - sending welcome message")

    message = "Welcome to Blockbuster! \n" \
              "\n" \
              "To register a car, text 'REGISTER AB05TYR Firstname Surname'. \n" \
              "\n" \
              "For more info visit http://bit.ly/bbparking or reply 'HELP' for commands."

    bb_sms_handler.send_sms_notification(smsrequest.servicenumber,
                                         smsrequest.requestormobile,
                                         message)