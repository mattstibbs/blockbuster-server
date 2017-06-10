from blockbuster import app
import logging

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Running http on port 5000")
    app.run(host='0.0.0.0', debug=True)
