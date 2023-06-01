import sys, inspect

list_of_models=[]
class User():
    def __init__(self, data):
        self.id = data.get('id', 'None')
        self.username = data.get('username', 'None')
        self.password = data.get('password', 'None')

    def __str__(self):
        return f"User(id={self.id}, username={self.username}, password={self.password})"

class User1():
    def __init__(self, data):
        self.id = data.get('id', 'None')
        self.username = data.get('username', 'None')
        self.password = data.get('password', 'None')

    def __str__(self):
        return f"User1(id={self.id}, username={self.username}, password={self.password})"


def get_classes():
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj):
            list_of_models.append(obj)
get_classes()
print(list_of_models)