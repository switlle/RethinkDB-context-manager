import rethinkdb as db

class UseDatabase:
    def __init__(self, config: dict) -> None:
        self.config = config

    def __enter__(self):
        """Подключение к базе данных RethinkDB"""
        self.conn = db.connect(**self.config).repl()
        return self

    def gettasks(self, table):
        """Получение всех записей из таблицы базы данных"""
        tasks = list(db.table(table).run())
        return tasks

    def gettask(self, table, req):
        """Получение записей из таблицы базы данных по определенному ID"""
        task = db.table(table).get(req).run()
        return task

    def getval(self, id, table):
        """Получение значений, без ключей из таблицы базы данных по определенному ID"""
        val = list(db.table(table).get(id).values().run())
        return val

    def insert(self, table, json):
        """Функция добавления новой записи в таблицe БД"""
        ins = db.table(table).insert(json).run()
        return ins

    def updat(self, table, id, json):
        """Функция обновления записи в таблице БД по определнному ID"""
        upd = db.table(table).get(id).update(json).run()
        return upd

    def delltask(self, table, req):
        """Функция удаления записи в таблице БД по определнному ID"""
        dell = db.table(table).get(req).delete().run()
        return dell

    def countid(self, table, req):
        """Функция определения записи в таблице БД по определнному ID
        0 - записи нет, 1 - запись имеется"""
        count = db.table(table).filter({'id': req}).count().run()
        return count

    def countall(self, table):
        """Функция определения количества записи в таблице БД"""
        countal = db.table(table).count().run()
        return countal

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Отключение от БД"""
        self.conn.close()
