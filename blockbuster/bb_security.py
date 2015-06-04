from werkzeug.security import generate_password_hash, check_password_hash

from blockbuster import bb_auditlogger
from blockbuster import bb_dbconnector_factory

auditor = bb_auditlogger.BBAuditLoggerFactory().create()


def get_encrypted_password(password):
    encrypted_password = generate_password_hash(password, method='pbkdf2:sha1', salt_length=8)
    return encrypted_password


def credentials_are_valid(username, password):
    db = bb_dbconnector_factory.DBConnectorInterfaceFactory().create()
    credentials = db.get_api_credentials(username)

    # Check whether the provided username exists in the system (this is purely for logging purposes)
    username_exists = True if credentials else False
    auditor.logAudit('app',
                     'USER_CHECK',
                     str.format("Username '{0}' exists: {1}", username, username_exists))

    # Given that the user is valid, check the password
    password_valid = False
    if credentials:
        password_valid = check_password_hash(credentials['password'], password)
        auditor.logAudit('app',
                         'PWD_CHECK',
                         str.format("Password valid for user '{0}': {1}", username, password_valid))

    return password_valid
