import os
from urllib.parse import urlparse

# General Settings
timerestriction = bool(os.environ.get('TIME_RESTRICTION', 'False'))
debug_mode = bool(os.environ.get('DEBUG_MODE', 'True'))
log_directory = './logs'

# Email Settings
# emailtype ['Sendgrid', 'Console', 'Gmail']
emailtype = os.environ.get('EMAIL_TYPE', 'Gmail')

# SMS Settings
# outboundsmstype = "WebService"
# outboundsmstype = "Twilio"
outboundsmstype = os.environ.get('OUTBOUND_SMS_TYPE', 'Console')

# Twilio Auth Keys
account_sid = os.environ.get('TWILIO_ACCOUNT_SID', 'twilio sid here')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN', 'auth token here')

# SMS Services Auth
spsms_basic_auth = 'basic auth header here'
spsms_host = 'host here'
spsms_url = 'url here'

# Postgres Connection Details
pg_connection_string = os.environ.get('DATABASE_URL', 'postgresql://blockbuster:blockbuster@localhost:5432/blockbuster')
s = urlparse(pg_connection_string)
pg_host = s.hostname
pg_dbname = str.replace(s.path, '/', '')
pg_user = s.username
pg_passwd = s.password

# Proxy Details
proxy_user = ''
proxy_pass = ''
proxy_host = ''
proxy_port = 8080

# Testing
test_to_number = ''
test_from_number = ''

# Pushover Keys
pushover_app_token = os.environ.get('PUSHOVER_APP_TOKEN', '')

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '')

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:32769/1')

# Email Configuration
mail_host = 'smtp.gmail.com'
mail_port = int(os.environ.get('SMTP_PORT', '587'))
mail_username = os.environ.get('SMTP_USERNAME', '')
mail_password = os.environ.get('SMTP_PASSWORD', '')
mail_fromaddr = mail_username
mail_monitoring_addr = os.environ.get('MAIL_MONITORING_ADDRESS', '')
smtp_server = f'{mail_host}:{mail_port}'

# New Number
return_number = os.environ.get('RETURN_NUMBER', '+440000111222')
