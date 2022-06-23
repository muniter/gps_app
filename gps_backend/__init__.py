from flask import Flask

app = Flask(__name__)

from . import database
session = database.Session()

from . import api
