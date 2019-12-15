from peewee import *


db = SqliteDatabase('data/mystery_santa.db')


class Group(Model):
    name = CharField(unique=True)
    password = CharField()
    
    class Meta:
        database = db
        

class User(Model):
    name = CharField()
    chat_id = IntegerField(primary_key=True, unique=False)
    message_id = IntegerField(null=True)
    group = ForeignKeyField(Group, null=True, related_name='users')
    santa = ForeignKeyField('self', null=True, related_name='targets')
    
    class Meta:
        database = db
        
        
User.create_table()
Group.create_table()
for user in User.select():
    targets = [target for target in user.targets]
    print(user.chat_id, user.name, 'santa =', user.santa, 'targets =', *targets)
