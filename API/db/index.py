from models import Vehicle, User, db

def get_vehicle_names():
    vehicle_names = []
    for vehicle in Vehicle.query.all():
        vehicle_names.append(vehicle.name)
    return vehicle_names

def get_vehicle_by_name(vehicle_name):
    return Vehicle.query.filter(Vehicle.name == vehicle_name).first()
    
def get_all_vehicles():
    return Vehicle.query.all()

def get_all_users():
    return User.query.all()

def get_user_by_id(id):
    return User.query.get(id)

def get_user_by_username(username):
    return User.query.filter_by(username = username).first()

def delete_user_by_id(id):
    User.query.filter_by(id=id).delete()
    db.session.commit()

def create_user(username, password):
    user = User(username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user

def check_if_user_exists(username):
    user = User.query.filter_by(username = username).first()
    return user != None