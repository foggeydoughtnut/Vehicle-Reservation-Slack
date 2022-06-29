from app import create_data_dict, app as test_app
from models import User, db
import API.db.index
import pytest

@pytest.fixture()
def app():
    test_app.config.update({
        "TESTING": True,
    })
    yield test_app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_create_data_dict():
    valid_input_data = ['slack_user_id', 'command', 'vehicle_name', 'from', 'date_start', 'time_start', 'to', 'date_end', 'time_end']
    data = create_data_dict(valid_input_data)
    assert type(data) == dict
    assert data['command'] == 'vehicle_name'
    assert data['from'] == 'date_startTtime_start'
    assert data['to'] == 'date_endTtime_end'

    invalid_input_data = ['slack_user_id', 'command']
    error_data = create_data_dict(invalid_input_data)
    assert type(data) == dict
    assert error_data["Error"]

def test_login(client):
    # create test admin user to log in
    test_user = API.db.index.get_user_by_username('test-user')
    if (test_user):
        API.db.index.delete_user_by_id(test_user.id)
    
    test_user = API.db.index.create_user('test-user', 'test')

    response = client.post("/login", data = {
        'username' : 'test-user',
        'password' : 'test'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/admin/'

    invalid_response = client.post("/login", data = {
        'username' : 'invalid-test-user',
        'password' : 'invalid-password'
    }, follow_redirects=True)

    assert invalid_response.status_code == 200
    assert invalid_response.request.path == '/login'

    # Check that it redirects
    response = client.post("/login", data = {
        'username' : 'test-user',
        'password' : 'test'
    }, follow_redirects=False)
    assert response.status_code == 302

    # Check that it redirects the user back to /login if they don't fill in a username or password
    empty_form_response = client.post('/login', data = {
        'username' : 'test',
        'password' : ''
    }, follow_redirects=True)
    assert empty_form_response.status_code == 200
    assert empty_form_response.request.path == '/login'
    # Check that it redirects the user if they don't fill in username or password
    empty_form_response = client.post('/login', data = {
        'username' : 'test',
        'password' : ''
    }, follow_redirects=False)
    assert empty_form_response.status_code == 302
    assert empty_form_response.request.path == '/login'


    API.db.index.delete_user_by_id(test_user.id)
    

def test_logout(client):
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    # Check there was only one redirect response
    assert len(response.history) == 1


    # Check that it does redirect
    redirect_response = client.get('/logout', follow_redirects=False)
    assert redirect_response.status_code == 302

def test_check_access_forbidden(client):
    """Check that the user can't access the model views when they aren't signed in"""
    user_response = client.get('/admin/user', follow_redirects=True)
    assert user_response.status_code == 403
    vehicle_response = client.get('/admin/vehicle', follow_redirects=True)
    assert vehicle_response.status_code == 403


