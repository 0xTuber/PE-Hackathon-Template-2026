from peewee import CharField, DecimalField, IntegerField, DateTimeField, TextField

from app.database import BaseModel

class Event (BaseModel):
    id = IntegerField(primary_key=True)
    url_id = IntegerField()
    user_id = IntegerField()
    event_type = CharField()
    timestamp = DateTimeField()
    details = TextField()
    