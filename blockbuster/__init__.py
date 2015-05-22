__author__ = 'Matt Stibbs'
__version__ = '1.26.00'
target_schema_version = '1.25.00'

from flask import Flask
app = Flask(__name__)


def startup():
    import blockbuster.bb_dbconnector_factory
    import blockbuster.bb_logging as log
    import blockbuster.bb_auditlogger as audit

    try:
        if blockbuster.bb_dbconnector_factory.DBConnectorInterfaceFactory().create().db_version_check():
            import blockbuster.bb_routes
            print("Running...")

        else:
            raise RuntimeError("Incorrect database schema version.")

    except RuntimeError, e:
        log.logger.exception("Incorrect database schema version.")
        audit.BBAuditLoggerFactory().create().logException('app', 'STARTUP', 'Incorrect database schema version.')

startup()