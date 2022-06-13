from models import User

def getUser(username):
    user = User.query.filter(User.username == username).first()
    if not user: return 'ERROR'
    return user

