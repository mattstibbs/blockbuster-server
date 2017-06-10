import blockbuster.config as config
import blockbuster.bb_dbconnector_factory as BbDbInterface
import blockbuster.config_services as config_services
import logging
import blockbuster.bb_auditlogger as BBAuditLogger

log = logging.getLogger(__name__)

import httplib
import urllib
from twilio.rest import TwilioRestClient
from twilio.rest.resources import Connection
from twilio.rest.resources.connection import PROXY_TYPE_HTTP
import time


class SMSSenderFactory:
    def __init__(self):
        pass
    
    def __del__(self):
        pass
    
    @staticmethod
    def create():
        if config.outboundsmstype == "WebService":
            return WebServiceSMSSender()
        elif config.outboundsmstype == "Console":
            return ConsoleSMSSender()
        elif config.outboundsmstype == "Twilio":
            return TwilioSMSSender()
        else:
            return WebServiceSMSSender()


class SMSSender:
    def __init__(self):
        raise NotImplementedError()
    
    def __del__(self):
        raise NotImplementedError()
    
    def send_sms(self):
        raise NotImplementedError()


class ConsoleSMSSender(SMSSender):
    def __init__(self):
        pass
    
    def __del__(self):
        pass
    
    def send_sms(self, originator, recipient, body):
        instancename, location = config_services.identify_service(originator)
        BbDbInterface.DBConnectorInterfaceFactory().create().add_analytics_record("Count", "SMS-Send", instancename)
        
        originator = config.return_number
        
        logentry = {
            "Direction": "----> O",
            "SMSService": "Emulator",
            "Command": "",
            "Originator": originator,
            "OriginatorName": instancename,
            "Destination": recipient,
            "RecipientName": BbDbInterface.DBConnectorInterfaceFactory().create().get_name_from_mobile(recipient),
            "Details": body
        }
        
        time.sleep(2)
        BbDbInterface.DBConnectorInterfaceFactory().create().add_transaction_record(logentry)
        
        # Create a description to be stored in the log table
        audit_description = "Originator:" + originator + ";Recipient:" + recipient + ";Body:" + body
        
        # Add the log table entry
        BBAuditLogger.BBAuditLoggerFactory().create().logAudit('bgwrk', 'SEND-SMS-CONSOLE', audit_description)
        
        message = ("*\n"
                   "******************************\n"
                   "Originator: " + originator + "\n"
                                                 "Recipient: " + recipient + "\n\n" +
                   body + "\n"
                          "==============================")
        
        print(message)


class WebServiceSMSSender(SMSSender):
    def __init__(self):
        log.debug("Instantiating WebServiceSMSSender instance.")
    
    def __del__(self):
        log.debug("Destroying a WebServiceSMSSender instance.")
    
    def send_sms(self, originator, recipient, body):
        smsservice = "WebService"
        
        instancename, location = config_services.identify_service(originator)
        BbDbInterface.DBConnectorInterfaceFactory().create().add_analytics_record("Count", "SMS-Send", instancename)
        
        host = config.spsms_host
        url = config.spsms_url
        
        originator = config.return_number
        
        values = {
            'Originator': originator,
            'Recipient': recipient,
            'Body': body,
        }
        
        headers = {
            'User-Agent': 'python',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': config.spsms_basic_auth
        }
        
        values = urllib.urlencode(values)
        
        conn = httplib.HTTPSConnection(host)
        conn.request("POST", url, values, headers)
        response = conn.getresponse()
        
        instancename, location = config_services.identify_service(originator)
        
        msgrequest = {'url': url, 'headers': headers, 'values': values}
        msgresponse = {'status': response.status, 'reason': response.reason, 'headers': response.getheaders()}
        message = {'Request': msgrequest, 'Response': msgresponse}
        
        logentry = {
            "Direction": "----> O",
            "SMSService": smsservice,
            "Command": "",
            "Originator": originator,
            "OriginatorName": instancename,
            "Destination": recipient,
            "RecipientName": BbDbInterface.DBConnectorInterfaceFactory().create().get_name_from_mobile(recipient),
            "Details": body,
            "Message": message
        }
        
        BbDbInterface.DBConnectorInterfaceFactory().create().add_transaction_record(logentry)
        
        # Create a description to be stored in the log table
        audit_description = "Originator:" + originator + ";Recipient:" + recipient + ";Body:" + body
        
        # Add the log table entry
        BBAuditLogger.BBAuditLoggerFactory().create().logAudit('bgwrk', 'SEND-SMS-WEBSERVICES', audit_description)
        
        log.debug('SPSMS Response: ' + str(response.status) + ' ' + str(response.reason))
        
        log.info("SMS sent via WebServices. Recipient: " + recipient)


class TwilioSMSSender(SMSSender):
    def __init__(self):
        self.client = TwilioRestClient(config.account_sid, config.auth_token)
        
        # This bit of code is here in case you need to use Twilio from behind a HTTP proxy.
        # You will need to change the if statement to True to enable it.
        if False:
            Connection.set_proxy_info(
                config.proxy_host,
                config.proxy_port,
                proxy_type=PROXY_TYPE_HTTP,
                proxy_user=config.proxy_user,
                proxy_pass=config.proxy_pass,
            )
    
    def __del__(self):
        pass
    
    def send_sms(self, originator, recipient, body):
        instancename, location = config_services.identify_service(originator)
        BbDbInterface.DBConnectorInterfaceFactory().create().add_analytics_record("Count", "SMS-Send", instancename)
        
        logentry = {
            "Direction": "----> O",
            "SMSService": "Twilio",
            "Command": "",
            "Originator": originator,
            "OriginatorName": instancename,
            "Destination": recipient,
            "RecipientName": BbDbInterface.DBConnectorInterfaceFactory().create().get_name_from_mobile(recipient),
            "Details": body
        }
        
        BbDbInterface.DBConnectorInterfaceFactory().create().add_transaction_record(logentry)
        
        # Create a description to be stored in the log table
        audit_description = "Originator:" + originator + ";Recipient:" + recipient + ";Body:" + body
        
        # Add the log table entry
        BBAuditLogger.BBAuditLoggerFactory().create().logAudit('bgwrk', 'SEND-SMS-TWILIO', audit_description)
        
        message = self.client.messages.create(
            body=body,
            to=recipient,  # Replace with your phone number
            from_=originator)  # Replace with your Twilio number
        
        print(message.sid)
