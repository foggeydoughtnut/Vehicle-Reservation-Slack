from app import create_data_dict, app as testApp, create_admin_user, load_user
from models import User, db
import pytest

@pytest.fixture()
def app():
    testApp.config.update({
        "TESTING": True,
    })
    yield testApp

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

def test_user_loader():
    # Create User to get
    testUser = User('test-user')
    testUser.set_password('test')
    testUser.password_hash
    db.session.add(testUser)
    db.session.commit()

    # Get the User
    test = load_user(testUser.id)
    assert test.username == 'test-user'
    assert test.check_password('test')

    # Delete the User
    User.query.filter_by(id=test.id).delete()
    db.session.commit() 

# def test_create_admin_user():
#     # Delete admin user if it exists
#     old_admin_user = session.query(User).filter(User.username == 'admin')
#     print(old_admin_user)
#     # User.query.filter(User.username == 'admin').delete()
#     # db.session.commit()
#     # Create the admin user
#     create_admin_user()
#     # Check that the admin user is in the database
#     admin = User.query.filter(User.username == 'admin')
#     assert admin.username == 'admin'
#     assert admin.check_password('test')

# def test_logout_redirect(client):
#     response = client.get("/logout")
#     print(response.status)
#     print(response.request.path)
#     # assert len(response.history) == 1
#     # assert response.request.path == "/login"

