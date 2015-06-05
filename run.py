__author__ = 'matt'

import blockbuster

if __name__ == '__main__':
    blockbuster.bb_logging.logger.info("Running http on port 5000")
    blockbuster.app.run(host='0.0.0.0', debug=True)
