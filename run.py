__author__ = 'matt'

import datetime
import blockbuster

blockbuster.app.debug = blockbuster.config.debug_mode

blockbuster.bb_logging.logger.info("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
blockbuster.bb_logging.logger.info("@@@@@@@@@@@@@@@@@@ BlockBuster " + blockbuster.__version__ + " "
                                                                                                        "@@@@@@@@@@@@@@@@@@")
blockbuster.bb_logging.logger.info("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
blockbuster.bb_logging.logger.info("=== Application startup - " + str(datetime.datetime.now()) +  " ====")
blockbuster.bb_logging.logger.info(
    '================Time restriction disabled================') \
    if not blockbuster.config.timerestriction else blockbuster.bb_logging.logger.info(
    '================Time restriction enabled================')

blockbuster.bb_logging.logger.info("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

if blockbuster.config.debug_mode:
    blockbuster.bb_logging.logger.info("========= APPLICATION IS RUNNING IN DEBUG MODE ==========")


# This section only applies when you are running run.py directly
if __name__ == '__main__':
    blockbuster.bb_logging.logger.info("Running http on port 5001")
    blockbuster.app.run(host='127.0.0.1', port=5001, debug=True)