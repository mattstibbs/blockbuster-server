import config
import logging
import logging.handlers


# ######### Set up logging ##########
# log.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s", level=log.DEBUG)
logger = logging.getLogger("blockbuster")
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
tfh = logging.handlers.TimedRotatingFileHandler(str.format('{0}/app.log', config.log_directory),
                                                when='midnight', delay=False, encoding=None, backupCount=7)
tfh.setLevel(logging.INFO)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatterch = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')
formattertfh = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')
ch.setFormatter(formatterch)
tfh.setFormatter(formattertfh)

# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(tfh)