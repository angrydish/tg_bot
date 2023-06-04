import sys, inspect

list_of_models=[]
class User():
    def __init__(self, data):
        self.id = data.get('id', 'None')
        self.telegram_id = data.get('telegram_id', 'None')
        self.username = data.get('username', 'None')
        self.password = data.get('password', 'None')
        self.number_of_files = data.get('number_of_files', 'None')

    def __str__(self):
        return f"User(id={self.id}, telegram_id={self.telegram_id} username={self.username}, password={self.password}, number_of_files={self.number_of_files})"

class User_File():
    def __init__(self, data):
        self.id = data.get('id', 'None')
        self.name = data.get('name', 'None')
        self.owner_telegram_id = data.get('owner_telegram_id', 'None')
        self.owner_user_id = data.get('owner_user_id', 'None')
        self.content = data.get('content', 'None')
        self.size = data.get('size', 'None')
        self.created_at = data.get('created_at', 'None')

    def __str__(self):
        return f"User_File(id={self.id}, name={self.name}, owner_telegram_id={self.owner_telegram_id}, owner_user_id={self.owner_user_id} content={self.content}, size={self.size}, created_at={self.created_at})"


def get_classes():
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj):
            list_of_models.append(obj)
get_classes()
print(list_of_models)