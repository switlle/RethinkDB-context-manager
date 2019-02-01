from flask import Flask
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
from hashlib import md5
from config import Config

app = Flask(__name__)
auth = HTTPBasicAuth()
app.config.from_object(Config)
api = Api(app)

def setpasswd(login:str, passw:str) -> str:
    """Преобразование пароля и логина в хеш MD5"""
    return str(md5(str(passw+login).lower().encode('utf-8')).hexdigest())
    
@auth.verify_password
def verify_password(username, password):
    """Проверка пароля и логина"""
    users = app.config['USERS']
    if username.lower() in users.keys():
        if users[str(username.lower())] == setpasswd(username.lower(), password):
            return users[str(username.lower())] #При совпедении пароля, возвращаем хеш пароля из БД
    return None

class Main(Resource):
    @auth.login_required
    def get(self):
        return {'GET message': 'GET !!!!!!'}
    
    @auth.login_required
    def post(self):
        return {'POST message': 'POST !!!!!!!'}

# Route
api.add_resource(Main, '/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
