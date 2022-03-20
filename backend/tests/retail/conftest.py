"""Test confiurations"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine

import groceryaid.db


@pytest_asyncio.fixture(autouse=True)
async def database(monkeypatch, tmpdir):
    """Yield database connection with empty tables created"""
    dbfile = f"sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(dbfile)
    monkeypatch.setattr("groceryaid.db._db.get_engine", lambda: engine)
    await groceryaid.db.init()
    yield engine
