# Local Imports
import bb_dbconnector_factory
import logging
from messaging import bb_mail_handler as mail

log = logging.getLogger(__name__)


def notification_list(recipient):
    # Get a dictionary of notification preferences for this user
    preferences = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().get_notification_preferences_for_user(recipient)

    # Set up an empty notify_list which will be used to stack up the preferred notifications for this user
    notify_list = []

    # Iterate through the items in the notifications preferences dictionary,
    # and add required notifications to the notify_list
    if preferences is not None:
        for k, v in preferences.items():
            if v == 1:
                notify_list.append(k)

    return notify_list


def email_notification(recipient, subject, message):
    toaddr = bb_dbconnector_factory.DBConnectorInterfaceFactory().create().get_email_address(recipient)
    subject = subject
    body = message
    #  mail.send_mail(toaddr, subject, body)        # Use this line if you want to send emails synchronously
    mail.send_mail_notification(toaddr, subject, body)     # Use this line if you have a celery-based worker for sending email


# Method can be called to trigger notifications to a recipient. The entity calling this method should not have to worry
# about what type of notifications are going to be sent - just that notifications need to be sent.
def send_notifications(recipient, subject, body):

    list = notification_list(recipient)

    for notification in list:
        log.debug("Checking notification type")

        if notification == "Email":
            log.debug("Email notification required")
            email_notification(recipient, subject, body)
        else:
            log.debug("Not a currently supported notification type")
            continue
