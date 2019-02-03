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
    conf = app.config['DB_CONFIG']
    use_db = app.config['DB_NAME']
    tab = app.config['DB_TAB']['tab_1']
    tab_root = app.config['DB_TAB']['tab_3']
    with UseDatabase(conf, use_db) as db:
        try:
            root = db.getroot(tab_root)['login']
            root_passw = db.getroot(tab_root)['passw']
        except TypeError:
            root, root_passw = None, None
        rt = root
        if not rt:
            root = app.config['ROOT_USER']['login']
            root_passw = app.config['ROOT_USER']['passw']
        if username.lower() == root:
            if root_passw == setpasswd(username.lower(), password):
                app.config['USER_PERMISSION'] = True
                #При совпедении passwd, возвращаем хеш passwd root
                passw = db.getroot(tab_root)['passw'] if rt else root_passw
                return passw
        else:
            try:
                usr = db.gettask(tab, str(username.lower()))['login']
                passw = db.gettask(tab, str(username.lower()))['passw']
            except TypeError:
                usr = None
            if usr == username.lower():
                if passw == setpasswd(username.lower(), password):
                    app.config['USER_PERMISSION'] = username.lower()
                    return db.gettask(tab, str(username.lower()))['passw']
    return None


@app.errorhandler(404)
def not_found(error):
    """Ответ при отсутствии данных"""
    return make_response(jsonify({'error': 'NotFound'}), 404)


@app.route('/api/db', methods=['GET','POST','DELETE'])
@auth.login_required
def setdb():
    """Служебный метод"""
    """Запрос баз данных, создание и удаление"""
    if app.config['USER_PERMISSION'] == True:
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
    if app.config['USER_PERMISSION'] == True:
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
    """Запрос и изменение root пароля, создание нового root пользователя и его удаление"""
    """После создания имени пользователя, его изменить нельзя, 
        только если удалить и создать нового root пользователя с новым именем"""
    conf = app.config['DB_CONFIG']
    use_db = app.config['DB_NAME']
    tab = app.config['DB_TAB']['tab_3']
    if app.config['USER_PERMISSION'] == True:
        if request.method == 'GET':
            with UseDatabase(conf, use_db) as db:
                try:
                    n = db.getroot(tab)
                except (KeyError, TypeError):
                    n = { 'error': 'the record does not exist' }
                if not n:
                    n = { 'error': 'the record does not exist' }
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
                    n = db.getroot(tab)['login']
                    id_name = n
                except (KeyError, TypeError):
                    n = None
                if not n:
                    n = db.insert(tab, new_json)
                elif n:
                    n = db.updetask(tab, id_name, new_json)
        elif request.method == 'DELETE':
            with UseDatabase(conf, use_db) as db:
                try:
                    n = db.getroot(tab)['login']
                    id_name = n
                except (KeyError, TypeError):
                    n = None
                if n:
                    n = db.delltask(tab, id_name)
                else:
                    n = { 'error': 'the record does not exist' }
        else:
            n = { 'error method': 'method is not supported' }
    return jsonify({'info': n})
        
    
@app.route('/api/all', methods=['GET','POST','DELETE'])
@auth.login_required
def all_users():
    """Служебный метод"""
    """Запрос содержания всех таблиц DB"""
    if app.config['USER_PERMISSION'] == True:
        if request.method == 'GET':
            conf = app.config['DB_CONFIG']
            use_db = app.config['DB_NAME']
            tab = app.config['DB_TAB']['tab_1']
            with UseDatabase(conf, use_db) as db:
                n = db.gettasks(tab)
        else:
            n = { 'error method': 'method is not supported' }
    else: n = { 'for user ' + app.config['USER_PERMISSION']: 'this request is not allowed' }
    return jsonify({'info': n})


@app.route('/api/new', methods=['GET','POST'])
def new_user():
    """Метод доступный для всех"""
    """Создание нового пользователя"""
#curl -s -H "Content-Type: application/json" -X POST -d '{"user": "mail@mail.ru"}' http://uwsgi.loc:5000/api/new
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


@app.route('/api/user/<task_id>', methods=['GET', 'POST', 'DELETE'])
@auth.login_required
def get_user(task_id):
    """Метод доступный для конкретного пользователя по login и passw или для пользователя root"""
    """Запрос данных о пользователе, редактирование данных и удаление"""
    if app.config['USER_PERMISSION'] == str(task_id).lower() or app.config['USER_PERMISSION'] == True:
        conf = app.config['DB_CONFIG']
        use_db = app.config['DB_NAME']
        tab = app.config['DB_TAB']['tab_1']
        if request.method == 'GET': #Запрос данных о пользователе
            with UseDatabase(conf, use_db) as db:
                n = db.gettask(tab, str(task_id))
        elif request.method == 'POST': #Редактирование данных пользователя
            new_json = {}
            with UseDatabase(conf, use_db) as db:
                try:
                    data = db.gettask(tab, str(task_id))
                except (KeyError, TypeError):
                    data = None
                if data:
                    new_json['passw'] = setpasswd(data['login'], request.json['passw']) if 'passw' in request.json else data['passw']
                    new_json['phone'] = request.json['phone'] if 'phone' in request.json else data['phone']
                    new_json['email'] = request.json['email'] if 'email' in request.json else data['email']
                    new_json['reg_date'] = data['reg_date']
                    new_json['ch_date'] = datetime.now().strftime("%Y-%m-%d %X")
                    new_json['name'] = request.json['name'] if 'name' in request.json else data['name']
                    new_json['gender'] = request.json['gender'] if 'gender' in request.json else data['gender']
                    n = db.updetask(tab, data['login'], new_json)
                else:
                    n = { 'error': 'the record does not exist' }
        elif request.method == 'DELETE': #Удаление данных о пользователе
            with UseDatabase(conf, use_db) as db:
                try:
                    n = db.gettask(tab, str(task_id))['login']
                except (KeyError, TypeError):
                    n = None
                id_name = n
                if n:
                    n = db.delltask(tab, id_name)
                else:
                    n = { 'error': 'the record does not exist' }
        else:
            n = { 'error method': 'method is not supported' }
    else:
        n =  { 'for user ' + app.config['USER_PERMISSION']: 'the request ' + str(task_id).lower() + ' is not allowed' }
    return jsonify({'info': n})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
