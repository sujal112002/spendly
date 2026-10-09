import pytest

from app import app as flask_app


@pytest.fixture
def app():
    # pytest-flask builds the `client` fixture from this one
    flask_app.config.update(TESTING=True)
    return flask_app
