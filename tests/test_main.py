import os
import pytest
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
from main import app, db


@pytest.fixture
def client():
    client = app.test_client()
    cleanup()
    db.create_all()
    yield client


def cleanup():
    db.drop_all()


def test_index_page_exists(client):
    response = client.get('/')
    assert b'Enter your guess' in response.data
