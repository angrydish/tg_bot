import psycopg2
from config import host, port, password, db_name, user

# try:
#     connection = psycopg2.connect(
#         host=host,
#         user=user,
#         password=password,
#         database=db_name,
#         port=port
#     )
#     with connection.cursor() as cursor:
#         cursor.execute(
#             "select version();"
#         )
#         print(f'server version: {cursor.fetchall()}')
# except Exception as e:
#     print("something went wrong", e)
# finally:
#     if connection:
#         connection.close()
#         print("connection closed.")

from psycopg2.extras import RealDictCursor
class User():
    def __init__(self, data):
        self.id = data.get('id', None)
        self.name = data.get('name', None)
        self.password = data.get('password', None)
    def __str__(self):
        return f"User(id={self.id}, name={self.name}, password={self.password})"
class DB:
    def __init__(self, config : dict):
        self.config = config
        self.connection = psycopg2.connect(**self.config)
    def execute(self, query: str):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                data = cursor.fetchone()
                print(type(data))
                self.connection.commit()
                if data is None:
                    return None
                return self.pack_data(**data)
        except Exception as e:
            print(f'Execute error!\n {e}')
    def pack_data(self, **kwargs):
        return User(kwargs)

a= {'host': host, 'port': port, 'user': user, 'password': password, 'database': db_name}
db = DB(a)
man = db.execute("select id, name , password  from users where id=1;")
print(man)
print(man.id)
print(man.name)
print(man.password)
# db.execute("""create table if not exists users(
#     id serial primary key,
#     name text,
#     password text
# );
# """)