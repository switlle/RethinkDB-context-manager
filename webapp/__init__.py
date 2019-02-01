from flask import Flask
from flask_restful import Api

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)

from webapp import resources
from webapp.resources import Main

# Route
api.add_resource(Main, '/')
