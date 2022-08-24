from run import app as t_app

import pytest

@pytest.fixture()
def app():
    t_app.config.update({
        "TESTING": True,
    })
    yield t_app

@pytest.fixture()
def client(app):
    return app.test_client()

def test_page_not_found(client):
    res = client.get("/asdf", follow_redirects=False)
    assert res.status_code == 404