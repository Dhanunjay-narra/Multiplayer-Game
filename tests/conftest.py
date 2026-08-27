"""Global test fixtures and path configuration."""
import os
import sys
import pytest_asyncio

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.database import init_db


@pytest_asyncio.fixture(autouse=True, scope="function")
async def setup_test_db():
    """Ensures test database tables are created before running tests."""
    await init_db()
