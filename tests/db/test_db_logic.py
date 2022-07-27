from app import load_user, create_admin_user
from models import Vehicle, db
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

def test_get_vehicle_by_name():
    # Create vehicle to get
    vehicle = Vehicle('test_name', 'test_calendar_id', 'test_calendar_group_id')
    db.session.add(vehicle)
    db.session.commit()
    # get that vehicle by name and assert everything equals what it should
    queried_vehicle = API.db.index.get_vehicle_by_name(vehicle.name)
    assert queried_vehicle.name == 'test_name'
    assert queried_vehicle.calendarID == 'test_calendar_id'
    assert queried_vehicle.calendarGroupID == 'test_calendar_group_id'
    # Remove the vehicle from the database
    Vehicle.query.filter_by(id=queried_vehicle.id).delete()
    db.session.commit()

def test_get_all_vehicles():
    # Create vehicles to get
    vehicle0 = Vehicle(f'test_name0', f'test_calendar_id_0', f'test_calendar_group_id_0')
    vehicle1 = Vehicle(f'test_name1', f'test_calendar_id_1', f'test_calendar_group_id_1')
    db.session.add(vehicle0)
    db.session.add(vehicle1)
    db.session.commit()
    # Get all vehicles and check that the vehicles added are in the query
    queried_vehicles = API.db.index.get_all_vehicles()
    assert type(queried_vehicles) == list
    assert vehicle0 in queried_vehicles
    assert vehicle1 in queried_vehicles
    # Remove the vehicles
    Vehicle.query.filter_by(id=vehicle0.id).delete()
    Vehicle.query.filter_by(id=vehicle1.id).delete()
    db.session.commit()

def test_check_if_username_exists():
    user = API.db.index.create_user('test-user', 'test-password')
    user_exists = API.db.index.check_if_user_exists(user.username)
    non_existent_user = API.db.index.check_if_user_exists(';al;skjdfaeq')
    assert user_exists == True
    assert non_existent_user == False
    API.db.index.delete_user_by_id(user.id)
