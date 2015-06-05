__author__ = 'Matt Stibbs'
__version__ = '1.26.04'
target_schema_version = '1.25.00'

from flask import Flask
app = Flask(__name__)


def startup():
    import datetime
    import blockbuster.bb_dbconnector_factory
    import blockbuster.bb_logging as log
    import blockbuster.bb_auditlogger as audit

    blockbuster.app.debug = blockbuster.config.debug_mode

    blockbuster.bb_logging.logger.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    blockbuster.bb_logging.logger.debug("@@@@@@@@@@@@@@@@@@ BlockBuster " + blockbuster.__version__ + " "
                                                                                                            "@@@@@@@@@@@@@@@@@@")
    blockbuster.bb_logging.logger.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    blockbuster.bb_logging.logger.info("Application Startup")
    blockbuster.bb_logging.logger.info(
        'Application Setting - Time Restriction Disabled') \
        if not blockbuster.config.timerestriction else blockbuster.bb_logging.logger.info(
        'Application Setting - Time Restriction Enabled')

    # blockbuster.bb_logging.logger.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

    if blockbuster.config.debug_mode:
        blockbuster.bb_logging.logger.info("========= APPLICATION IS RUNNING IN DEBUG MODE ==========")

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
