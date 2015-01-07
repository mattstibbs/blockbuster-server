__author__ = 'matt'
__version__ = '1.23.04'
__db_schema_version__ = '1.23.00'

from flask import Flask
app = Flask(__name__)

import blockbuster.bb_routes

print("Running...")