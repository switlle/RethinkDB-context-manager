class Config(object):
    ROOT = True
    ROOT_USER = {'login': 'root', 'passw': 'b4b8daf4b8ea9d39568719e1e320076f'}
    USER_PERMISSION = None
    DB_CONFIG = { 'host': 'localhost', 'port': 28015, }
    DB_NAME = 'data'
    DB_TAB = {'tab_1': 'data', 'tab_2': 'log', 'tab_3': 'root'}
    DB_CONT = {'login': None, 'name': None, 'passw': None, 'gender': None, 'reg_date': None, 'ch_date': None, 'phone': None, 'email': None}
    HELP = {'Create a new user and edit the user': 'method POST', \
            'Format of the incoming data': \
            {'*login': 'your login', \
            '*email': 'mail@mail.ru', \
            '*phone': '79005006826', \
            '*pass': 'XXXXXXXXXX', \
            'name': 'not required, are added when editing a profile', \
            'gender': 'not required, are added when editing a profile'} , \
            'explanations': 'profile editing is performed after login and password are specified', \
            'example edit user': 'curl -s -u login:pass -H Content-Type: application/json -X POST -d YOUR DATA http://uwsgi.loc:5000/api/user', \
            'example create new user': 'curl -s -H Content-Type: application/json -X POST -d YOUR DATA http://uwsgi.loc:5000/api/new' }
