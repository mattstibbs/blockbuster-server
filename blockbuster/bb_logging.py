import logging
import logging.handlers

# ######### Set up logging ##########
# log.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s", level=log.DEBUG)
logger = logging.getLogger('bb_log')
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
tfh = logging.handlers.TimedRotatingFileHandler('./logs/app.log', when='midnight', delay=False, encoding=None,
                                                backupCount=5)
tfh.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatterch = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formattertfh = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatterch)
tfh.setFormatter(formattertfh)

# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(tfh)