from flask import Flask
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
from config import Config

app = Flask(__name__)
auth = HTTPBasicAuth()
app.config.from_object(Config)
api = Api(app)

@auth.get_password
def get_pw(username):
    users = app.config['USERS']
    if username in users:
        return users.get(username)
    return None
    
class Main(Resource):
    @auth.login_required
    def get(self):
        return {"GET message": app.config['USERS']}
    
    @auth.login_required
    def post(self):
        return {"POST message": "Hello, World!"}

# Route
api.add_resource(Main, '/')
