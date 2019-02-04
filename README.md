## RethinkDB context manager

Диспетчер контекста для работы с базой данных RethinkDB

Пример использования:

```python
from rethinkdbcm import UseDatabase
conf = app.config['DB_CONFIG']
use_db = str(app.config['DB_NAME'])
with UseDatabase(conf) as db:
     if request.method == 'GET':
          d = db.all_db()
     elif request.method == 'POST': 
          d = db.create_db(use_db)
      elif request.method == 'DELETE':
          d = db.del_db(use_db)
```

В диспетчере контекста реализовано:

```python
"""Получение всех баз данных"""
all_db()
"""Создание новой базы данных"""
create_db(name)
"""Удаление базы данных"""
del_db(name)
"""Получение всех таблиц из подключенной БД"""
all_table(name_db)
"""Создание новой таблицы в базе данных"""
create_tab(name_db, name_t)
"""Удаление таблицы из базы данных"""
del_tab(name_db, name_t)
"""Добавление новой записи в таблицу БД"""
insert(name_t, json)
"""Определение записи в таблице БД по определнному ID 0 - записи нет, 1 - запись имеется"""
countid(name_t, id_name, req)
"""Получение всех записей из таблицы базы данных, если записи отсутствуют возращает None"""
gettasks(name_t)
"""Получение записей из таблицы базы данных по определенному ID"""
gettask(name_t, req)
"""Обновление записи в таблице БД по определнному ID"""
updetask(name_t, id_name, json)
"""Удаление записи в таблице БД по определнному ID"""
delltask(name_t, id_name)
"""Получение значений, без ключей из таблицы БД по определенному ID"""
getval(name_t, id_name)
"""Определение количества записи в таблице БД"""
countall(name_t)
```
