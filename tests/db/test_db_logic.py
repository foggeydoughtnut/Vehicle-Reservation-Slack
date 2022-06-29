from app import load_user, create_admin_user
from models import User, db


def test_user_loader():
    # Create User to get
    test_user = User('test-user')
    test_user.set_password('test')
    test_user.password_hash
    db.session.add(test_user)
    db.session.commit()

    # Get the User
    test = load_user(test_user.id)
    assert test.username == 'test-user'
    assert test.check_password('test')

    # Delete the User
    User.query.filter_by(id=test.id).delete()
    db.session.commit() 

def test_create_admin_user():
    # Delete admin user if it exists
    old_admin_user = User.query.filter_by(username = 'admin').first()
    if (old_admin_user is not None):
        User.query.filter_by(id=old_admin_user.id).delete()
        db.session.commit()
    create_admin_user()
    # Check that the admin user is in the database
    admin = User.query.filter_by(username = 'admin').first()
    assert admin.username == 'admin'
    assert admin.check_password('password')
