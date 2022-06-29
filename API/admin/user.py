from models import User

def get_user(username):
    user = User.query.filter(User.username == username).first()
    if not user: return 'ERROR'
    return user

