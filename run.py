__author__ = 'matt'

# import blockbuster
from blockbuster import app, bb_logging

if __name__ == '__main__':
    bb_logging.logger.info("Running http on port 5000")
    app.run(host='0.0.0.0', debug=True)
