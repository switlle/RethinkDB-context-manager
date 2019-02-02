import rethinkdb as db
from rethinkdb.errors import ReqlOpFailedError

class UseDatabase:
    def __init__(self, config: dict, db=None) -> None:
        self.config = config
        self.config['db'] = db
#========= Connect to DB ============================
    def __enter__(self):
        """Подключение к базе данных RethinkDB"""
        self.conn = db.connect(**self.config).repl()
        return self

#========= Get, Create, Delete DB ===================
    def all_db(self):
        """Получение всех баз данных"""
        try:
            return db.db_list().run()
        except ReqlOpFailedError:
            d = { self.config['db']: 'does not exist' }
            return d
        
    def create_db(self, name):
        """Создание новой базы данных"""
        try: 
            return db.db_create(name).run()
        except ReqlOpFailedError:
            d = { name: 'the database is already there' }
            return d
        
    def del_db(self, name):
        """Удаление базы данных"""
        try:
            return db.db_drop(name).run()
        except ReqlOpFailedError:
            d = { name: 'database not found' }
            return d

#========== Get, Create, Delete Table ==================
    def all_table(self, name_db):
        """Получение всех таблиц из подключенной БД"""
        try:
            t = db.table_list().run(self.conn)
            if not t: #Если таблиц нет, выводим сообщение { 'table': 'not found' }
                t = { 'table in DB ' + name_db: 'not found' }
            return t
        except ReqlOpFailedError:
            t = { 'DB ' + name_db: 'does not exist' }
            return t
            
    def create_tab(self, name_db, name_t):
        """Создание новой таблицы в базе данных"""
        try: 
            return db.db(name_db).table_create(name_t).run()
        except ReqlOpFailedError:
            t = { name_t + ' in DB ' + name_db: 'the table already exists' }
            return t
            
    def del_tab(self, name_db, name_t):
        """Удаление таблицы из базы данных"""
        try:
            return db.db(name_db).table_drop(name_t).run()
        except ReqlOpFailedError:
            t = { name_t + ' in DB ' + name_db: 'the table does not exist' }
            return t

#=========================================================
    def insert(self, name_t, json):
        """Функция добавления новой записи в таблицe БД"""
        try:
            return db.table(name_t).insert(json).run()
        except ReqlOpFailedError:
            t = { name_t: 'the table does not exist' }
            return t

    def countid(self, name_t, id_name, req):
        """Функция определения записи в таблице БД по определнному ID
        0 - записи нет, 1 - запись имеется"""
        return db.table(name_t).filter({id_name: req}).count().run()
        
    def gettasks(self, name_t):
        """Получение всех записей из таблицы базы данных"""
        try:
            return list(db.table(name_t).run())[0]
        except (ReqlOpFailedError, IndexError):
            t = None #t = { name_t: 'the table does not exist' }
        #except :
        #    t = None
        return t

    def gettask(self, name_t, req):
        """Получение записей из таблицы базы данных по определенному ID"""
        return db.table(name_t).get(req).run()

    def getval(self, id, table):
        """Получение значений, без ключей из таблицы базы данных по определенному ID"""
        val = list(db.table(table).get(id).values().run())
        return val

    def updat(self, table, id, json):
        """Функция обновления записи в таблице БД по определнному ID"""
        upd = db.table(table).get(id).update(json).run()
        return upd

    def delltask(self, table, req):
        """Функция удаления записи в таблице БД по определнному ID"""
        dell = db.table(table).get(req).delete().run()
        return dell

    def countall(self, table):
        """Функция определения количества записи в таблице БД"""
        countal = db.table(table).count().run()
        return countal

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Отключение от БД"""
        self.conn.close()
