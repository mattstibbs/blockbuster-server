__author__ = 'Matt Stibbs'
__version__ = '1.27.00'
target_schema_version = '1.25.00'

from flask import Flask
app = Flask(__name__)


def startup():
    import blockbuster.bb_dbconnector_factory
    import blockbuster.bb_logging as log
    import blockbuster.bb_auditlogger as audit

    blockbuster.app.debug = blockbuster.config.debug_mode

    blockbuster.bb_logging.logger.info(str.format("Application Startup - BlockBuster v{0} Schema v{1}",
                                                  blockbuster.__version__, target_schema_version))
    time_setting = "Application Setting - Time Restriction Disabled" if not blockbuster.config.timerestriction else "Application Setting - Time Restriction Enabled"
    print(time_setting)

    if blockbuster.config.debug_mode:
        print("========= APPLICATION IS RUNNING IN DEBUG MODE ==========")

    try:
        if blockbuster.bb_dbconnector_factory.DBConnectorInterfaceFactory().create().db_version_check():
            import blockbuster.bb_routes
            print("Running...")

        else:
            raise RuntimeError("Incorrect database schema version. Wanted ")

    except RuntimeError, e:
        log.logger.exception(e)
        audit.BBAuditLoggerFactory().create().logException('app', 'STARTUP', str(e))

startup()
