class Config(object):
    ROOT = True
    ROOT_USER = { 'root': 'b4b8daf4b8ea9d39568719e1e320076f' }
    DB_CONFIG = { 'host': 'localhost', 'port': 28015, }
    DB_NAME = 'data'
    DB_TAB = {'tab_1': 'data', 'tab_2': 'log'}
    DB_CONT = {'new': {'name': None, 'passw': None, 'gender': None, 'reg_date': None, 'ch_date': None, 'phone': None, 'email': None}}
    HELP = {'Create a new user and edit the user': 'method POST', \
            'Format of the incoming data': \
            {'your login': {'email': 'mail@mail.ru', \
                            'phone': '79005006826', \
                            'pass': 'XXXXXXXXXX'} }, \
            'other data 1': 'name, gender', \
            'other data 2': 'made after registration using login and password',
            'example edit user': 'curl -s -u login:pass -H Content-Type: application/json -X POST -d YOUR DATA http://uwsgi.loc:5000/api/user', \
            'example create new user': 'curl -s -H Content-Type: application/json -X POST -d YOUR DATA http://uwsgi.loc:5000/api/new' }
    
    DATA = { 'john': {'name': None, 'passw': '018ff8ac396bc810a93e2f84dfbb1714', 'gender': None, 'reg_date': None, 'ch_date': None, 'phone': None, 'email': None}, \
            'susan': {'name': None, 'passw': '35699bdb666b55656fabd4a201c6291f', 'gender': None, 'reg_date': None, 'ch_date': None, 'phone': None, 'email': None} }
