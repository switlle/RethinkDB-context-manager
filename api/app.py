from flask import Flask, abort, jsonify, make_response
from flask_httpauth import HTTPBasicAuth
from hashlib import md5
from config import Config

app = Flask(__name__)
auth = HTTPBasicAuth()
app.config.from_object(Config)


def setpasswd(login:str, passw:str) -> str:
    """Преобразование пароля и логина в хеш MD5"""
    return str(md5(str(passw+login).lower().encode('utf-8')).hexdigest())


@auth.verify_password
def verify_password(username, password):
    """Проверка пароля и логина"""
    users = app.config['DATA']
    #Если login найден в БД, проверяем совпадает ли passwd
    if username.lower() in users.keys():
        if users[str(username.lower())]['passw'] == setpasswd(username.lower(), password):
    #При совпедении passwd, возвращаем хеш passwd из БД
            return users[str(username.lower())]
    return None


@app.errorhandler(400)
def bad_request(error):
    """Ответ при неправильном запросе"""
    return make_response(jsonify({'error': 'BadRequest'}), 400)


@app.errorhandler(404)
def not_found(error):
    """Ответ при отсутствии данных в базе"""
    return make_response(jsonify({'error': 'NotFound'}), 404)


@app.route('/api', methods=['GET','POST'])
@auth.login_required
def everyone():
    """Запрос данных о всех пользователях"""
    # curl -s -u john:hello -X POST http://192.168.0.12:5000/api
    # curl -s -u john:hello -G http://192.168.0.12:5000/api
    return jsonify(app.config['DATA'])


@app.route('/api/<todo>', methods=['GET','POST'])
@auth.login_required
def oneof(todo):
    """Запрос данных по конкретному пользователю"""
    if todo in app.config['DATA'].keys():
    # curl -s -u john:hello -X POST http://192.168.0.12:5000/api/susan
    # curl -s -u john:hello -G http://192.168.0.12:5000/api
        return jsonify({str(todo): app.config['DATA'][str(todo)]})
    else:
        abort(404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
