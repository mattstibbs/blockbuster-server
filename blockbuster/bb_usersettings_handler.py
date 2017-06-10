# Local imports
import logging
import bb_auditlogger
import config_services
import bb_dbconnector_factory
from messaging import bb_sms_handler
import bb_notification_handler as notify

# Set up the logger
logger = logging.getLogger(__name__)


# Method is run when a SET command to determine which particular setting the user is updating.
def setting(sms_to, sms_from, sms_list):

    # Add analytics record
    instance_name, a = config_services.identify_service(sms_to)
    bb_dbconnector_factory.DBConnectorInterfaceFactory().create().add_analytics_record("Count", "Command-SETTING", instance_name)

    # Make sure that there are enough values in the message to actually change a setting
    # You need three - 1. SET, 2. SETTING (e.g. EMAIL), 3. VALUE (e.g. ON)
    if len(sms_list) >= 3:

        # Firstly check to see which setting the user wishes to update
        if sms_list[1].upper() == "EMAIL":
            logger.debug("User changing email settings")
            email_settings(sms_to, sms_from, sms_list)
        elif sms_list[1].upper() == "CONTACT":
            logger.debug("User changing contact settings")
            contact_settings(sms_to, sms_from, sms_list)
        else:
            return

        return

    else:
        bb_sms_handler.send_sms_notification(sms_to, sms_from,
                                             "Please ensure you provide all the necessary parameters to change settings. ")
        return


# Method to process a setting request for EMAIL
def email_settings(sms_to, sms_from, sms_list):
    if sms_list[2].upper() == "OFF":
        logger.debug("User requested that email notifications are disabled")
        result = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().disable_email_notifications(sms_from)
        bb_sms_handler.send_sms_notification(sms_to, sms_from, result)
        return

    elif sms_list[2].upper() == "ON":
        logger.debug("User requested that email notifications are enabled")
        result = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().enable_email_notifications(sms_from)
        bb_sms_handler.send_sms_notification(sms_to, sms_from, result)
        notify.send_notifications(sms_from, "Test Notification", "Email notifications have now been turned on. "
                                                                 "You should add blockbuster.notify@gmail.com "
                                                                 "to your contacts.")
        return

    else:
        email_address = sms_list[2]
        logger.debug("Updating with email address " + email_address)
        result = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().update_email_address(sms_from, email_address)
        bb_sms_handler.send_sms_notification(sms_to, sms_from, result)
        notify.send_notifications(sms_from, "Test Notification", "Notifications are now enabled for this email address.")
        return


# Method to process setting changes for CONTACT
def contact_settings(bb_service_number, user_mobile, sms_list):

    # If the user sends a command of "SET CONTACT MOBILE OFF", mobile number sharing for them will be disabled.
    global result
    if len(sms_list) > 3 and sms_list[2].upper() == "MOBILE" and sms_list[3].upper() == "OFF":
        # Log that the user has chosen to disable sharing of their mobile number
        logger.debug("Updating user setting Share_Mobile to OFF")

        # Attempt to disable mobile number sharing for this user - will return a success code of 0 (success) or 1 (fail)
        success_code = bb_dbconnector_factory.DBConnectorInterfaceFactory()\
            .create().disable_mobile_number_sharing(user_mobile)

        if success_code == 0:
            result = "Share Mobile Number is now OFF."
            logger.info("User Setting Updated: Share Mobile OFF")

        else:
            result = "There was an issue enabling this setting - please contact BlockBuster support."
            logger.error("Error disabling Share Mobile setting for user.")

        bb_sms_handler.send_sms_notification(bb_service_number, user_mobile, result)

        return

    # If the user sends any other command beginning with "SET CONTACT MOBILE"
    # then mobile number sharing will be enabled for them.
    elif sms_list[2].upper() == "MOBILE":
        # Log that the user has chosen to enable sharing of their mobile number
        logger.debug("Updating user setting Share_Mobile to ON")

        # Attempt to enable mobile number sharing for this user - will return a success code of 0 (success) or 1 (fail)
        success_code = bb_dbconnector_factory.DBConnectorInterfaceFactory()\
            .create().enable_mobile_number_sharing(user_mobile)

        if success_code == 0:
            result = "Share Mobile Number is now ON."
            logger.info("User Setting Updated: Share Mobile ON")

        else:
            result = "There was an issue enabling this setting - please contact BlockBuster support."
            logger.error("Error enabling Share Mobile setting for user.")

        bb_sms_handler.send_sms_notification(bb_service_number, user_mobile, result)

        return

    # If the user sends a "SET CONTACT CLEAR" command
    # erase any alternative contact text that they have set and enable mobile sharing
    elif sms_list[2].upper() == "CLEAR":
        # Log that the user has chosen to enable sharing of their mobile number
        logger.debug("Clearing alternative contact text and enabling mobile sharing")
        bb_auditlogger.BBAuditLoggerFactory().create().logAudit('app',
                                                                'SETTING-CONTACT-CLEAR',
                                                                "Mobile:" + user_mobile)

        # Attempt to enable mobile number sharing for this user - will return a success code of 0 (success) or 1 (fail)
        success_clear = bb_dbconnector_factory.DBConnectorInterfaceFactory()\
            .create().remove_alternative_contact_text(user_mobile)
        success_code = bb_dbconnector_factory.DBConnectorInterfaceFactory()\
            .create().enable_mobile_number_sharing(user_mobile)

        if success_code == 0 and success_clear == 0:
            result = "Your additional contact information has been cleared and mobile number sharing is enabled."
            logger.info("User Setting Updated: Share Mobile ON and Alternative Contact Info CLEARED.")

        else:
            result = "There was an issue clearing your contact information - please report this issue."
            # TODO: Create a new logError method on the BBAuditLogger and then convert the below
            # BBAuditLogger.BBAuditLoggerFactory().create().logException('app',
            #                                                            'SETTING-CONTACT-CLEAR',
            #                                                            "Mobile:" + user_mobile)

        bb_sms_handler.send_sms_notification(bb_service_number, user_mobile, result)

        return

    else:
        # Assign the alternative text provided by the user to a variable
        alt_text_last_index = (len(sms_list))
        alternative_text = sms_list[2]
        i = 3
        while i < alt_text_last_index:
            alternative_text = alternative_text + " " + sms_list[i]
            i += 1

        # Log that the user has chosen to update their alternative contact information
        logger.info("Updating user setting with alternative contact information.")
        logger.debug("New contact information: " + alternative_text)

        # Call the method in the DAL to update the alternative contact information for that user.
        # Assign the result to a variable.
        success_code = bb_dbconnector_factory.DBConnectorInterfaceFactory()\
            .create()\
            .update_alternative_contact_text(user_mobile, alternative_text)

        if success_code == 0:
            result = "Alternative contact info has been set to:\n\n \"" + alternative_text + "\""

        else:
            result = "There was an issue setting the alternative contact info - please contact BlockBuster support."

        # Send an SMS to the user confirming that their details have been updated.
        bb_sms_handler.send_sms_notification(bb_service_number, user_mobile, result)

        return
