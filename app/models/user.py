from peewee import CharField, IntegerField, DateTimeField, BooleanField

from app.database import BaseModel

class User (BaseModel):
    id = IntegerField(primary_key=True)
    username = CharField()
    email = CharField()
    created_at = DateTimeField()