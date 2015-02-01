__author__ = 'mstibbs'

# External Modules
from datetime import datetime

# Internal Modules
import bb_dbconnector_factory
import bb_auditlogger
import bb_types
import config_services
import bb_notification_handler
import bb_usersettings_handler as user_settings
import blockbuster.bb_command_processor
from blockbuster.workflows import start
from blockbuster.messaging.bb_pushover_handler import send_push_notification
from config import *
from messaging import bb_sms_handler
from bb_logging import logger


def process_twilio_request(request):

    logger.info('################################ NEW SMS ###############################################')

    if not within_operational_period():
        logger.info("Interaction suppressed due to time restrictions.")
        return "<Response></Response>"

    # Create an instance of an smsrequest object
    smsrequest = bb_types.SMSRequestFactory().create()

    # Extract some information from the http requests
    SMSFrom = str(request.form['From'])
    SMSTo = str(request.form['To'])

    # Strip whitespace from the beginning and end of the body of the message
    SMSBody = str(request.form['Body']).rstrip().lstrip()

    # Populate the smsrequest instance with details of the received request
    smsrequest.requestormobile = SMSFrom
    smsrequest.servicenumber = SMSTo
    smsrequest.requestbody = SMSBody

    global instancename
    global location
    instancename, location = config_services.identify_service(SMSTo)
    smsrequest.instancename = instancename

    SMSList = combinesplitregistrations(SMSBody, location)
    smsrequest.requestcommandlist = SMSList

    smsservice = "Twilio"
    smsrequest.requestsmsservice = smsservice

    # Add an analytics record for the received request
    bb_dbconnector_factory.DBConnectorInterfaceFactory()\
        .create()\
        .add_analytics_record("Count", "SMS-Receive", instancename)

    # Construct a dictionary containing details for creating a message log entry
    logentry = {
        "Direction": "I <----",
        "SMSService": smsservice,
        "Command": "",
        "Originator": SMSFrom,
        "OriginatorName": bb_dbconnector_factory.DBConnectorInterfaceFactory().create().get_name_from_mobile(SMSFrom),
        "Destination": SMSTo,
        "RecipientName": instancename,
        "Details": SMSBody
    }

    # Construct a dictionary containing details for creating an audit log entry
    audit_entry = "Originator:" + SMSFrom + \
                  ";Receipient:" + SMSTo + \
                  ";Body:" + SMSBody

    # Check the incoming message to see which function has been requested
    commandelement = smsrequest.getcommandelement()

    # Define lists of aliases for some of the commands
    start_command_list = ['START']
    help_command_list = ['HELP', '?']
    move_command_list = ['MOVE', 'M']
    block_command_list = ['BLOCK', 'B']
    unblock_command_list = ['UNBLOCK', 'U']
    unregister_command_list = ['UNREGISTER', 'UR']

    # First, check if the command is a register command. If so, process the registration.
    if commandelement == "REGISTER":
        logentry['Command'] = "REGISTER"
        bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_transaction_record(logentry)
        bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'RCVCMD-REGISTER', audit_entry)
        logger.info("REGISTER Command Received")
        register(SMSTo, SMSFrom, SMSList, location)
        return "<Response></Response>"

    if commandelement in help_command_list:
        logentry['Command'] = "HELP"
        bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_transaction_record(logentry)
        bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'RCVCMD-HELP', audit_entry)
        return syntaxhelp(SMSTo, SMSFrom)

    if commandelement in start_command_list:
        logentry['Command'] = "START"
        bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_transaction_record(logentry)
        bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'RCVCMD-START', audit_entry)
        start.send_welcome_message(smsrequest)
        return "<Response></Response>"

    # If not a registration, proceed to check that the requesting user is registered with the service.
    logger.debug("Checking that user is registered...")

    # If the user is not registered, respond asking them to register and write log entries
    if not bb_dbconnector_factory.DBConnectorInterfaceFactory().create().number_is_registered(smsrequest.requestormobile):
        logger.debug("User is not registered to use this service")
        send_not_registered_SMS(SMSTo, SMSFrom)
        bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_transaction_record(logentry)
        bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'NOT-REGISTERED', audit_entry)

        return "<Response></Response>"


    if commandelement in unregister_command_list:
        logger.info("UNREGISTER Command Received")
        logentry['Command'] = "UNREGISTER"
        bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_transaction_record(logentry)
        bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'RCVCMD-UNREGISTER', audit_entry)
        return unregister(smsrequest)

    elif commandelement == "WHOIS":
        logger.info("WHOIS Command Received")
        logentry['Command'] = "WHOIS"
        bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_transaction_record(logentry)
        bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'RCVCMD-WHOIS', audit_entry)
        whois(SMSTo, SMSFrom, SMSList)
        return "<Response></Response>"

    elif commandelement in move_command_list:
        logger.info("MOVE Command Received")
        logentry['Command'] = "MOVE"
        bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_transaction_record(logentry)
        bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'RCVCMD-MOVE', audit_entry)
        return move(SMSTo, SMSFrom, SMSList)

    elif commandelement in block_command_list:
        logger.info("BLOCK Command Received")
        logentry['Command'] = "BLOCK"
        bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_transaction_record(logentry)
        bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'RCVCMD-BLOCK', audit_entry)
        return block(SMSTo, SMSFrom, SMSList)

    elif commandelement in unblock_command_list:
        logger.info("UNBLOCK Command Received")
        logentry['Command'] = "UNBLOCK"
        bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_transaction_record(logentry)
        bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'RCVCMD-UNBLOCK', audit_entry)
        return unblock(SMSTo, SMSFrom, SMSList)

    elif commandelement == "OK":
        logger.info("MOVE Request Acknowledged")
        logentry['Command'] = "OK"
        bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_transaction_record(logentry)
        bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'RCVCMD-ACK', audit_entry)
        acknowledge_move_request(SMSTo, SMSFrom, SMSList)
        return "<Response></Response>"

    elif commandelement == ".":
        logger.info("STATUS Command Received")
        logentry['Command'] = "STATUS"
        bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_transaction_record(logentry)
        bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'RCVCMD-STATUS', audit_entry)
        current_status(smsrequest)
        return "<Response></Response>"

    elif commandelement == "PUSH":
        logger.info("PUSH Command Received")
        logentry['Command'] = "ADD_PUSHOVER_TOKEN"
        bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_transaction_record(logentry)
        bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'RCVCMD-SETTING', audit_entry)
        push(SMSTo, SMSFrom, SMSList)
        return "<Response></Response>"

    elif commandelement == "SET":
        logger.info("SET Command Received")
        logentry['Command'] = "SETTING"
        bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_transaction_record(logentry)
        bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'RCVCMD-SETTING', audit_entry)
        user_settings.setting(SMSTo, SMSFrom, SMSList)
        return "<Response></Response>"

    else:
        logger.info("Command Not Recognised - Assuming WHOIS")
        logentry['Command'] = "WHOIS"
        bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_transaction_record(logentry)
        bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app', 'RCVCMD-WHOIS', audit_entry)

        # Format the registration number so that it is all capitals
        uppercasereg = SMSBody.upper().replace(" ", "")
        logger.debug("Using Registration Plate: " + uppercasereg)
        bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, cardetails(uppercasereg))
        return "<Response></Response>"


# ============================= SMS REQUEST METHODS =============================
def current_status(smsrequest):

    # Get the current status for the requesting user
    status = blockbuster.bb_command_processor.current_status(smsrequest)

    active_blocks_as_blockee = status['blockedBy']
    active_blocks_as_blocker = status['blocking']

    # Check the list of people you are blocking in
    if len(active_blocks_as_blockee) > 0:
        text_list_of_blocks_as_blockee = "Currently being blocked by:\n\n"
        for b in active_blocks_as_blockee:

            blocker_name = bb_dbconnector_factory.DBConnectorInterfaceFactory()\
                .create().get_name_from_mobile(b['blocker'])

            text_list_of_blocks_as_blockee = text_list_of_blocks_as_blockee + blocker_name +"\n"
    else:
        text_list_of_blocks_as_blockee = "Not currently blocked in.\n"

    # Check the list of people blocking you in
    if len(active_blocks_as_blocker) > 0:
        text_list_of_blocks_as_blocker = "Currently blocking:\n\n"
        for b in active_blocks_as_blocker:

            blocked_reg = b['blocked_reg']

            blocked_name = bb_dbconnector_factory.DBConnectorInterfaceFactory()\
                .create().get_name_from_mobile(b['blockee'])

            text_list_of_blocks_as_blocker = text_list_of_blocks_as_blocker + blocked_name + " (" + blocked_reg + ")\n"
    else:
        text_list_of_blocks_as_blocker = "Not currently blocking anyone in."

    status_message = text_list_of_blocks_as_blockee + "\n" + text_list_of_blocks_as_blocker

    # Send the current status back to the user via SMS
    bb_sms_handler.send_sms_notification(smsrequest.servicenumber, smsrequest.requestormobile, status_message)

    # Also send them their current status via email
    email_subject = "Current BlockBuster Status"
    email_message = status_message
    bb_notification_handler.send_notifications(smsrequest.requestormobile, email_subject, email_message)

    return


# ============================= UTILITY METHODS =============================
# Checks whether the current time is within the operational period, and returns True if so.
# Otherwise returns False.
def within_operational_period():

    try:
        if not timerestriction:
            return True
    except Exception, e:
        bb_auditlogger.BBAuditLoggerFactory().create().logException(e)
        pass

    now = datetime.now()
    start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
    end_time = now.replace(hour=20, minute=0, second=0, microsecond=0)

    if now > end_time or now < start_time:
        return False
    else:
        return True


def cardetails(formattedreg):
# Perform a check against the database to see if the registration already exists.
# Advise user if registration is not known, otherwise proceed with obtaining details
    if checkifregexists(formattedreg) == 1:
        logger.debug("Car Does Exist")
        return selectregistration(formattedreg)

    else:
        logger.debug("Car Does Not Exist")
        return carnotexist(formattedreg)

# Check a single registration to see if it exists in the database
def checkifregexists(reg):
    return bb_dbconnector_factory.DBConnectorInterfaceFactory().create().checkifregexists(reg)


def selectregistration(requestreg):
    drivername = cardetailsfromdatabase(requestreg)
    if drivername:
        logger.debug("Returning: " + drivername)
        return drivername
    else:
        logger.debug("No Details")
        return nodriverdetails()


def cardetailsfromdatabase(requestreg):
    try:
        logger.debug("Retrieving Details From Database For Registration: " + requestreg)
        dict = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().getCarDetailsAsDictionary(requestreg)
        drivername = dict['FirstName'] + " " + dict['Surname']
        logger.debug("Car Owner Is: " + drivername)
        return "Car " + requestreg + " belongs to " + drivername
    except Exception, e:
        bb_auditlogger.BBAuditLoggerFactory().create().logException(e)
        return ""

# JB's code to combine split registations into single word with no white space
def combinesplitregistrations(message, location):

    def contains_digits(s):
        return any(char.isdigit() for char in s)

    f = message

    words = message.split(" ")

    newwords = []
    totalwords = len(words)

    e = 0
    while e < totalwords:
        thisword = words[e]

        if len(thisword) < 5 and contains_digits(thisword) and e < (totalwords-1) and len(words[e+1]) < 4:
            e += 1
            newwords.append(thisword + words[e])
            bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_analytics_record("Count", "RegistrationPlateMerge", location)
        else:
            if words[e] != "":
                newwords.append(words[e])
            else:
                pass
        e += 1

    return newwords


def unregister(smsrequest):
    bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_analytics_record("Count", "Command-UNREGISTER", smsrequest.instancename)

    if len(smsrequest.requestcommandlist) < 2:
        return notEnoughDeRegistrationDetails(smsrequest.servicenumber, smsrequest.requestormobile)

    if len(smsrequest.requestcommandlist) > 2:
        message = "You have provided too many details in your text. Unregister text should be 'UNREGISTER AB125DF'."
        bb_sms_handler.send_sms_notification(smsrequest.servicenumber, smsrequest.requestormobile, message)
        return "<Response></Response>"

    try:
        smsrequest.requestorreg = smsrequest.requestcommandlist[1].upper()

        if bb_dbconnector_factory.DBConnectorInterfaceFactory().create().remove_registration(smsrequest.requestorreg, smsrequest.requestormobile) == 1:
            message = "Car " + smsrequest.requestorreg + " has been unregistered from BlockBuster."
            logger.debug(message)
            bb_sms_handler.send_sms_notification(smsrequest.servicenumber, smsrequest.requestormobile, message)

        elif bb_dbconnector_factory.DBConnectorInterfaceFactory().create().remove_registration(smsrequest.requestorreg, smsrequest.requestormobile) == 0:
            message = "Car is not registered to this mobile number."
            logger.debug(message)
            bb_sms_handler.send_sms_notification(smsrequest.servicenumber, smsrequest.requestormobile, message)

        elif bb_dbconnector_factory.DBConnectorInterfaceFactory().create().remove_registration(smsrequest.requestorreg, smsrequest.requestormobile) == -1:
            message = "Unable to unregister car " + smsrequest.requestorreg + " - please report the issue."
            logger.error("Unable to unregister car " + smsrequest.requestorreg + ".")
            bb_sms_handler.send_sms_notification(smsrequest.servicenumber, smsrequest.requestormobile, message)

        else:
            raise Exception("Unable to unregister this car at this time.")
            logger.error("Unable to unregister car at this time.")

    except Exception, e:
        bb_auditlogger.BBAuditLoggerFactory().create().logException(e)
        message = "Unable to unregister car " + smsrequest.requestorreg + " - please report the issue."
        logger.error("Unable to unregister car " + smsrequest.requestorreg + ".")
        bb_sms_handler.send_sms_notification(smsrequest.servicenumber, smsrequest.requestormobile, message)

    return "<Response></Response>"


def respond_noregistrationspecified(ServiceNumber, RecipientNumber):
    logger.info("Returning: No Registration Specified")
    message = "You didn't provide a registration. \n \n Text '?' for help."
    bb_sms_handler.send_sms_notification(ServiceNumber, RecipientNumber, message)
    return "<Response></Response>"


def carnotexist(reg):
    logger.info("Returning: Not Found")
    return "Car with registration " + reg + " not found. \n \n Text '?' for help."


def nodriverdetails():
    logger.info("Returning: No Driver Details")
    return "Car not found. \n\n Text '?' for help."


def featurenotimplemented(SMSTo, SMSFrom, SMSList):
    logger.info("Returning: Not Implemented")
    message = "Sorry, feature not implemented yet. \n \n Text '?' for help."
    bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, message)
    return "<Response></Response>"


def notEnoughRegistrationDetails(SMSTo, SMSFrom):
    logger.info("Returning: Not Enough Details Provided")
    message = "You have not provided enough details. Please use format: \n \n'REGISTER FD05RYT Joe Bloggs'"
    bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, message)
    return "<Response></Response>"


def notEnoughDeRegistrationDetails(SMSTo, SMSFrom):
    logger.info("Returning: Not Enough Details Provided")
    message = "You have not provided enough details. Please use format: \n \n'UNREGISTER FD05RYT'"
    bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, message)
    return "<Response></Response>"


def notEnoughBlockDetails(SMSTo, SMSFrom):
    logger.info("Returning: Not Enough Details Provided")
    message = "You have not provided enough details. Please use format: \n \n'BLOCK FD05RYT' \n \nwith the registration as a single word."
    bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, message)
    return "<Response></Response>"

def send_not_registered_SMS(SMSTo, SMSFrom):
    logger.info("Returning: Please Register To Use This Service")
    message = "Please register to use BlockBuster. \n \nSimply text 'REGISTER YourNumberPlate Firstname Surname'."
    bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, message)
    return None

# Method is run when a PUSH command is received from a user
def push(SMSTo, SMSFrom, SMSList):
    bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_analytics_record("Count", "Command-PUSH", instancename)

    if len(SMSList) > 1:
        if SMSList[1].upper() == "OFF":
            logger.info("User requested that push notifications are disabled")
            message = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().turn_push_notifications_off(SMSFrom)
            bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, message)
            return
        elif SMSList[1].upper() == "ON":
            logger.info("User requested that push notifications are enabled")
            message = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().turn_push_notifications_on(SMSFrom)
            bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, message)
            return
        else:
            pushover_token = SMSList[1]
            logger.debug("Using Pushover token " + pushover_token)
            logger.info("Setting Pushover token for user")
            message = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_pushover_token_for_user(SMSFrom, pushover_token)
            bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, message)
    else:
        return


def send_push_notification_if_appropriate(service_number, mobile, title, message):
    pushover_token = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().get_pushover_user_token_from_mobile(mobile)

    if pushover_token != "":
        send_push_notification(pushover_token, message, title, service_number)


def whois(SMSTo, SMSFrom, SMSList):
    bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_analytics_record("Count", "Command-WHOIS", instancename)

    if len(SMSList) > 1:
        upper_case_reg = SMSList[1].upper()
        logger.debug("Using Registration Plate: " + upper_case_reg)
        response = cardetails(upper_case_reg)

    else:
        response = respond_noregistrationspecified(SMSTo, SMSFrom)

    bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, response)

# Respond to the user with an SMS containing hints on commands to use with BlockBuster
def syntaxhelp(SMSTo, SMSFrom):
    bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_analytics_record("Count", "Command-HELP", instancename)

    logger.info("Returning Help Info")
    message = "'REGISTER G857TYL John Smith' to register.\n\n" \
              "'WHOIS G857TYL' for car info (Default when only reg specified).\n \n" \
              "'BLOCK (B) GF58YTL' to block someone in. \n \n" \
              "'UNBLOCK (U) GF58YTL' to unblock someone. \n \n" \
              "'MOVE (M) G857TYL' to request that someone moves their car. \n \n" \
              "'OK' to acknowledge a move request.\n \n" \
              "'.' to get your current status.\n \n" \
              "'UNREGISTER (UR) G857TYL' to unregister from BlockBuster for specified car."
    bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, message)
    return "<Response></Response>"


def register(SMSTo, SMSFrom, SMSList, location):
    bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_analytics_record("Count", "Command-REGISTER", instancename)

    if len(SMSList) < 4:
        return notEnoughRegistrationDetails(SMSTo, SMSFrom)

    registration = SMSList[1].upper()
    firstname = SMSList[2]
    surname = SMSList[3]
    mobile = SMSFrom
    location = location

    message = bb_dbconnector_factory.DBConnectorInterfaceFactory()\
        .create()\
        .register_new_car(registration,
                          firstname,
                          surname,
                          mobile,
                          location)

    bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, message)
    return


def move(service_number, requester_number, SMSList):
    bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_analytics_record("Count", "Command-MOVE", instancename)

    def get_landline_number_string(reg):
        try:
            alt_contact_text = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().get_landline_from_reg(reg)
            if alt_contact_text != "":
                return (str(alt_contact_text) + "\n")
            else:
                return ""
        except Exception, e:
            bb_auditlogger.BBAuditLoggerFactory().create().logException(e)
            return ""

    # Method to send SMS messages to both blocker and blockee where the MOVE command is for a specific car
    def request_single_car_move(reg):

        # Search the database for the registration plate provided
        if checkifregexists(reg):

            # Try and retrieve details from the database for both the blockEE and blockER
            try:
                dict_blocker = bb_dbconnector_factory.DBConnectorInterfaceFactory().create()\
                    .get_user_dict_from_reg(blocking_reg)
                print(dict_blocker)

                dict_blockee = bb_dbconnector_factory.DBConnectorInterfaceFactory().create()\
                    .get_user_dict_from_mobile(requester_number)
                print(dict_blockee)

            except Exception, e:
                bb_auditlogger.BBAuditLoggerFactory().create().logException(e)
                pass

            # If the blocker has a Mobile number (and therefore is registered with BlockBuster) then do this
            if dict_blocker['Mobile'] != "" and dict_blocker['Mobile'] != None:

                # If the blockee is registered with BlockBuster then do this
                if dict_blockee:
                    message = dict_blockee['FirstName'] + " " + dict_blockee['Surname'] + \
                        " needs you to move your car, please.\n\n" \
                        "Text 'OK' to confirm that you have received this."

                    subject = "Please move your car"

                    bb_sms_handler.send_sms_notification(service_number, dict_blocker['Mobile'], message)

                    # Send a push notification if that user wants them
                    send_push_notification_if_appropriate(service_number, dict_blocker['Mobile'], subject, message)

                    # Ask the notification handler to send out the appropriate notifications
                    bb_notification_handler.send_notifications(dict_blocker['Mobile'], subject, message)

                    # Open a move request for that blocker / blockee combination
                    add_move_request(dict_blocker['Mobile'], requester_number)

                    landline_string = get_landline_number_string(blocking_reg)
                    logger.debug(landline_string)

                    blocker_name = dict_blocker['FirstName'] + " " + dict_blocker['Surname']
                    blocker_mobile = dict_blocker['Mobile']
                    blocker_reg = reg

                    list_of_names = blocker_name + " (" + \
                                    blocker_reg + ")\n" + \
                                    include_mobile_number(blocker_mobile) + \
                                    get_landline_number_string(blocker_reg) + "\n"

                    send_move_blockee_message(service_number,requester_number, list_of_names)

                # The blockee is not registered with BlockBuster
                # so advise them to register with the service before trying to use it
                else:
                    bb_sms_handler.send_sms_notification(service_number, requester_number, "Sorry - please register this mobile number to use "
                                          "this BlockBuster service. \n \n Text '?' for help.")

            # The blockER is not registered with BlockBuster
            # so provide them the name of the car owner
            else:
                bb_sms_handler.send_sms_notification(service_number, requester_number, "Sorry - this car belongs to " + dict_blocker['FirstName'] + " "
                                                 + dict_blocker['Surname'] + " but they do not have a mobile "
                                                                             "number registered.")

        else:
            # If the MOVE command was sent on its own (therefore searching for existing blocks)
            if len(SMSList) < 2:
                bb_sms_handler.send_sms_notification(service_number, requester_number, "Sorry - cannot find any current blocks for you.")

            # In which case it must have been sent with a registration plate as a parameter
            else:
                bb_sms_handler.send_sms_notification(service_number, requester_number, "Sorry - vehicle not registered with BlockBuster.")

        return "<Response></Response>"

    # Method to send MOVE response to blockee where there is a list of blockers who have been informed.
    def send_move_blockee_message(service_number2, requester_number2, names_list):
        messageblocker = "I've asked these people to move: \n\n" + names_list
        bb_sms_handler.send_sms_notification(service_number2, requester_number2, messageblocker)


    def include_mobile_number(mobile):
        share_mobile = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().mobile_sharing_enabled(mobile)
        if share_mobile:
            return (mobile + "\n")
        elif not share_mobile:
            return ""


    def add_move_request(blocker_mobile, blockee_mobile):
        move_request = {
            "BlockerMobile": blocker_mobile,
            "BlockeeMobile": blockee_mobile
        }
        bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_move_request(move_request)

    # IF check to see whether the MOVE command was sent on its own or with a registration plate. If so, do the below.
    sentWithoutRegistration = (len(SMSList) < 2)
    if sentWithoutRegistration:

        # Get a count of the active blocks for the person requesting the 'MOVE'
        count_of_blocks = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().get_count_of_blocks_for_blockee(requester_number)
        logger.debug('Count of blocks: ' + str(count_of_blocks))

        # Where the number of blocks is less than 1 (i.e. 0 as it shouldn't ever be a negative number) send a message
        # informing the blockee that there are no active blocks registered for them.
        if count_of_blocks < 1:
            bb_sms_handler.send_sms_notification(service_number, requester_number, "Sorry - cannot find any current blocks for you. \n\n"
                                                       "Use 'MOVE registration' for a specific car.")
            return "<Response></Response>"

        # Get a list of active blocks for the person requesting the 'MOVE' as a cursor
        list_of_blocks = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().get_list_of_blocks_for_blockee(requester_number)

        # Declare this outside the for loop so that it can be accessed once the for loop is complete
        list_of_names = ""

        # Iterate through the cursor, sending an SMS to each blocker asking them to move.
        for block_item in list_of_blocks:
                a = service_number
                b = requester_number
                blocker_mobile = block_item['blocker_mobile']
                d = block_item['blocked_reg']
                blockee_name = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().get_name_from_mobile(b)
                blocker_name = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().get_name_from_mobile(blocker_mobile)
                blocker_reg = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().get_reg_from_mobile(blocker_mobile)

                # Compile the message to send to the blocker.
                message = blockee_name + " (" + d + ") needs you to move your car, please.\n\n" \
                                                    "Text 'OK' to confirm that you have received this."

                # Send the SMS to the blocker.
                bb_sms_handler.send_sms_notification(a, blocker_mobile, message)

                # Send a push notification if the user wants it
                subject = "Move Request"
                send_push_notification_if_appropriate(service_number, blocker_mobile, subject, message)

                # Ask the notification handler to send out the appropriate notifications
                bb_notification_handler.send_notifications(blocker_mobile, subject, message)

                # Open a move request for that blocker
                add_move_request(blocker_mobile, b)

                # Add the name, reg, and mobile number of the blocker to the list
                # so that they can be provided back to the blockee.
                list_of_names = list_of_names + \
                                blocker_name + " (" + \
                                blocker_reg + ")\n" + \
                                include_mobile_number(blocker_mobile) + \
                                get_landline_number_string(blocker_reg) + "\n"

        # Now send a single message to the blockee containing a list of all people who were being blocked.
        send_move_blockee_message(service_number, requester_number, list_of_names)
        return "<Response></Response>"

    # A value was provided after the MOVE command therefore treat it as if a registration plate was provided.
    else:
        blocking_reg = SMSList[1].upper()
        return request_single_car_move(blocking_reg)


def acknowledge_move_request(SMSTo, SMSFrom, SMSList):
    bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_analytics_record("Count", "Command-ACKNOWLEDGE", instancename)
    open_move_requests = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().get_open_move_requests(SMSFrom)
    blocker_name = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().get_name_from_mobile(SMSFrom)

    if len(open_move_requests) < 1:
        bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, "BlockBuster doesn't know of anyone waiting for you to move at this time.")
        return

    for move_request in open_move_requests:
        message = blocker_name + " has acknowledged your move request."
        bb_sms_handler.send_sms_notification(SMSTo, move_request['blockee_mobile'], message)
        bb_dbconnector_factory.DBConnectorInterfaceFactory().create().remove_move_request(SMSFrom, move_request['blockee_mobile'])

    return


def block(SMSTo, SMSFrom, SMSList):
    bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_analytics_record("Count", "Command-BLOCK", instancename)

    # Loop through the registrations provided and add them all to an array
    reg_list = []
    total_elements = len(SMSList)
    # Start at element[1} as we have already established that element[0] contains the command by the face we're here.
    e = 1
    while e < total_elements:
        # Skip elements which have come from multiple spaces between registrations in the message.
        if SMSList[e] == "":
            pass
        else:
            reg_list.append(SMSList[e])
        e += 1

    logger.debug("Number of registrations in list is " + str(len(reg_list)))

    # Check that a registration was actually provided. If not, respond to the user.
    if len(reg_list) < 1:
        return respond_noregistrationspecified(SMSTo, SMSFrom)

    # Now work through each of the registrations in the list, working out what the status is, and triggering a
    # notification message if appropriate. Also build up a list of the statuses so that they can be fed back to
    # the user.
    list_of_blockees = ""

    for registration in reg_list:

        logger.debug("Currently processing " + registration)
        blocked_reg = registration.upper()

        # TODO: Refactor the registered check out of this as this is now done at first receipt of the web request
        try:
            dict_blocker = bb_dbconnector_factory.DBConnectorInterfaceFactory().create()\
                    .get_user_dict_from_mobile(SMSFrom)
            logger.debug("Surname of Blocker is " + dict_blocker['Surname'])

        except Exception, e:
            bb_auditlogger.BBAuditLoggerFactory().create().logException(e)
            message = "Sorry - please register this mobile number to use this BlockBuster service. \n \n " \
                "Reply '?' for help."

            # Send message to the blocker to advise them to register in order to use the service.
            bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, message)
            return "<Response></Response>"

        # Search the database for the registration number provided
        if checkifregexists(registration.upper()):
            try:
                dict_blockee = bb_dbconnector_factory.DBConnectorInterfaceFactory().create()\
                    .get_user_dict_from_reg(registration.upper())

                logger.debug("Surname of blockee is " + dict_blockee['Surname'])

            except Exception, e:
                bb_auditlogger.BBAuditLoggerFactory().create().logException(e)
                pass

            # If the blockee does not have a mobile number registered, tell the blocker that they can't be notified,
            # and then continue with the next iteration of the loop.
            if dict_blockee['Mobile'] == '' or dict_blockee['Mobile'] is None:

                list_of_blockees = list_of_blockees + registration.upper() + ": " + "Not Registered (" + dict_blockee['FirstName'] + " " \
                    + dict_blockee['Surname'] + ")\n\n"
                continue

            # Create the message to be sent to the person being blocked in.
            messageblockee = dict_blocker['FirstName'] + " " + dict_blocker['Surname'] + " has blocked in your car " \
                + blocked_reg + ". \n\nText MOVE to ask them to move their car."

            # Send the message to the blockee.
            bb_sms_handler.send_sms_notification(SMSTo, dict_blockee['Mobile'], messageblockee)

            #Send a push notification if the user wants it
            subject = "You've been blocked in"
            send_push_notification_if_appropriate(SMSTo, dict_blockee['Mobile'], subject, messageblockee)

            # Ask the notification handler to send out the appropriate notifications
            bb_notification_handler.send_notifications(dict_blockee['Mobile'], subject, messageblockee)

            # Construct the list of blockees
            list_of_blockees = list_of_blockees + registration.upper() + ": " + "Notified (" + dict_blockee['FirstName'] + " " \
                + dict_blockee['Surname'] + ")\n\n"

            # Construct a block record
            block_parameters = {
                "BlockedReg": blocked_reg,
                "BlockeeMobile": dict_blockee['Mobile'],
                "BlockerMobile": SMSFrom
            }

            # Add the block record to the DB
            bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_block_record(block_parameters)


        else:
            list_of_blockees = list_of_blockees + \
                               registration.upper() + ": Not Found" + "\n\n"

    # Create the message to be sent to the blocker.
    messageblocker = list_of_blockees + "'U REG' to unblock specific car, 'U' for all."

    # Send the message to the blocker.
    bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, messageblocker)

    return "<Response></Response>"


def unblock(SMSTo, SMSFrom, SMSList):
    bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_analytics_record("Count", "Command-UNBLOCK", instancename)

    def send_unblock_blockee_messages(service_number, unblocker_number, blockee_number, blocked_reg, blocker_name, blockee_name):
        messageblockee = blocker_name + " is no longer blocking your car (" + blocked_reg + ") in."

        bb_sms_handler.send_sms_notification(service_number, blockee_number, messageblockee)

        #Send a push notification if the user wants it
        subject = "You've been unblocked"
        send_push_notification_if_appropriate(service_number, blockee_number, subject, messageblockee)

        # Ask the notification handler to send out the appropriate notifications
        bb_notification_handler.send_notifications(blockee_number, subject, messageblockee)


    def send_unblock_blocker_message(service_number, unblocker_number, list_of_names):
        messageblocker = "I've told these people that you've moved: \n\n" + list_of_names
        bb_sms_handler.send_sms_notification(service_number, unblocker_number, messageblocker)

     # Check whether the UNBLOCK command was sent on its own....
    if len(SMSList) < 2:
        logger.debug('Command: UNBLOCK (no reg)')

        list_of_blocks = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().get_list_of_blocks_for_blocker(SMSFrom)

        # Check the length of the cursor to see how many active blocks there are
        # If there is at least one active block, process those blocks...
        if len(list_of_blocks) > 0:

            list_of_names = ""
            # Iterate through the cursor and process each active block.
            # Send a message to the blockee, and remove the block.
            for block_item in list_of_blocks:
                a = SMSTo
                b = SMSFrom
                c = block_item['blockee_mobile']
                d = block_item['blocked_reg']
                blocker_name = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().get_name_from_mobile(b)
                blockee_name = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().get_name_from_reg(d)
                send_unblock_blockee_messages(a, b, c, d, blocker_name, blockee_name)
                list_of_names = list_of_names + blockee_name + "\n"
                bb_dbconnector_factory.DBConnectorInterfaceFactory().create().remove_blocks(b, d)

            # Now send a message to the blocker containing a list of all people who were being blocked.
            send_unblock_blocker_message(SMSTo, SMSFrom, list_of_names)
            return "<Response></Response>"

        # If there are no active blocks, inform the unblocker that there are no active blocks found
        else:
            logger.info("No active blocks found.")
            bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, "You are not currently blocking anyone in.")
            return "<Response></Response>"

    # ... or if a registration plate was specified with the UNBLOCK command
    else:
        try:
            blocked_reg = SMSList[1].upper()
        except Exception, e:
            bb_auditlogger.BBAuditLoggerFactory().create().logException(e)
            logger.warn('No Registration Specified')
            respond_noregistrationspecified(SMSTo, SMSFrom)
            return "<Response></Response>"

        # Search the database for the registration number provided
        if checkifregexists(blocked_reg):
            try:
                dict_blockee = bb_dbconnector_factory.DBConnectorInterfaceFactory().create()\
                    .get_user_dict_from_reg(blocked_reg)
                logger.debug(dict_blockee['Surname'])

            except Exception, e:
                bb_auditlogger.BBAuditLoggerFactory().create().logException(e)
                logger.error("Error retrieving user dictionary from reg \n" + str(e))
                pass

            if dict_blockee['Mobile'] == "" or dict_blockee['Mobile'] is None:
                message = "Sorry - that car belongs to " + dict_blockee['FirstName'] + " " \
                          + dict_blockee['Surname'] + " but they do not have a mobile number registered."
                bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, message)
                return "<Response></Response>"

            try:
                dict_blocker = bb_dbconnector_factory.DBConnectorInterfaceFactory().create()\
                    .get_user_dict_from_mobile(SMSFrom)

                logger.debug(dict_blocker['Surname'])

            except Exception, e:
                bb_auditlogger.BBAuditLoggerFactory().create().logException(e)
                message = "Sorry - please register this mobile number to use this BlockBuster service. \n \n " \
                          "Reply '?' for help."

                bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, message)

                return "<Response></Response>"

            messageblockee = dict_blocker['FirstName'] + " " + dict_blocker['Surname'] + " is no longer blocking you in."
            messageblocker = "I've told " + dict_blockee['FirstName'] + " " + dict_blockee['Surname'] + \
                             " that you've moved."

            bb_sms_handler.send_sms_notification(SMSTo, dict_blockee['Mobile'], messageblockee)

            #Send a push notification if the user wants it
            subject = "You've been unblocked"
            send_push_notification_if_appropriate(SMSTo, dict_blockee['Mobile'], subject, messageblockee)

            # Ask the notification handler to send out the appropriate notifications
            bb_notification_handler.send_notifications(dict_blockee['Mobile'], subject, messageblockee)

            bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, messageblocker)

            # Remove the block records from the database for a specified blocker_number and blocked_reg combination.
            bb_dbconnector_factory.DBConnectorInterfaceFactory().create().remove_blocks(SMSFrom, blocked_reg)

            return "<Response></Response>"

        else:
            bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, "Sorry - that car isn't registered with BlockBuster.")
            return "<Response></Response>"