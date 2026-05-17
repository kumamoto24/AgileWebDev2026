import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_DATABASE_PATH = PROJECT_ROOT / "tests" / "test_app.db"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DATABASE_PATH}")

from app import app, db


def pytest_sessionstart(session):
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():
        db.create_all()


def pytest_sessionfinish(session, exitstatus):
    with app.app_context():
        db.session.remove()
        db.engine.dispose()

    if TEST_DATABASE_PATH.exists():
        TEST_DATABASE_PATH.unlink()