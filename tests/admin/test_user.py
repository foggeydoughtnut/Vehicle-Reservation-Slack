import API.admin.user
import app

def test_get_user():
    with app.app.app_context():
        user = API.admin.user.getUser('admin')
        assert user
        assert user.username == "admin"

        invalid_user = API.admin.user.getUser('test')
        assert invalid_user == 'ERROR'        