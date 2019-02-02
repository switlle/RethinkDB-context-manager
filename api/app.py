from flask import Flask, abort, jsonify, make_response, request
from flask_httpauth import HTTPBasicAuth
from rethinkdbcm import UseDatabase
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
            # curl -s -G http://uwsgi.loc:5000/api/db
            if request.method == 'GET':
                d = db.all_db()
            # curl -s -X POST http://uwsgi.loc:5000/api/db
            elif request.method == 'POST': 
                d = db.create_db(use_db)
            # curl -s -X DELETE http://uwsgi.loc:5000/api/db
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
        conf['db'] = app.config['DB_NAME']
        name = list(app.config['DB_TAB'].values())
        with UseDatabase(conf) as db:
            # curl -s -G -u root:root http://uwsgi.loc:5000/api/tab
            if request.method == 'GET':
                """Запрос таблиц"""
                t = db.all_table()
            # curl -s -u root:root -X POST http://uwsgi.loc:5000/api/tab
            elif request.method == 'POST':
                """Создание таблицы"""
                t = ''
                for n in range(len(name)):
                    if n != len(name)-1:
                        message = db.create_tab(name[n])
                        t = t + '{},'.format(message)
                    else:
                        message = db.create_tab(name[n])
                        t = t + '{}'.format(message)
            # curl -s -u root:root -X DELETE http://uwsgi.loc:5000/api/tab
            elif request.method == 'DELETE':
                """Удалени таблицы"""
                t = ''
                for n in range(len(name)):
                    if n != len(name)-1:
                        message = db.del_tab(name[n])
                        t = t + '{},'.format(message)
                    else:
                        message = db.del_tab(name[n])
                        t = t + '{}'.format(message)
    else:
        t = { 'set table': 'not allowed' }
    return jsonify({'info': t})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
