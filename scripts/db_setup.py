import os
from dotenv import load_dotenv
load_dotenv()

from app.database import db
from app.models.user import User
from app.models.url import URL
from app.models.event import Event
from peewee import PostgresqlDatabase, chunked
import csv

database = PostgresqlDatabase(
    os.environ.get("DATABASE_NAME", "hackathon_db"),
    host=os.environ.get("DATABASE_HOST", "localhost"),
    port=int(os.environ.get("DATABASE_PORT", 5432)),
    user=os.environ.get("DATABASE_USER", "postgres"),
    password=os.environ.get("DATABASE_PASSWORD", "postgres"),
)
db.initialize(database)

db.connect()
db.create_tables([User, URL, Event], safe=True)
db.close()

def load_csv(filepath, model):
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with db.atomic():
        for batch in chunked(rows, 100):
            model.insert_many(batch).execute()

if User.select().count() == 0:
    load_csv("seeds/users.csv", User)
if URL.select().count() == 0:
    load_csv("seeds/urls.csv", URL)
if Event.select().count() == 0:
    load_csv("seeds/events.csv", Event)

print("Tables created and populated successfully.")