import API.User
import API.graphAPI

def test_get_user_by_access_token(requests_mock):
    test_access_token = 'test_token'
    requests_mock.get(
        f"{API.graphAPI.GRAPH_API_ENDPOINT}me",
        json = {'user' : {
            'displayName' : 'test',
            'userPrincipleName' : 'email@email.com'
        }},
        status_code=200,
    )
    user = API.User.getUserByAccessToken(test_access_token)
    assert user['user']['displayName'] == 'test'
    assert user['user']['userPrincipleName'] == 'email@email.com'
    assert type(user) == dict
    
def test_get_user(mocker):
    mocker.patch('API.graphAPI.generateAccessToken', return_value='test_access_token')
    mocker.patch('API.User.getUserByAccessToken', return_value={'displayName' : 'test_name', 'userPrincipalName' : 'email@email.com'})
    user = API.User.getUser()
    assert user['displayName'] == 'test_name'
    assert user['userPrincipalName'] == 'email@email.com'
    assert type(user) == dict

def test_get_users_name(mocker):
    mocker.patch('API.User.getUser', return_value={'displayName' : 'test_user_name'})
    name = API.User.getUsersName()
    assert name == 'test_user_name'

def test_get_users_email(mocker):
    mocker.patch('API.User.getUser', return_value={'userPrincipalName' : 'email@email.com'})
    email = API.User.getUsersEmail()
    assert email == "email@email.com"