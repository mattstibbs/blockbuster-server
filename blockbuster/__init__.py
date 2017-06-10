__author__ = 'Matt Stibbs'
__version__ = '1.27.00'
target_schema_version = '1.25.00'

from flask import Flask
import logging
import blockbuster.bb_auditlogger as audit

logger = logging.getLogger(__name__)

app = Flask(__name__)


def startup():
    import blockbuster.bb_dbconnector_factory

    blockbuster.app.debug = blockbuster.config.debug_mode

    print(str.format("Application Startup - BlockBuster v{0} Schema v{1}",
                     blockbuster.__version__, target_schema_version))

    time_setting = "Application Setting - Time Restriction Disabled" \
        if not blockbuster.config.timerestriction \
        else "Application Setting - Time Restriction Enabled"

    print(time_setting)

    if blockbuster.config.debug_mode:
        print("========= APPLICATION IS RUNNING IN DEBUG MODE ==========")

    try:
        if blockbuster.bb_dbconnector_factory.DBConnectorInterfaceFactory().create().db_version_check():
            import blockbuster.bb_routes
            print("Running...")

        else:
            raise RuntimeError(str.format("Incorrect database schema version. Wanted {0}", target_schema_version))

    except RuntimeError as e:
        logger.exception(e)
        audit.BBAuditLoggerFactory().create().logException('app', 'STARTUP', str(e))
        raise

startup()
