from app import load_user, create_admin_user
import API.db.index


def test_user_loader():
    test_user = API.db.index.create_user('test-user', 'test')

    # Get the User
    test = load_user(test_user.id)
    assert test.username == 'test-user'
    assert test.check_password('test')

    API.db.index.delete_user_by_id(test.id)

def test_create_admin_user():
    old_admin_user = API.db.index.get_user_by_username('admin')
    if (old_admin_user is not None):
        # Delete admin user if it exists
        API.db.index.delete_user_by_id(old_admin_user.id)
    create_admin_user()
    # Check that the admin user is in the database
    admin = API.db.index.get_user_by_username('admin')
    assert admin.username == 'admin'
    assert admin.check_password('password')

def test_create_user():
    user = API.db.index.create_user('test-user', 'test-password')
    assert user.username == 'test-user'
    assert user.check_password('test-password')
    API.db.index.delete_user_by_id(user.id)

def test_delete_user_by_id():
    user = API.db.index.create_user('test-user', 'test-password')
    API.db.index.delete_user_by_id(user.id)
    assert API.db.index.get_user_by_id(user.id) is None   

def test_get_user_by_id():
    user = API.db.index.create_user('test-user', 'test-password')
    queried_user = API.db.index.get_user_by_id(user.id)
    assert queried_user.username == 'test-user'
    assert queried_user.id == user.id
    assert queried_user.check_password('test-password')
    API.db.index.delete_user_by_id(user.id)

def test_get_user_by_username():
    user = API.db.index.create_user('test-user', 'test-password')
    queried_user = API.db.index.get_user_by_username(user.username)
    assert queried_user.username == 'test-user'
    assert queried_user.id == user.id
    assert queried_user.check_password('test-password')
    API.db.index.delete_user_by_id(user.id)

