import psycopg2
from psycopg2.extras import RealDictCursor

import models.models
from db.config import host, port, password, database, user
from models.models import *
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





class DB:
    def __init__(self, config: dict):
        self.config = config
        self.connection = psycopg2.connect(**self.config)

    def read_query_name(self, query_name) -> str:
        try:
            with open(f'../queries/{query_name}' + '.sql', 'r') as file:
                query = file.read()
                return str(query)
        except Exception as e:
            raise Exception(f'Query exception!\n{e}')

    def pack_data(self, **kwargs):
        return User(kwargs)

    def execute_one(self, query_name: str, params: dict = None, model: list_of_models = None) -> models.models.get_classes():
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = self.read_query_name(query_name)
                cursor.execute(query, params)
                data = cursor.fetchone()
                #print((data.get('id')))
                self.connection.commit()
                if data is None:
                    return None
                if model is not None:
                    print(data)
                    return model(data)
                else:
                    return data
        except Exception as e:
            self.connection.rollback()
            raise Exception(f'Execute one error!\n {e}')

    def execute_all(self, query_name: str, params: dict = None, model: list_of_models = None) -> models.models.get_classes():
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = self.read_query_name(query_name)
                cursor.execute(query, params)
                data = cursor.fetchall()
                # print(type(data))
                self.connection.commit()
                if data is None:
                    return None
                #print("\n\n\n",data)
                #[print(_) for _ in data]
                return [model(_) for _ in data]
        except Exception as e:
            self.connection.rollback()
            raise Exception(f'Execute all error!\n {e}')

    def execute_none(self, query_name: str, params: dict = None):
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = self.read_query_name(query_name)
                cursor.execute(query, params)
                self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise Exception(f'Execute none error!\n{e}')



#a = {'host': host, 'port': port, 'user': user, 'password': password, 'database': db_name}
#db = DB(a)

# db.execute_none("""CREATE TABLE IF NOT EXISTS "users" (
#   "id" SERIAL PRIMARY KEY,
#   "username" text NOT NULL UNIQUE,
#   "password" text NOT NULL,
#   "number_of_files" int
# );
# """)
# db.execute_none("""CREATE TABLE IF NOT EXISTS "file" (
#   "id" SERIAL PRIMARY KEY,
#   "name" text NOT NULL,
#   "user_id" int NOT NULL,
#   "size" int NOT NULL,
#   "created_at" timestamp
# );
# """)
# db.execute_none("""
# ALTER TABLE "file" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");
# """)

# db.execute_none("""
# insert into users (username, password) values ('bebra','123');
# """)
#db.execute_none('create_database')
#man = db.execute_one('read_user', params={'username': 'bebra'}, model=User)
#print(man)
# users = db.execute_all('read_all_users')
# for user in users:
#     print(user)