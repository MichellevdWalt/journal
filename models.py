import datetime
from peewee import *

DATABASE = SqliteDatabase('journal.db')

class Journal(Model):
    title = CharField()
    date = DateTimeField(default=datetime.datetime.now)
    time_spent = CharField()
    learnt = CharField()
    resources = CharField()
    
    
    class Meta:
        database = DATABASE
        order_by = ('-date',)

    @classmethod
    def create_journal_entry(cls, title, time_spent, learnt, resources):
        try:
            with DATABASE.transaction():
                cls.create(
                    title=title,
                    time_spent=time_spent,
                    learnt=learnt,
                    resources=resources)
        except:
            pass
            
            

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Journal,], safe=True)
    DATABASE.close()