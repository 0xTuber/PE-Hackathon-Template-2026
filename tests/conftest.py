import os
import tempfile

os.environ["PROMETHEUS_MULTIPROC_DIR"] = tempfile.mkdtemp()

import pytest
from app import create_app
from app.database import db
from app.models.user import User
from app.models.url import URL
from app.models.event import Event

@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for each test."""
    # Create the app with standard test config
    app = create_app({
        "TESTING": True,
    })
    
    # Create tables before tests run
    with app.app_context():
        db.create_tables([User, URL, Event])
        
    yield app
    
    # Drop tables after tests finish
    with app.app_context():
        db.drop_tables([User, URL, Event])

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(autouse=True)
def clean_db():
    """Clean all tables before each test to ensure isolation."""
    User.delete().execute()
    URL.delete().execute()
    Event.delete().execute()
