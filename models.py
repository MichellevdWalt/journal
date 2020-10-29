import datetime
from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('journal.db')


class User(UserMixin, Model):
    user_id = AutoField()
    username = CharField(unique=True)
    password = CharField(max_length=100)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

    def get_id(self):
           return (self.user_id)

    @classmethod
    def create_user(cls, username, password):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    password=generate_password_hash(password)
                )
        except IntegrityError:
            raise ValueError("User already exists")


class Journal(Model):
    title = CharField()
    date = DateTimeField(default=datetime.datetime.now)
    time_spent = CharField()
    learnt = CharField()
    resources = CharField()
    user = ForeignKeyField(
        User,
        backref='entries'
    )
    
    class Meta:
        database = DATABASE
        order_by = ('-date',)

    @classmethod
    def create_journal_entry(cls, title, time_spent, learnt, resources, user):
        try:
            with DATABASE.transaction():
                cls.create(
                    title=title,
                    time_spent=time_spent,
                    learnt=learnt,
                    resources=resources,
                    user=user)
        except:
            pass
            

class Tags(Model):
    user = ForeignKeyField(
        User,
        backref='tags'
    )
    tags = TextField()
    
    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)


class Relationship(Model):
    from_user = ForeignKeyField(User, backref='relationships')
    to_user = ForeignKeyField(User, backref='related_to')
    
    class Meta:
        database = DATABASE
        indexes = (
            (('from_user', 'to_user'), True),
        )
            
            

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Journal, Relationship, Tags], safe=True)
    DATABASE.close()