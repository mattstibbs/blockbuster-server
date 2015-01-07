from messaging import bb_sms_handler

__author__ = 'matt'

########################################
# Local imports
import bb_dbconnector_factory
import config_services
import bb_notification_handler as notify
import logging
import bb_auditlogger

log = logging.getLogger('bb_log.' + __name__)
########################################


# Method is run when a SET command to determine which particular setting the user is updating.
def setting(SMSTo, SMSFrom, SMSList):

    # Add analytics record
    instancename, a = config_services.identify_service(SMSTo)
    bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_analytics_record("Count", "Command-SETTING", instancename)

    # Make sure that there are enough values in the message to actually change a setting
    # You need three - 1. SET, 2. SETTING (e.g. EMAIL), 3. VALUE (e.g. ON)
    if len(SMSList) >= 3:

        # Firstly check to see which setting the user wishes to update
        if SMSList[1].upper() == "EMAIL":
            log.info("User changing email settings")
            email_settings(SMSTo, SMSFrom, SMSList)
        elif SMSList[1].upper() == "CONTACT":
            log.info("User changing contact settings")
            contact_settings(SMSTo, SMSFrom, SMSList)
        else:
            return

        return

    else:
        bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, "Please ensure you provide all the necessary parameters to change settings. ")
        return


# Method to process a setting request for EMAIL
def email_settings(SMSTo, SMSFrom, SMSList):
    if SMSList[2].upper() == "OFF":
        log.info("User requested that email notifications are disabled")
        result = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().disable_email_notifications(SMSFrom)
        bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, result)
        return

    elif SMSList[2].upper() == "ON":
        log.info("User requested that email notifications are enabled")
        result = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().enable_email_notifications(SMSFrom)
        bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, result)
        notify.send_notifications(SMSFrom, "Test Notification", "Email notifications have now been turned on. " + \
                                           "You should add blockbuster.notify@gmail.com to your contacts.")
        return

    else:
        email_address = SMSList[2]
        log.info("Updating with email address " + email_address)
        result = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().update_email_address(SMSFrom, email_address)
        bb_sms_handler.send_sms_notification(SMSTo, SMSFrom, result)
        notify.send_notifications(SMSFrom, "Test Notification", "Notifications are now enabled for this email address.")
        return

# Method to process setting changes for CONTACT
def contact_settings(bbServiceNumber, userMobile, SMSList):

    # If the user sends a command of "SET CONTACT MOBILE OFF", mobile number sharing for them will be disabled.
    if (len(SMSList) > 3 and SMSList[2].upper() == "MOBILE" and SMSList[3].upper() == "OFF"):
        # Log that the user has chosen to disable sharing of their mobile number
        log.info("Updating user setting Share_Mobile to OFF")

        # Attempt to disable mobile number sharing for this user - will return a success code of 0 (success) or 1 (fail)
        successCode = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().disable_mobile_number_sharing(userMobile)

        if successCode == 0:
            result = "Share Mobile Number is now OFF."

        elif successCode == 1:
            result = "There was an issue enabling this setting - please contact BlockBuster support."

        bb_sms_handler.send_sms_notification(bbServiceNumber, userMobile, result)

        return

    # If the user sends any other command beginning with "SET CONTACT MOBILE"
    # then mobile number sharing will be enabled for them.
    elif (SMSList[2].upper() == "MOBILE"):
        # Log that the user has chosen to enable sharing of their mobile number
        log.info("Updating user setting Share_Mobile to ON")

        # Attempt to enable mobile number sharing for this user - will return a success code of 0 (success) or 1 (fail)
        successCode = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().enable_mobile_number_sharing(userMobile)

        if successCode == 0:
            result = "Share Mobile Number is now ON."

        elif successCode == 1:
            result = "There was an issue enabling this setting - please contact BlockBuster support."

        bb_sms_handler.send_sms_notification(bbServiceNumber, userMobile, result)

        return


    # If the user sends a "SET CONTACT CLEAR" command
    # erase any alternative contact text that they have set and enable mobile sharing
    elif (SMSList[2].upper() == "CLEAR"):
        # Log that the user has chosen to enable sharing of their mobile number
        log.info("Clearing alternative contact text and enabling mobile sharing")
        bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app',
                                                               'SETTING-CONTACT-CLEAR',
                                                               "Mobile:" + userMobile)

        # Attempt to enable mobile number sharing for this user - will return a success code of 0 (success) or 1 (fail)
        successClear = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().remove_alternative_contact_text(userMobile)
        successCode = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().enable_mobile_number_sharing(userMobile)

        if successCode == 0 and successClear == 0:
            result = "Your additional contact information has been cleared and mobile number sharing is enabled."

        elif successCode == 1 or successClear == 1:
            result = "There was an issue clearing your contact information - please report this issue."
            # TODO: Create a new logError method on the BBAuditLogger and then convert the below
            # BBAuditLogger.BBAuditLoggerFactory().create().logException('app',
            #                                                            'SETTING-CONTACT-CLEAR',
            #                                                            "Mobile:" + userMobile)

        bb_sms_handler.send_sms_notification(bbServiceNumber, userMobile, result)

        return


    else:
        # Assign the alternative text provided by the user to a variable
        alt_text_last_index = (len(SMSList))
        alternative_text = SMSList[2]
        i = 3
        while i < alt_text_last_index:
            alternative_text = alternative_text + " " + SMSList[i]
            i+=1

        # Log that the user has chosen to update their alternative contact information
        log.info("Updating user setting with alternative contact information.")
        log.debug("New contact information: " + alternative_text)

        # Call the method in the DAL to update the alternative contact information for that user.
        # Assign the result to a variable.
        successCode = bb_dbconnector_factory.DBConnectorInterfaceFactory()\
            .create()\
            .update_alternative_contact_text(userMobile, alternative_text)

        if successCode == 0:
            result = "Alternative contact info has been set to:\n\n \"" + alternative_text + "\""

        elif successCode == 1:
            result = "There was an issue setting the alternative contact info - please contact BlockBuster support."

        # Send an SMS to the user confirming that their details have been updated.
        bb_sms_handler.send_sms_notification(bbServiceNumber, userMobile, result)

        return