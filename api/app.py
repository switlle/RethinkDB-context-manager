from flask import Flask, abort, jsonify, make_response, request
from flask_httpauth import HTTPBasicAuth
from rethinkdbcm import UseDatabase
from hashlib import md5
from datetime import datetime
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
    root = app.config['ROOT_USER']
    conf = app.config['DB_CONFIG']
    use_db = app.config['DB_NAME']
    tab = app.config['DB_TAB']['tab_1']
    with UseDatabase(conf, use_db) as db:
        if username.lower() in root.keys():
            if root[str(username.lower())] == setpasswd(username.lower(), password):
            #При совпедении passwd, возвращаем хеш passwd root
                app.config['GET_USER'] = str(username.lower())
                return root[str(username.lower())]
        else:
            try:
                l = db.gettask(tab, str(username.lower()))['login']
            except TypeError:
                l = None
            if l == username.lower():
                if db.gettask(tab, str(username.lower()))['passw'] == setpasswd(username.lower(), password):
                    app.config['GET_USER'] = str(username.lower())
                    return db.gettask(tab, str(username.lower()))['passw']
    
    return None
    


@app.errorhandler(400)
def bad_request(error):
    """Ответ при неправильном запросе"""
    return make_response(jsonify({'error': 'BadRequest'}), 400)


@app.errorhandler(404)
def not_found(error):
    """Ответ при отсутствии данных в базе"""
    return make_response(jsonify({'error': 'NotFound'}), 404)


@app.route('/api/db', methods=['GET','POST','DELETE'])
@auth.login_required
def setdb():
    """Служебный метод"""
    """Запрос баз данных, создание и удаление"""
    if app.config['GET_USER'] == 'root':
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
    """Служебный метод"""
    """Запрос таблиц, создание и удаление"""
    if app.config['GET_USER'] == 'root':
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
    

@app.route('/api/admin', methods=['GET','POST','DELETE'])
@auth.login_required
def setadmin():
    """Служебный метод"""
    """Запрос, создание и изменение root пользователя и пароля"""
    conf = app.config['DB_CONFIG']
    use_db = app.config['DB_NAME']
    tab = app.config['DB_TAB']['tab_3']
    if app.config['GET_USER'] == 'root':
        if request.method == 'GET':
            with UseDatabase(conf, use_db) as db:
                n = db.gettasks(tab)
        elif request.method == 'POST':
            new_json = {}
            if not request.json:
                err = { 'request': 'not json format' }
                return jsonify({'error': err})
            elif not 'login' in request.json or not request.json['login']:
                err = { 'request': 'login field is empty' }
                return jsonify({'error': err})
            elif not 'passw' in request.json or not request.json['passw']:
                err = { 'request': 'password field is empty' }
                return jsonify({'error': err})
            new_json['id'] = str(request.json['login'].lower())
            new_json['login'] = new_json['id']
            new_json['passw'] = setpasswd(new_json['login'], request.json['passw'])
            with UseDatabase(conf, use_db) as db:
                try:
                    n = db.gettasks(tab)['login']
                except (KeyError, TypeError):
                    n = None
                if not n:
                    n = db.insert(tab, new_json)
                #elif n:
                    
        else:
            n = { 'error method': 'method is not supported' }
    return jsonify({'info': n})
        
    
    
@app.route('/api/all', methods=['GET','POST','DELETE'])
@auth.login_required
def all_users():
    """Служебный метод"""
    """Запрос содержания всех таблиц DB"""
    if request.method == 'GET' and app.config['GET_USER'] == 'root':
        conf = app.config['DB_CONFIG']
        use_db = app.config['DB_NAME']
        tab = app.config['DB_TAB']['tab_1']
        with UseDatabase(conf, use_db) as db:
            n = db.gettasks(tab)
    else:
        n = { 'error method': 'method is not supported' }
    return jsonify({'info': n})


@app.route('/api/new', methods=['GET','POST'])
def new_user():
    """Метод доступный для всех"""
    """Создание нового пользователя"""
#curl -s -H "Content-Type: application/json" -X POST -d '{"name": {"user": "mail@mail.ru"}}' http://uwsgi.loc:5000/api/new
    content = app.config['DB_CONT']
    conf = app.config['DB_CONFIG']
    use_db = app.config['DB_NAME']
    tab = app.config['DB_TAB']['tab_1']
    id_name = 'id'
    new_json = {}
    if request.method == 'GET':
        return jsonify(app.config['HELP'])
    elif request.method == 'POST':
        if not request.json:
            err = { 'request': 'not json format' }
            return jsonify({'error': err})
        elif not 'passw' in request.json or not request.json['passw']:
            err = { 'request': 'password field is empty' }
            return jsonify({'error': err})
        elif not 'login' in request.json or not request.json['login']:
            err = { 'request': 'login field is empty' }
            return jsonify({'error': err})
        elif not 'phone' in request.json or not request.json['phone']:
            err = { 'request': 'phone number field is empty' }
            return jsonify({'error': err})
        elif not 'email' in request.json or not request.json['email']:
            err = { 'request': 'email field is empty' }
            return jsonify({'error': err})
        else:
            new_json['id'] = str(request.json['login'].lower())
            new_json['login'] = new_json['id']
            new_json['passw'] = setpasswd(new_json['login'], request.json['passw'])
            new_json['phone'] = request.json['phone']
            new_json['email'] = request.json['email']
            new_json['reg_date'] = datetime.now().strftime("%Y-%m-%d %X")
            new_json['ch_date'] = new_json['reg_date']
            new_json['name'] = request.json['name'] if 'name' in request.json else content['name']
            new_json['gender'] = request.json['gender'] if 'gender' in request.json else content['gender']
            with UseDatabase(conf, use_db) as db:
                if db.countid(tab, id_name, new_json['id']) == 0:
                #Если записи нет, добавляем новую
                    n = db.insert(tab, new_json)
                else:
                    n = { 'user ' + new_json['login']: 'already exist' }
                return jsonify({'info': n})


@app.route('/api/<task_id>', methods=['GET', 'POST', 'DELETE'])
@auth.login_required
def get_user(task_id):
    """Запрос содержания таблици по определенному ID (login), обновление и ее удаление из DB"""
    conf = app.config['DB_CONFIG']
    use_db = app.config['DB_NAME']
    tab = app.config['DB_TAB']['tab_1']
    if request.method == 'GET':
        with UseDatabase(conf, use_db) as db:
            n = db.gettask(tab, str(task_id))
        return jsonify({'info': n})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
