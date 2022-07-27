from app import app as t_app

import API.db.index
import API.Calendar
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

def test_base_index_redirects(client):
    res = client.get("/", follow_redirects=False)
    assert res.status_code == 302
    assert res.request.path == '/'

    res_follow_redirect = client.get('/', follow_redirects=True)
    assert res_follow_redirect.status_code == 200
    assert res_follow_redirect.request.path == '/login'




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

def test_create_user_success(client, mocker):
    mocker.patch('app.MyUserView.is_accessible', return_value=True)
    create_test_user_success = client.post('/create/new/user', data = {
        'username' : 'r8ZdYvguLuhrdPyp',
        'password' : 'yio2lmiTyU2uHzbf',
        'confirm_password' : 'yio2lmiTyU2uHzbf'
    }, follow_redirects=True)
    assert create_test_user_success.status_code == 200
    assert create_test_user_success.request.path == '/admin/user/'
    API.db.index.delete_user_by_username('r8ZdYvguLuhrdPyp')

def test_create_user_not_matching_passwords(client, mocker):
    mocker.patch('app.MyUserView.is_accessible', return_value=True)
    create_test_user_not_matching_passwords = client.post('/create/new/user', data = {
        'username' : 'r8ZdYvguLuhrdPyp',
        'password' : 'yio2lmiTyU2uHzbf',
        'confirm_password' : 'yio'
    }, follow_redirects=False)
    assert create_test_user_not_matching_passwords.status_code == 302
    assert create_test_user_not_matching_passwords.request.path == '/create/new/user'
    API.db.index.delete_user_by_username('r8ZdYvguLuhrdPyp')

    create_test_user_not_matching_passwords_redirect = client.post('/create/new/user', data = {
        'username' : 'r8ZdYvguLuhrdPyp',
        'password' : 'yio2lmiTyU2uHzbf',
        'confirm_password' : 'yio'
    }, follow_redirects=True)
    assert create_test_user_not_matching_passwords_redirect.status_code == 200
    assert create_test_user_not_matching_passwords_redirect.request.path == '/admin/user/new'
    API.db.index.delete_user_by_username('r8ZdYvguLuhrdPyp')

def test_create_user_existing_username(client, mocker):
    user0 = API.db.index.create_user('r8ZdYvguLuhrdPyp', 'yio2lmiTyU2uHzbf')
    mocker.patch('app.MyUserView.is_accessible', return_value=True)
    create_test_user_existing_username_redirect = client.post('/create/new/user', data = {
        'username' : 'r8ZdYvguLuhrdPyp',
        'password' : 'yio2lmiTyU2uHzbf',
        'confirm_password' : 'yio2lmiTyU2uHzbf'
    }, follow_redirects=True)
    assert create_test_user_existing_username_redirect.status_code == 200
    assert create_test_user_existing_username_redirect.request.path == '/admin/user/new'
    API.db.index.delete_user_by_id(user0.id)

    user1 = API.db.index.create_user('r8ZdYvguLuhrdPyp', 'yio2lmiTyU2uHzbf')
    mocker.patch('app.MyUserView.is_accessible', return_value=True)
    create_test_user_existing_username = client.post('/create/new/user', data = {
        'username' : 'r8ZdYvguLuhrdPyp',
        'password' : 'yio2lmiTyU2uHzbf',
        'confirm_password' : 'yio2lmiTyU2uHzbf'
    }, follow_redirects=False)
    assert create_test_user_existing_username.status_code == 302
    assert create_test_user_existing_username.request.path == '/create/new/user'
    API.db.index.delete_user_by_id(user1.id)