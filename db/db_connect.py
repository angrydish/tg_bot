from models.models import *
from db.config import host, port, password, database, user
from db.db import *

db = DB({
    'host': host,
    'port': port,
    'database': database,
    'user': user,
    'password': password
    })

print(db.execute_one('test_query'))
try:
    db.execute_none('create_database')
except BaseException as e:
    print("----------")
    print("if you see this message, then db tried to die, but all went good, error:")
    print(e)
    print("as i said it did")
    print("----------")