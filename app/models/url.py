from peewee import CharField, DecimalField, IntegerField, DateTimeField, TextField, BooleanField

from app.database import BaseModel

class URL (BaseModel):
    id = IntegerField(primary_key=True)
    user_id = IntegerField()
    short_code = CharField()
    original_url = CharField()
    title = CharField()
    is_active = BooleanField()
    created_at = DateTimeField()
    updated_at = DateTimeField()