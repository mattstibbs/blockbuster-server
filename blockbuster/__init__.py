__author__ = 'matt'
__version__ = '1.24.00'
__db_schema_version__ = '1.24.00'

from flask import Flask
app = Flask(__name__)

import blockbuster.bb_routes

print("Running...")