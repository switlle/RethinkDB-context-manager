from flask import Flask, abort, jsonify, make_response, request
from flask_httpauth import HTTPBasicAuth
from rethinkdbcm import UseDatabase
from hashlib import md5
import json
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
    root = app.config['ROOT_USER']
    #Если login найден в БД, проверяем совпадает ли passwd
    if username.lower() in root.keys() and app.config['ROOT']:
        if root[str(username.lower())] == setpasswd(username.lower(), password):
        #При совпедении passwd, возвращаем хеш passwd root
            return root[str(username.lower())]
    elif username.lower() in users.keys():
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
    # curl -s -u john:hello -X POST http://uwsgi.loc:5000/api
    # curl -s -u john:hello -G http://uwsgi.loc:5000/api
    return jsonify(app.config['DATA'])


@app.route('/api/<todo>', methods=['GET','POST'])
@auth.login_required
def oneof(todo):
    """Запрос данных по конкретному пользователю"""
    if todo in app.config['DATA'].keys():
    # curl -s -u john:hello -X POST http://uwsgi.loc:5000/api/susan
    # curl -s -u john:hello -G http://uwsgi.loc:5000/api
        return jsonify({str(todo): app.config['DATA'][str(todo)]})
    else:
        abort(404)


@app.route('/api/db', methods=['GET','POST','DELETE'])
@auth.login_required
def setdb():
    """Запрос баз данных, создание и удаление"""
    if app.config['ROOT']:
        conf = app.config['DB_CONFIG']
        use_db = str(app.config['DB_NAME'])
        with UseDatabase(conf) as db:
            # curl -s -u root:root -G http://uwsgi.loc:5000/api/db
            if request.method == 'GET':
                d = db.all_db()
            # curl -s -u root:root -X POST http://uwsgi.loc:5000/api/db
            elif request.method == 'POST': 
                d = db.create_db(use_db)
            # curl -s -u root:root -X DELETE http://uwsgi.loc:5000/api/db
            elif request.method == 'DELETE':
                d = db.del_db(use_db)
    else:
        d = { 'set database': 'not allowed' }
    return jsonify({'info': d})
    
@app.route('/api/tab', methods=['GET','POST','DELETE'])
@auth.login_required
def settab():
    """Запрос таблиц, создание и удаление"""
    if app.config['ROOT']:
        conf = app.config['DB_CONFIG']
        use_db = app.config['DB_NAME']
        name = list(app.config['DB_TAB'].values())
        t = ''
        with UseDatabase(conf, use_db) as db:
            # curl -s -G -u root:root http://uwsgi.loc:5000/api/tab
            if request.method == 'GET':
                """Запрос таблиц"""
                t = db.all_table(use_db)
            # curl -s -u root:root -X POST http://uwsgi.loc:5000/api/tab
            elif request.method == 'POST':
                """Создание таблицы"""
                for n in range(len(name)):
                    message = db.create_tab(use_db, name[n])
                    if n != len(name)-1:
                        t = t + '{},'.format(message)
                    else:
                        t = t + '{}'.format(message)
            # curl -s -u root:root -X DELETE http://uwsgi.loc:5000/api/tab
            elif request.method == 'DELETE':
                """Удалени таблицы"""
                for n in range(len(name)):
                    message = db.del_tab(use_db, name[n])
                    if n != len(name)-1:
                        t = t + '{},'.format(message)
                    else:
                        t = t + '{}'.format(message)
    else:
        t = { 'set table': 'not allowed' }
    return jsonify({'info': t})
    
    
@app.route('/api/new', methods=['GET','POST'])
def new_user():
#curl -s -H "Content-Type: application/json" -X POST -d '{"name": {"user": "mail@mail.ru"}}' http://uwsgi.loc:5000/api/new
    if request.method == 'POST':
        js = json.loads(json.dumps(request.json))
        json_key = str({'Name': str(*list(js.keys()))})
        #json_keys = '\{\'Name\': {}\}'.format(*json_key)
        json_value = str(*list(js.values()))
        return jsonify(json_key, json_value)
    elif request.method == 'GET':
        return jsonify(app.config['HELP'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
