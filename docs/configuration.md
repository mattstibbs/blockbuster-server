# Configuring Blockbuster

## Configuration Files
There are three files used for storing configuration.

In the blockbuster package:

* config.py
* config_services.py

In the blockbuster_celery package:

* config_celery.py

---
## Config.py

### General Settings
	timerestriction = False/True
If set to True, this will prevent any interactions with the service via SMS between 20:00 and 08:00. This is to prevent delayed SMS in the networks from ending up at peoples' phones in the middle of the night.

	debug_mode = False/True
When True the app runs in debug mode meaning a full debug log output is created. There isn't much of reason not to just leave this on True.

### Email Type
	emailtype = "Gmail" or "Console"

### SMS Type
	outboundsmstype = "WebService"
	outboundsmstype = "Console"

### Twilio Auth Keys
	account_sid = "key"
	auth_token = "key"

### Twilio Auth Keys (Trial Account)
	account_sid = "twilio account sid"
	auth_token = "twilio auth token"

### Twilio Auth Keys (Testing Credentials)
	account_sid = "key"
	auth_token = "key"

### Web Services SMS Auth
	spsms_basic_auth = 'Basic key'
	spsms_host = 'url_host'
	spsms_url = '/Path/to/SMSSubmissions.ashx'

### Postgres Connection Details
	pg_host = 'localhost'
	pg_dbname = 'blockbuster'
	pg_user = 'blockbuster'
	pg_passwd = 'blockbuster'

### Pushover Keys
	pushover_app_token = "pushover originator token"

### Email Configuration
    smtp_server = 'smtp.gmail.com:587'
    mail_host = 'smtp.gmail.com'
    mail_port = '587'
    mail_username = 'email@gmail.com'
    mail_fromaddr = mail_username
    mail_password = 'password'
    mail_monitoring_addr = 'email to be used for exception reports'

### REST API Configuration
    api_username = "api username"
    api_passphrase = "api password"

### New Number
    return_number = "+440000111222"
    
---
## config_services.py
Config_services.py is used to configure access numbers served by the application. 

It is in the format of a Python if statement:

```
def identify_service(SMSTo):
    if SMSTo == "+441234000999":
        instancename = "BB Test"
        location = "Test"
    elif SMSTo == "+441234111222":
        instancename = "BB Secondary"
        location = "Secondary"
    elif SMSTo == "+447777888999":
        instancename = "Global Blockbuster"
        location = "Global"
    elif SMSTo == "API":
        instancename = "BB API"
        location = "API"
    else:
        instancename = "BB Unknown"
        location = "Unknown"
    return instancename, location
```
