"""API test specific test configuration"""

import pytest

import fastapi.testclient

from groceryaid import app


@pytest.fixture
def testclient():
    """Returns test client for API tests"""
    return fastapi.testclient.TestClient(app)
