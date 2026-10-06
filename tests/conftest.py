import json
import sqlite3
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
FIXTURES = Path(__file__).parent / "fixtures"
SCHEMA = PROJECT_ROOT / "database" / "schema.sql"


def load_fixture(name):
    """Read a saved API response from tests/fixtures/ (never the live API)."""
    with open(FIXTURES / name, encoding="utf-8") as file:
        return json.load(file)


def build_database(connection):
    """Create every table from schema.sql and turn on foreign keys, like the pipeline does."""
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA.read_text())
    return connection


@pytest.fixture
def db():
    """A fresh in-memory database for each test, so tests never touch data/player_projection.db."""
    connection = build_database(sqlite3.connect(":memory:"))
    yield connection
    connection.close()


@pytest.fixture
def teams_path():
    return FIXTURES / "teams.json"
